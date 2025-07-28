#!/usr/bin/env python3
"""
Bulk Processor - Batch processing module for CodeMeta files

This module provides functionality for processing multiple CodeMeta files
and repositories in batch operations.

Author: Ronald Siebes (UCDS Group, VU Amsterdam)
ORCID: 0000-0001-8772-7904
"""

import json
import os
import glob
from typing import Dict, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from .codemeta_generator import CodeMetaGenerator, create_soda_science_organization
from .enhancer import CodeMetaEnhancer


class BulkProcessor:
    """
    Class for batch processing of CodeMeta files and repositories.
    
    Provides functionality for:
    - Processing multiple repositories
    - Enhancing multiple CodeMeta files
    - Applying organizational context to multiple files
    - Batch validation and reporting
    """
    
    def __init__(self, schema_version: str = "3.0", max_workers: int = 4):
        """
        Initialize the bulk processor.
        
        Args:
            schema_version: CodeMeta schema version to use
            max_workers: Maximum number of concurrent workers
        """
        self.schema_version = schema_version
        self.max_workers = max_workers
        self.generator = CodeMetaGenerator(schema_version)
        self.enhancer = CodeMetaEnhancer(schema_version)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def process_repository_list(self, repo_urls: List[str], output_dir: str, 
                              organization_info: Optional[Dict] = None) -> Dict[str, str]:
        """
        Process a list of repository URLs to generate CodeMeta files.
        
        Args:
            repo_urls: List of GitHub repository URLs
            output_dir: Directory to save generated CodeMeta files
            organization_info: Optional organizational context to add
            
        Returns:
            Dictionary mapping repository URLs to output file paths or error messages
        """
        os.makedirs(output_dir, exist_ok=True)
        results = {}
        
        self.logger.info(f"Processing {len(repo_urls)} repositories...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self._process_single_repository, url, output_dir, organization_info): url
                for url in repo_urls
            }
            
            # Collect results
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results[url] = result
                    self.logger.info(f"✅ Processed: {url}")
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    results[url] = error_msg
                    self.logger.error(f"❌ Failed: {url} - {error_msg}")
        
        return results
    
    def _process_single_repository(self, repo_url: str, output_dir: str, 
                                 organization_info: Optional[Dict]) -> str:
        """Process a single repository and return the output file path."""
        # Extract repository name for filename
        repo_name = repo_url.split('/')[-1]
        output_file = os.path.join(output_dir, f"codemeta_{repo_name}.json")
        
        # Generate CodeMeta
        codemeta = self.generator.generate_from_github(repo_url)
        
        # Add organizational context if provided
        if organization_info:
            self.generator.add_organizational_context(codemeta, organization_info)
        
        # Save the file
        self.generator.save_codemeta(codemeta, output_file)
        
        return output_file
    
    def enhance_directory(self, input_dir: str, output_dir: Optional[str] = None,
                         organization_info: Optional[Dict] = None) -> Dict[str, str]:
        """
        Enhance all CodeMeta files in a directory.
        
        Args:
            input_dir: Directory containing CodeMeta files
            output_dir: Output directory (uses input_dir if None)
            organization_info: Optional organizational context to add
            
        Returns:
            Dictionary mapping input files to output files or error messages
        """
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = input_dir
        
        # Find CodeMeta files
        codemeta_files = self._find_codemeta_files(input_dir)
        results = {}
        
        self.logger.info(f"Enhancing {len(codemeta_files)} CodeMeta files...")
        
        for input_file in codemeta_files:
            try:
                filename = os.path.basename(input_file)
                output_file = os.path.join(output_dir, filename)
                
                # Enhance the file
                enhanced = self.enhancer.enhance_file(input_file, output_file)
                
                # Add organizational context if provided
                if organization_info:
                    self.enhancer.add_organizational_context(enhanced, organization_info)
                    
                    # Save again with organizational context
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(enhanced, f, indent=2, ensure_ascii=False)
                
                results[input_file] = output_file
                self.logger.info(f"✅ Enhanced: {filename}")
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                results[input_file] = error_msg
                self.logger.error(f"❌ Failed: {input_file} - {error_msg}")
        
        return results
    
    def _find_codemeta_files(self, directory: str) -> List[str]:
        """Find all CodeMeta files in a directory."""
        patterns = [
            os.path.join(directory, "codemeta*.json"),
            os.path.join(directory, "codemeta.json"),
            os.path.join(directory, "*codemeta*.json")
        ]
        
        files = []
        for pattern in patterns:
            files.extend(glob.glob(pattern))
        
        # Remove duplicates and return
        return list(set(files))
    
    def update_software_requirements(self, directory: str, requirements_mapping: Dict[str, Dict]) -> Dict[str, str]:
        """
        Update software requirements across multiple CodeMeta files.
        
        Args:
            directory: Directory containing CodeMeta files
            requirements_mapping: Mapping of package names to requirement objects
            
        Returns:
            Dictionary mapping files to update status
        """
        codemeta_files = self._find_codemeta_files(directory)
        results = {}
        
        self.logger.info(f"Updating software requirements in {len(codemeta_files)} files...")
        
        for filepath in codemeta_files:
            try:
                # Load file
                with open(filepath, 'r', encoding='utf-8') as f:
                    codemeta = json.load(f)
                
                # Update software requirements
                if "softwareRequirements" in codemeta:
                    updated_requirements = []
                    
                    for req in codemeta["softwareRequirements"]:
                        if isinstance(req, str):
                            # Look up in mapping
                            package_name = req.split('/')[-1] if '/' in req else req
                            if package_name in requirements_mapping:
                                updated_requirements.append(requirements_mapping[package_name])
                            else:
                                # Create basic requirement object
                                updated_requirements.append({
                                    "@id": req,
                                    "@type": "SoftwareApplication",
                                    "identifier": package_name,
                                    "name": package_name
                                })
                        else:
                            updated_requirements.append(req)
                    
                    codemeta["softwareRequirements"] = updated_requirements
                
                # Save updated file
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(codemeta, f, indent=2, ensure_ascii=False)
                
                results[filepath] = "Updated successfully"
                self.logger.info(f"✅ Updated: {os.path.basename(filepath)}")
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                results[filepath] = error_msg
                self.logger.error(f"❌ Failed: {filepath} - {error_msg}")
        
        return results
    
    def add_reference_publications(self, directory: str, publications_mapping: Dict[str, Dict]) -> Dict[str, str]:
        """
        Add reference publications to multiple CodeMeta files.
        
        Args:
            directory: Directory containing CodeMeta files
            publications_mapping: Mapping of project names to publication objects
            
        Returns:
            Dictionary mapping files to update status
        """
        codemeta_files = self._find_codemeta_files(directory)
        results = {}
        
        self.logger.info(f"Adding reference publications to {len(codemeta_files)} files...")
        
        for filepath in codemeta_files:
            try:
                # Load file
                with open(filepath, 'r', encoding='utf-8') as f:
                    codemeta = json.load(f)
                
                # Extract project name from filename or CodeMeta name
                filename = os.path.basename(filepath)
                project_name = filename.replace('codemeta_', '').replace('.json', '')
                
                # Check if we have publications for this project
                if project_name in publications_mapping:
                    codemeta["referencePublication"] = publications_mapping[project_name]
                    
                    # Save updated file
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(codemeta, f, indent=2, ensure_ascii=False)
                    
                    results[filepath] = "Publication added"
                    self.logger.info(f"✅ Added publication: {project_name}")
                else:
                    results[filepath] = "No publication mapping found"
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                results[filepath] = error_msg
                self.logger.error(f"❌ Failed: {filepath} - {error_msg}")
        
        return results
    
    def validate_directory(self, directory: str) -> Dict[str, List[str]]:
        """
        Validate all CodeMeta files in a directory.
        
        Args:
            directory: Directory containing CodeMeta files
            
        Returns:
            Dictionary mapping files to validation messages
        """
        codemeta_files = self._find_codemeta_files(directory)
        results = {}
        
        self.logger.info(f"Validating {len(codemeta_files)} CodeMeta files...")
        
        for filepath in codemeta_files:
            try:
                # Load file
                with open(filepath, 'r', encoding='utf-8') as f:
                    codemeta = json.load(f)
                
                # Validate using both generator and enhancer
                generator_warnings = self.generator.validate_codemeta(codemeta)
                enhancer_messages = self.enhancer.validate_enhancement(codemeta)
                
                all_messages = generator_warnings + enhancer_messages
                results[filepath] = all_messages
                
                if not generator_warnings:
                    self.logger.info(f"✅ Valid: {os.path.basename(filepath)}")
                else:
                    self.logger.warning(f"⚠️  Issues: {os.path.basename(filepath)}")
                
            except Exception as e:
                error_msg = f"Validation error: {str(e)}"
                results[filepath] = [error_msg]
                self.logger.error(f"❌ Failed: {filepath} - {error_msg}")
        
        return results
    
    def generate_report(self, results: Dict[str, str], output_file: str) -> None:
        """
        Generate a processing report.
        
        Args:
            results: Results dictionary from processing operations
            output_file: Path to save the report
        """
        report = {
            "timestamp": str(datetime.now()),
            "total_files": len(results),
            "successful": len([r for r in results.values() if not r.startswith("Error")]),
            "failed": len([r for r in results.values() if r.startswith("Error")]),
            "details": results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Report saved to: {output_file}")


# Utility functions for common bulk operations
def process_soda_science_repositories(repo_urls: List[str], output_dir: str) -> Dict[str, str]:
    """
    Process SODA Science repositories with organizational context.
    
    Args:
        repo_urls: List of SODA Science repository URLs
        output_dir: Output directory for CodeMeta files
        
    Returns:
        Processing results
    """
    processor = BulkProcessor()
    soda_org = create_soda_science_organization()
    
    return processor.process_repository_list(repo_urls, output_dir, soda_org)


def enhance_soda_science_files(input_dir: str, output_dir: Optional[str] = None) -> Dict[str, str]:
    """
    Enhance SODA Science CodeMeta files with organizational context.
    
    Args:
        input_dir: Directory containing CodeMeta files
        output_dir: Output directory (uses input_dir if None)
        
    Returns:
        Enhancement results
    """
    processor = BulkProcessor()
    soda_org = create_soda_science_organization()
    
    return processor.enhance_directory(input_dir, output_dir, soda_org)


if __name__ == "__main__":
    # Example usage
    processor = BulkProcessor()
    
    # Example: Process multiple repositories
    # repo_urls = [
    #     "https://github.com/sodascience/metasyn",
    #     "https://github.com/sodascience/osmenrich"
    # ]
    # results = process_soda_science_repositories(repo_urls, "./output/")
    
    # Example: Enhance existing files
    # results = enhance_soda_science_files("./examples/soda_science/")
    
    print("Bulk processor ready for use!")

