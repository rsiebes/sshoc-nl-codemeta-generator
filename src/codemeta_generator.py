#!/usr/bin/env python3
"""
Main orchestrator for CodeMeta 3.1 metadata generation.
"""

import importlib
import json
import pkgutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add the project root to the Python path to allow absolute imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src import modules
from src.schema_validator import validate_metadata, print_validation_report
from src.utils import filter_empty_values

class CodeMetaGenerator:
    """Main orchestrator for CodeMeta metadata generation."""

    def __init__(self, verbose: bool = True):
        """
        Initialize the CodeMeta generator.

        Args:
            verbose (bool): Enable verbose output.
        """
        self.verbose = verbose
        self.discovered_modules = []
        self.module_results = {}
        self.errors = []

    def discover_modules(self) -> List:
        """
        Dynamically discover all modules in the src.modules package.

        Returns:
            List: A list of discovered modules.
        """
        discovered = []
        for _, name, _ in pkgutil.iter_modules(modules.__path__):
            if name.startswith("codemeta_"):
                try:
                    module = importlib.import_module(f"src.modules.{name}")
                    discovered.append(module)
                except ImportError as e:
                    error_msg = f"Error importing module {name}: {e}"
                    self.errors.append(error_msg)
                    if self.verbose:
                        print(f"✗ {error_msg}")
        return discovered

    def execute_modules(self, repository_url: str) -> Dict:
        """
        Execute all discovered modules and aggregate their results.

        Args:
            repository_url (str): The URL of the GitHub repository.

        Returns:
            Dict: The aggregated metadata from all modules.
        """
        aggregated_data = {}

        if not self.discovered_modules:
            if self.verbose:
                print("No CodeMeta modules found. Please create modules in the src/modules directory.")
            return aggregated_data

        if self.verbose:
            print(f"\nExecuting {len(self.discovered_modules)} modules...")

        for module in self.discovered_modules:
            if hasattr(module, "get") and callable(module.get):
                try:
                    result = module.get(repository_url)
                    if result and isinstance(result, dict):
                        aggregated_data.update(result)
                        self.module_results[module.__name__] = result
                        if self.verbose:
                            print(f"✓ {module.__name__}")
                    else:
                        if self.verbose:
                            print(f"⊘ {module.__name__} (no data)")
                except Exception as e:
                    error_msg = f"Error executing module {module.__name__}: {e}"
                    self.errors.append(error_msg)
                    if self.verbose:
                        print(f"✗ {error_msg}")
            else:
                error_msg = f"Module {module.__name__} does not have a callable 'get' function."
                self.errors.append(error_msg)
                if self.verbose:
                    print(f"✗ {error_msg}")

        return aggregated_data

    def build_codemeta(self, aggregated_data: Dict) -> Dict:
        """
        Build the final CodeMeta JSON-LD structure.

        Args:
            aggregated_data (Dict): The aggregated metadata from all modules.

        Returns:
            Dict: The final CodeMeta metadata structure.
        """
        codemeta_data = {
            "@context": "https://codemeta.github.io/terms/",
            "@type": "SoftwareSourceCode"
        }

        # Merge aggregated data
        codemeta_data.update(aggregated_data)

        # Filter out empty values
        codemeta_data = filter_empty_values(codemeta_data)

        return codemeta_data

    def validate(self, codemeta_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate the generated metadata against the CodeMeta 3.1 schema.

        Args:
            codemeta_data (Dict): The CodeMeta metadata to validate.

        Returns:
            Tuple[bool, List[str]]: A tuple of (is_valid, list_of_errors).
        """
        is_valid, errors = validate_metadata(codemeta_data)
        if not is_valid:
            self.errors.extend(errors)
        return is_valid, errors

    def write_output(self, codemeta_data: Dict, output_file: str) -> bool:
        """
        Write the CodeMeta metadata to a JSON-LD file.

        Args:
            codemeta_data (Dict): The CodeMeta metadata to write.
            output_file (str): The path to the output file.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            with open(output_file, "w") as f:
                json.dump(codemeta_data, f, indent=2)
            if self.verbose:
                print(f"\n✓ CodeMeta metadata successfully written to {output_file}")
            return True
        except Exception as e:
            error_msg = f"Error writing output file: {e}"
            self.errors.append(error_msg)
            if self.verbose:
                print(f"✗ {error_msg}")
            return False

    def generate(self, repository_url: str, output_file: str = "codemeta.jsonld") -> Dict:
        """
        Generate CodeMeta metadata for a GitHub repository.

        Args:
            repository_url (str): The URL of the GitHub repository.
            output_file (str): The path to the output codemeta.jsonld file.

        Returns:
            Dict: The generated CodeMeta metadata as a dictionary.
        """
        if self.verbose:
            print("=" * 80)
            print("CODEMETA GENERATION PROCESS")
            print("=" * 80)
            print(f"\nRepository: {repository_url}")

        # Step 1: Discover modules
        if self.verbose:
            print("\n[1/5] Discovering modules...")
        self.discovered_modules = self.discover_modules()
        if self.verbose:
            print(f"      Found {len(self.discovered_modules)} modules")

        # Step 2: Execute modules
        if self.verbose:
            print("\n[2/5] Executing modules...")
        aggregated_data = self.execute_modules(repository_url)

        # Step 3: Build CodeMeta structure
        if self.verbose:
            print("\n[3/5] Building CodeMeta structure...")
        codemeta_data = self.build_codemeta(aggregated_data)
        if self.verbose:
            print(f"      Generated {len(codemeta_data)} properties")

        # Step 4: Validate metadata
        if self.verbose:
            print("\n[4/5] Validating metadata...")
        is_valid, validation_errors = self.validate(codemeta_data)
        if self.verbose:
            if is_valid:
                print("      ✓ Metadata is valid")
            else:
                print(f"      ✗ Validation errors found: {len(validation_errors)}")

        # Step 5: Write output
        if self.verbose:
            print("\n[5/5] Writing output...")
        self.write_output(codemeta_data, output_file)

        # Print validation report
        if self.verbose:
            print_validation_report(codemeta_data)

        return codemeta_data

    def get_errors(self) -> List[str]:
        """
        Get all errors that occurred during generation.

        Returns:
            List[str]: A list of error messages.
        """
        return self.errors

    def get_module_results(self) -> Dict:
        """
        Get the results from each module.

        Returns:
            Dict: A dictionary mapping module names to their results.
        """
        return self.module_results


def generate(repository_url: str, output_file: str = "codemeta.jsonld", verbose: bool = True) -> Dict:
    """
    Generate CodeMeta metadata for a GitHub repository (convenience function).

    Args:
        repository_url (str): The URL of the GitHub repository.
        output_file (str): The path to the output codemeta.jsonld file.
        verbose (bool): Enable verbose output.

    Returns:
        Dict: The generated CodeMeta metadata as a dictionary.
    """
    generator = CodeMetaGenerator(verbose=verbose)
    return generator.generate(repository_url, output_file)


if __name__ == "__main__":
    # Example usage:
    repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
    generate(repo_url)
