"""Submodule for extracting identifier from repository metadata."""

from typing import Any, Dict, Optional

from src.submodules.base import BaseSubmodule


class IdentifierSubmodule(BaseSubmodule):
    """Extract identifier from repository data."""

    PROPERTY_NAME = "identifier"
    CATEGORY = "core_metadata"

    def extract(self) -> Optional[str]:
        """
        Extract the identifier from repository data.

        Returns:
            Repository identifier (URL-based) or None
        """
        try:
            # Use repository URL as identifier
            url = self.repo_data.get("url")
            if url:
                return url

            return None

        except Exception as e:
            self.error = str(e)
            return None
