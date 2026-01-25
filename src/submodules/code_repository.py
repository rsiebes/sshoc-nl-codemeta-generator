"""Submodule for extracting code repository URL from repository metadata."""

from typing import Any, Dict, Optional

from src.submodules.base import BaseSubmodule


class CodeRepositorySubmodule(BaseSubmodule):
    """Extract code repository URL from repository data."""

    PROPERTY_NAME = "codeRepository"
    CATEGORY = "core_metadata"

    def extract(self) -> Optional[str]:
        """
        Extract the code repository URL from repository data.

        Returns:
            Repository clone URL or None
        """
        try:
            # Get clone URL from GitHub API data
            clone_url = self.repo_data.get("data", {}).get("clone_url")

            if clone_url:
                return clone_url

            # Fallback to constructing from owner and repo
            owner = self.repo_data.get("owner")
            repo = self.repo_data.get("repo")
            if owner and repo:
                return f"https://github.com/{owner}/{repo}.git"

            return None

        except Exception as e:
            self.error = str(e)
            return None
