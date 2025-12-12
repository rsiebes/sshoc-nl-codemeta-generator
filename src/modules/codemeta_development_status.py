"""
CodeMeta Development Status Module

This module extracts the development status of a GitHub repository.
It analyzes repository metadata, commit history, and documentation to determine
if the project is in 'active', 'inactive', 'concept', or 'archived' status.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from src.github_api import (
    parse_repository_url,
    fetch_repository_info,
    fetch_file_content,
    get_github_token
)


# Development status constants
STATUS_ACTIVE = "Active"
STATUS_INACTIVE = "Inactive"
STATUS_CONCEPT = "Concept"
STATUS_ARCHIVED = "Archived"
STATUS_SUSPENDED = "Suspended"

# Time thresholds (in days)
ACTIVE_THRESHOLD = 180  # 6 months
INACTIVE_THRESHOLD = 365  # 1 year


def get_repository_status(owner: str, repo: str) -> Optional[str]:
    """
    Determine repository development status from GitHub API metadata.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: Development status or None if not determinable.
    """
    try:
        repo_info = fetch_repository_info(owner, repo)
        if not repo_info:
            return None

        # Check if repository is archived
        if repo_info.get("archived"):
            return STATUS_ARCHIVED

        # Check last push date
        if "pushed_at" in repo_info:
            last_push = repo_info["pushed_at"]
            if last_push:
                # Parse ISO 8601 datetime
                last_push_date = datetime.fromisoformat(last_push.replace("Z", "+00:00"))
                days_since_push = (datetime.now(last_push_date.tzinfo) - last_push_date).days

                if days_since_push < ACTIVE_THRESHOLD:
                    return STATUS_ACTIVE
                elif days_since_push < INACTIVE_THRESHOLD:
                    return STATUS_INACTIVE
                else:
                    return STATUS_INACTIVE

        return None

    except Exception:
        return None


def check_readme_status(owner: str, repo: str) -> Optional[str]:
    """
    Check README for development status indicators.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: Development status or None if not found.
    """
    try:
        readme_content = fetch_file_content(owner, repo, "README.md")
        if not readme_content:
            return None

        readme_lower = readme_content.lower()

        # Check for status indicators
        status_indicators = {
            STATUS_ARCHIVED: ["archived", "no longer maintained", "deprecated"],
            STATUS_SUSPENDED: ["suspended", "on hold", "paused"],
            STATUS_CONCEPT: ["proof of concept", "poc", "experimental", "alpha"],
            STATUS_ACTIVE: ["actively maintained", "actively developed", "under active development"],
        }

        for status, keywords in status_indicators.items():
            for keyword in keywords:
                if keyword in readme_lower:
                    return status

        return None

    except Exception:
        return None


def check_setup_py_status(owner: str, repo: str) -> Optional[str]:
    """
    Check setup.py for development status classifier.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: Development status or None if not found.
    """
    try:
        setup_content = fetch_file_content(owner, repo, "setup.py")
        if not setup_content:
            return None

        setup_lower = setup_content.lower()

        # Check for PyPI classifiers
        classifiers = {
            STATUS_ACTIVE: [
                "development status :: 5 - production/stable",
                "development status :: 4 - beta",
            ],
            STATUS_CONCEPT: [
                "development status :: 3 - alpha",
                "development status :: 2 - pre-alpha",
            ],
            STATUS_INACTIVE: [
                "development status :: 7 - inactive",
            ],
        }

        for status, keywords in classifiers.items():
            for keyword in keywords:
                if keyword in setup_lower:
                    return status

        return None

    except Exception:
        return None


def check_pyproject_toml_status(owner: str, repo: str) -> Optional[str]:
    """
    Check pyproject.toml for development status classifier.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: Development status or None if not found.
    """
    try:
        pyproject_content = fetch_file_content(owner, repo, "pyproject.toml")
        if not pyproject_content:
            return None

        pyproject_lower = pyproject_content.lower()

        # Check for classifiers in pyproject.toml
        classifiers = {
            STATUS_ACTIVE: [
                "development status :: 5 - production/stable",
                "development status :: 4 - beta",
            ],
            STATUS_CONCEPT: [
                "development status :: 3 - alpha",
                "development status :: 2 - pre-alpha",
            ],
            STATUS_INACTIVE: [
                "development status :: 7 - inactive",
            ],
        }

        for status, keywords in classifiers.items():
            for keyword in keywords:
                if keyword in pyproject_lower:
                    return status

        return None

    except Exception:
        return None


def check_package_json_status(owner: str, repo: str) -> Optional[str]:
    """
    Check package.json for development status indicators.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: Development status or None if not found.
    """
    try:
        package_content = fetch_file_content(owner, repo, "package.json")
        if not package_content:
            return None

        import json
        package_data = json.loads(package_content)

        # Check for deprecated flag
        if package_data.get("deprecated"):
            return STATUS_ARCHIVED

        # Check for status in description
        description = package_data.get("description", "").lower()
        if "archived" in description or "deprecated" in description:
            return STATUS_ARCHIVED

        return None

    except Exception:
        return None


def get(repository_url: str) -> Dict:
    """
    Extract development status from a GitHub repository.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'developmentStatus' key if status is found, empty dict otherwise.
    """
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    # Try multiple strategies in priority order
    strategies = [
        lambda: check_readme_status(owner, repo),
        lambda: check_setup_py_status(owner, repo),
        lambda: check_pyproject_toml_status(owner, repo),
        lambda: check_package_json_status(owner, repo),
        lambda: get_repository_status(owner, repo),
    ]

    status = None
    for strategy in strategies:
        try:
            status = strategy()
            if status:
                break
        except Exception:
            continue

    if not status:
        return {}

    return {
        "developmentStatus": status
    }
