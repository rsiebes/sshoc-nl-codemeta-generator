"""Manager for orchestrating submodule execution."""

from typing import Any, Dict, List

from src.core import get_logger
from src.submodules import (
    NameSubmodule,
    DescriptionSubmodule,
    UrlSubmodule,
    CodeRepositorySubmodule,
    VersionSubmodule,
    IdentifierSubmodule,
    KeywordsSubmodule,
)

logger = get_logger(__name__)


class SubmoduleManager:
    """Manages the execution of all Codemeta submodules."""

    def __init__(self):
        """Initialize the submodule manager."""
        self.submodules = []
        self.results = {}
        self.execution_times = {}

    def register_submodule(self, submodule_class, repo_data: Dict[str, Any]) -> None:
        """
        Register a submodule for execution.

        Args:
            submodule_class: The submodule class to instantiate
            repo_data: Repository data to pass to the submodule
        """
        instance = submodule_class(repo_data)
        self.submodules.append(instance)

    def register_core_metadata_submodules(self, repo_data: Dict[str, Any]) -> None:
        """
        Register all core metadata submodules.

        Args:
            repo_data: Repository data to pass to submodules
        """
        self.register_submodule(NameSubmodule, repo_data)
        self.register_submodule(DescriptionSubmodule, repo_data)
        self.register_submodule(UrlSubmodule, repo_data)
        self.register_submodule(CodeRepositorySubmodule, repo_data)
        self.register_submodule(VersionSubmodule, repo_data)
        self.register_submodule(IdentifierSubmodule, repo_data)

    def register_ai_extraction_submodules(self, repo_data: Dict[str, Any]) -> None:
        """
        Register all AI extraction submodules (e.g., Gemini-based).

        Args:
            repo_data: Repository data to pass to submodules
        """
        self.register_submodule(KeywordsSubmodule, repo_data)

    def execute_all(self) -> Dict[str, Any]:
        """
        Execute all registered submodules.

        Returns:
            Dictionary with extracted Codemeta properties
        """
        logger.info(f"Executing {len(self.submodules)} submodules...")

        codemeta_data = {}

        for submodule in self.submodules:
            property_name = submodule.PROPERTY_NAME
            value = submodule.run()

            if value is not None:
                codemeta_data[property_name] = value
                self.results[property_name] = value
            else:
                self.results[property_name] = None

            self.execution_times[property_name] = submodule.extraction_time

        logger.info(f"Submodule execution completed. {len(codemeta_data)} properties extracted.")
        return codemeta_data

    def get_status(self) -> Dict[str, Any]:
        """
        Get status of all submodules.

        Returns:
            Dictionary with status information for each submodule
        """
        status = {
            "total_submodules": len(self.submodules),
            "total_extracted": sum(1 for v in self.results.values() if v is not None),
            "total_time": sum(self.execution_times.values()),
            "submodules": [submodule.get_status() for submodule in self.submodules],
        }
        return status

    def log_status(self) -> None:
        """Log the status of all submodules."""
        status = self.get_status()
        logger.info(f"Submodule Status:")
        logger.info(f"  Total submodules: {status['total_submodules']}")
        logger.info(f"  Properties extracted: {status['total_extracted']}")
        logger.info(f"  Total execution time: {status['total_time']:.3f}s")

        for submodule_status in status["submodules"]:
            if submodule_status["extracted"]:
                logger.debug(
                    f"  ✓ {submodule_status['property']}: "
                    f"{submodule_status['extraction_time']:.3f}s"
                )
            else:
                logger.debug(
                    f"  ✗ {submodule_status['property']}: "
                    f"{submodule_status['extraction_time']:.3f}s"
                )
