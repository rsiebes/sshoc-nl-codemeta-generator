"""Submodule for extracting software description from repository metadata."""

from typing import Any, Dict, Optional

from src.submodules.base import BaseSubmodule


class DescriptionSubmodule(BaseSubmodule):
    """Extract software description from repository data."""

    PROPERTY_NAME = "description"
    CATEGORY = "core_metadata"

    def extract(self) -> Optional[str]:
        """
        Extract the software description from repository data.

        Returns:
            Repository description or None
        """
        try:
            # Get description from GitHub API data
            description = self.repo_data.get("data", {}).get("description")

            if description:
                return description

            return None

        except Exception as e:
            self.error = str(e)
            return None
