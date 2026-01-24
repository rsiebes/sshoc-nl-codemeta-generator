"""Base class for all Codemeta submodules."""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from src.core import get_logger

logger = get_logger(__name__)


class BaseSubmodule(ABC):
    """Abstract base class for Codemeta property submodules."""

    # Subclass should override this
    PROPERTY_NAME: str = "unknown"
    CATEGORY: str = "unknown"

    def __init__(self, repo_data: Dict[str, Any]):
        """
        Initialize the submodule.

        Args:
            repo_data: Repository data from GitHub API
        """
        self.repo_data = repo_data
        self.extraction_time = 0.0
        self.value = None
        self.error = None

    @abstractmethod
    def extract(self) -> Optional[Any]:
        """
        Extract the property value from repository data.

        Returns:
            The extracted value or None if not found

        Raises:
            Should log errors but not raise exceptions
        """
        pass

    def validate(self) -> bool:
        """
        Validate the extracted value.

        Returns:
            True if value is valid, False otherwise
        """
        return self.value is not None

    def get_data(self) -> Optional[Any]:
        """
        Get the extracted and validated data.

        Returns:
            The extracted value or None
        """
        return self.value if self.validate() else None

    def run(self) -> Optional[Any]:
        """
        Run the extraction process with timing and error handling.

        Returns:
            The extracted value or None
        """
        start_time = time.time()

        try:
            logger.debug(f"[{self.CATEGORY}] Extracting {self.PROPERTY_NAME}...")

            self.value = self.extract()

            self.extraction_time = time.time() - start_time

            if self.value is not None:
                logger.info(
                    f"[{self.CATEGORY}] {self.PROPERTY_NAME} extracted successfully "
                    f"({self.extraction_time:.3f}s)"
                )
            else:
                logger.debug(
                    f"[{self.CATEGORY}] {self.PROPERTY_NAME} not found "
                    f"({self.extraction_time:.3f}s)"
                )

            return self.get_data()

        except Exception as e:
            self.extraction_time = time.time() - start_time
            self.error = str(e)
            logger.warning(
                f"[{self.CATEGORY}] Error extracting {self.PROPERTY_NAME}: {self.error} "
                f"({self.extraction_time:.3f}s)"
            )
            return None

    def get_status(self) -> Dict[str, Any]:
        """
        Get extraction status information.

        Returns:
            Dictionary with status information
        """
        return {
            "property": self.PROPERTY_NAME,
            "category": self.CATEGORY,
            "extracted": self.value is not None,
            "value": self.value,
            "extraction_time": self.extraction_time,
            "error": self.error,
        }
