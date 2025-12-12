"""
CodeMeta Code Repository Module

This module extracts the code repository information from a GitHub repository.
It provides the repository URL and type information in CodeMeta format.
"""

from typing import Dict, Optional
from src.github_api import (
    parse_repository_url,
    fetch_repository_info,
    get_github_token
)


def get(repository_url: str) -> Dict:
    """
    Extract code repository information from a GitHub repository.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'codeRepository' key containing repository information,
              empty dict if repository information cannot be extracted.
    """
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    try:
        # Fetch repository information
        repo_info = fetch_repository_info(owner, repo)
        if not repo_info:
            return {}

        # Build the code repository object
        code_repository = {
            "@type": "Repository",
            "url": repository_url
        }

        # Add repository type if available
        # GitHub repositories are typically git repositories
        if repo_info.get("language"):
            # Add language information to help identify repository type
            code_repository["language"] = repo_info.get("language")

        # Add clone URL (HTTPS)
        if repo_info.get("clone_url"):
            code_repository["clone_url"] = repo_info.get("clone_url")

        # Add SSH URL if available
        if repo_info.get("ssh_url"):
            code_repository["ssh_url"] = repo_info.get("ssh_url")

        # Add repository size information
        if repo_info.get("size"):
            code_repository["size"] = repo_info.get("size")

        # Add repository visibility
        if "private" in repo_info:
            code_repository["private"] = repo_info.get("private")

        # Add fork information
        if "fork" in repo_info:
            code_repository["fork"] = repo_info.get("fork")

        # Add default branch
        if repo_info.get("default_branch"):
            code_repository["default_branch"] = repo_info.get("default_branch")

        return {
            "codeRepository": code_repository
        }

    except Exception:
        return {}
