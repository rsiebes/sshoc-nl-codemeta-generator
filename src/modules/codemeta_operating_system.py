"""
CodeMeta Operating System Module

This module extracts supported operating systems with specific flavors and versions
from a GitHub repository. It detects OS support from README, CI/CD configuration,
and setup files.
"""

from typing import Dict, List, Optional, Set
from src.github_api import (
    parse_repository_url,
    fetch_file_content,
    fetch_repository_info
)
import re


# Comprehensive OS patterns with flavors and versions
OS_PATTERNS = {
    # Linux distributions with versions
    "Ubuntu": [
        r"ubuntu\s*(?:22\.04|20\.04|18\.04|16\.04|14\.04|12\.04|10\.04)?",
        r"ubuntu-latest",
        r"ubuntu:\s*\d+\.\d+",
    ],
    "Debian": [
        r"debian\s*(?:12|11|10|9|8)?",
        r"debian:\s*\d+",
    ],
    "CentOS": [
        r"centos\s*(?:8|7|6)?",
        r"centos:\s*\d+",
    ],
    "RHEL": [
        r"rhel\s*(?:9|8|7|6)?",
        r"red\s*hat",
    ],
    "Fedora": [
        r"fedora\s*(?:\d+)?",
    ],
    "Alpine": [
        r"alpine\s*(?:3\.\d+)?",
        r"alpine:\s*\d+\.\d+",
    ],
    "Arch": [
        r"arch\s*linux",
    ],
    "openSUSE": [
        r"opensuse",
        r"suse",
    ],
    "Linux": [
        r"linux",
        r"ubuntu",
        r"debian",
        r"fedora",
        r"centos",
        r"rhel",
        r"alpine",
    ],
    # macOS versions
    "macOS": [
        r"macos-(?:latest|13|12|11|10\.15)",
        r"macos\s*(?:13|12|11|10\.15|10\.14|10\.13)?",
        r"darwin",
        r"osx",
    ],
    # Windows versions
    "Windows": [
        r"windows-(?:latest|2022|2019|2016)",
        r"windows\s*(?:server\s*)?(?:2022|2019|2016|10)?",
        r"win32",
        r"msvc",
        r"visual\s*studio",
    ],
    # BSD variants
    "FreeBSD": [
        r"freebsd\s*(?:13|12|11)?",
    ],
    "OpenBSD": [
        r"openbsd\s*(?:7\.\d+)?",
    ],
    "NetBSD": [
        r"netbsd\s*(?:9|8)?",
    ],
    "BSD": [
        r"bsd",
        r"freebsd",
        r"openbsd",
        r"netbsd",
    ],
    # Mobile platforms
    "iOS": [
        r"ios\s*(?:\d+)?",
        r"iphone",
        r"ipad",
    ],
    "Android": [
        r"android\s*(?:\d+)?",
    ],
    # Other Unix-like systems
    "Unix": [
        r"unix",
        r"posix",
        r"solaris",
    ],
}


def extract_os_with_details(text: str) -> Set[str]:
    """
    Extract operating systems with specific flavors and versions from text.

    Args:
        text (str): Text to search for OS information.

    Returns:
        Set[str]: Set of detected operating systems with details.
    """
    detected_os = set()
    text_lower = text.lower()

    for os_name, patterns in OS_PATTERNS.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                detected_os.add(os_name)
                # Extract version if present
                matched_text = match.group(0)
                # Check for version numbers
                version_match = re.search(r'\d+\.?\d*', matched_text)
                if version_match:
                    version = version_match.group(0)
                    # Add OS with version if it's meaningful
                    if version and version not in ["2", "10", "12"]:  # Filter common false positives
                        os_with_version = f"{os_name} {version}"
                        detected_os.add(os_with_version)
                break

    return detected_os


def detect_os_from_readme(owner: str, repo: str) -> List[str]:
    """
    Detect supported operating systems from README.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected operating systems with details.
    """
    try:
        readme_content = fetch_file_content(owner, repo, "README.md")
        if not readme_content:
            return []

        detected_os = extract_os_with_details(readme_content)
        return sorted(list(detected_os))

    except Exception:
        return []


def detect_os_from_ci_config(owner: str, repo: str) -> List[str]:
    """
    Detect supported operating systems from CI/CD configuration.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected operating systems with details.
    """
    try:
        detected_os = set()

        # Check GitHub Actions workflow
        workflow_content = fetch_file_content(owner, repo, ".github/workflows/main.yml")
        if not workflow_content:
            workflow_content = fetch_file_content(owner, repo, ".github/workflows/ci.yml")

        if workflow_content:
            detected_os.update(extract_os_with_details(workflow_content))

        # Check Travis CI config
        travis_content = fetch_file_content(owner, repo, ".travis.yml")
        if travis_content:
            detected_os.update(extract_os_with_details(travis_content))

        # Check AppVeyor config
        appveyor_content = fetch_file_content(owner, repo, "appveyor.yml")
        if appveyor_content:
            detected_os.update(extract_os_with_details(appveyor_content))

        # Check Circle CI config
        circleci_content = fetch_file_content(owner, repo, ".circleci/config.yml")
        if circleci_content:
            detected_os.update(extract_os_with_details(circleci_content))

        return sorted(list(detected_os))

    except Exception:
        return []


def detect_os_from_setup_files(owner: str, repo: str) -> List[str]:
    """
    Detect supported operating systems from setup files.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected operating systems with details.
    """
    try:
        detected_os = set()

        # Check setup.py for classifiers
        setup_content = fetch_file_content(owner, repo, "setup.py")
        if setup_content:
            detected_os.update(extract_os_with_details(setup_content))

        # Check pyproject.toml for classifiers
        pyproject_content = fetch_file_content(owner, repo, "pyproject.toml")
        if pyproject_content:
            detected_os.update(extract_os_with_details(pyproject_content))

        # Check Dockerfile for OS base images
        dockerfile_content = fetch_file_content(owner, repo, "Dockerfile")
        if dockerfile_content:
            detected_os.update(extract_os_with_details(dockerfile_content))

        return sorted(list(detected_os))

    except Exception:
        return []


def get(repository_url: str) -> Dict:
    """
    Extract supported operating systems from a GitHub repository.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'operatingSystem' key if OS info is found, empty dict otherwise.
    """
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    # Detect OS from multiple sources
    os_list = set()

    # Try README detection
    readme_os = detect_os_from_readme(owner, repo)
    os_list.update(readme_os)

    # Try CI/CD config detection
    ci_os = detect_os_from_ci_config(owner, repo)
    os_list.update(ci_os)

    # Try setup files detection
    setup_os = detect_os_from_setup_files(owner, repo)
    os_list.update(setup_os)

    if not os_list:
        return {}

    return {
        "operatingSystem": sorted(list(os_list))
    }
