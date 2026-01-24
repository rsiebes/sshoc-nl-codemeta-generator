"""Main orchestrator for Codemeta generation."""

import json
from pathlib import Path
from typing import Dict, Any

from .core import (
    Cache,
    Config,
    GitHubAPI,
    CodemetaGenerationError,
    OutputError,
    get_logger,
)
from .submodules.manager import SubmoduleManager

logger = get_logger(__name__)


class CodemetaGenerator:
    """Main class for generating Codemeta metadata."""

    def __init__(self, config: Config):
        """
        Initialize the Codemeta generator.

        Args:
            config: Configuration object
        """
        self.config = config
        self.github_api = GitHubAPI(wait_on_rate_limit=config.wait_on_rate_limit)
        self.cache = Cache(use_cache=config.use_cache, ttl=config.cache_ttl)
        self.repo_info = None

    def generate(self) -> Dict[str, Any]:
        """
        Generate Codemeta metadata.

        Returns:
            Dictionary containing Codemeta metadata

        Raises:
            CodemetaGenerationError: If generation fails
        """
        logger.info("Starting Codemeta generation")

        try:
            # Parse repository URL to get owner and repo
            owner, repo = self.github_api.parse_repo_url(self.config.repo_url)

            # Try to get cached data
            cached_data = self.cache.get(owner, repo)
            if cached_data:
                logger.info(f"Using cached data for {owner}/{repo}")
                self.repo_info = cached_data
            else:
                # Fetch repository information from GitHub API
                logger.debug(f"Fetching repository information from {self.config.repo_url}")
                repo_info = self.github_api.get_repository_info(self.config.repo_url)
                self.repo_info = repo_info

                # Cache the data
                self.cache.set(owner, repo, repo_info)

            # Generate minimal Codemeta structure
            codemeta = self._create_codemeta_structure()

            logger.info("Codemeta generation completed successfully")
            return codemeta

        except Exception as e:
            logger.error(f"Error during Codemeta generation: {str(e)}")
            raise CodemetaGenerationError(f"Failed to generate Codemeta: {str(e)}")

    def _create_codemeta_structure(self) -> Dict[str, Any]:
        """
        Create the Codemeta JSON-LD structure using submodules.

        Returns:
            Dictionary with Codemeta structure
        """
        # Initialize submodule manager
        manager = SubmoduleManager()
        manager.register_core_metadata_submodules(self.repo_info)

        # Execute all submodules
        extracted_data = manager.execute_all()

        # Log submodule status
        manager.log_status()

        # Create Codemeta structure with extracted data
        codemeta = {
            "@context": "https://w3id.org/codemeta/3.1",
            "@type": "SoftwareSourceCode",
        }

        # Add extracted properties
        codemeta.update(extracted_data)

        logger.debug(f"Created Codemeta structure: {json.dumps(codemeta, indent=2)}")
        return codemeta

    def save_to_file(self, codemeta: Dict[str, Any]) -> None:
        """
        Save Codemeta metadata to a JSON-LD file.

        Args:
            codemeta: Codemeta metadata dictionary

        Raises:
            OutputError: If file writing fails
        """
        try:
            output_path = self.config.output_path
            logger.info(f"Writing Codemeta to {output_path}")

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(codemeta, f, indent=2, ensure_ascii=False)

            logger.info(f"Successfully saved Codemeta to {output_path}")

        except IOError as e:
            logger.error(f"Error writing to file {output_path}: {str(e)}")
            raise OutputError(f"Failed to write Codemeta file: {str(e)}")
