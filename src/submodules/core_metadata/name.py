"""Submodule for extracting software name from repository metadata."""

from typing import Any, Dict, Optional

from src.submodules.base import BaseSubmodule


class NameSubmodule(BaseSubmodule):
    """Extract software name from repository data."""

    PROPERTY_NAME = "name"
    CATEGORY = "core_metadata"

    def extract(self) -> Optional[str]:
        """
        Extract the software name from repository data.

        Returns:
            Repository name or None
        """
        try:
            # Get name from GitHub API data
            name = self.repo_data.get("data", {}).get("name")

            if name:
                return name

            return None

        except Exception as e:
            self.error = str(e)
            return None
