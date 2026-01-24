"""Submodule for extracting project URL from repository metadata."""

from typing import Any, Dict, Optional

from src.submodules.base import BaseSubmodule


class UrlSubmodule(BaseSubmodule):
    """Extract project URL from repository data."""

    PROPERTY_NAME = "url"
    CATEGORY = "core_metadata"

    def extract(self) -> Optional[str]:
        """
        Extract the project URL from repository data.

        Returns:
            Repository HTML URL or None
        """
        try:
            # Get HTML URL from GitHub API data
            url = self.repo_data.get("data", {}).get("html_url")

            if url:
                return url

            # Fallback to url field if present
            url = self.repo_data.get("url")
            if url:
                return url

            return None

        except Exception as e:
            self.error = str(e)
            return None
