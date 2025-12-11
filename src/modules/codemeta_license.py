#!/usr/bin/env python3
"""
CodeMeta property module for extracting license information.

This module extracts license information from a GitHub repository using
multiple strategies:
1. From GitHub API repository metadata
2. From LICENSE file in the repository
3. From setup.py license field
4. From pyproject.toml license field
5. From package.json license field

The module maps license names to SPDX identifiers for standardization.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, List
import re
import json
import requests

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.github_api import parse_repository_url, fetch_repository_info, fetch_file_content
from src.utils import normalize_url


# SPDX License Identifier Mapping
# Maps common license names to SPDX identifiers
SPDX_LICENSE_MAP = {
    "MIT": "MIT",
    "Apache 2.0": "Apache-2.0",
    "Apache License 2.0": "Apache-2.0",
    "GPL": "GPL-3.0-only",
    "GPLv3": "GPL-3.0-only",
    "GPL-3.0": "GPL-3.0-only",
    "GPL-3.0-only": "GPL-3.0-only",
    "GPL-3.0-or-later": "GPL-3.0-or-later",
    "GPLv2": "GPL-2.0-only",
    "GPL-2.0": "GPL-2.0-only",
    "GPL-2.0-only": "GPL-2.0-only",
    "GPL-2.0-or-later": "GPL-2.0-or-later",
    "LGPL": "LGPL-3.0-only",
    "LGPLv3": "LGPL-3.0-only",
    "LGPL-3.0": "LGPL-3.0-only",
    "LGPL-3.0-only": "LGPL-3.0-only",
    "LGPL-3.0-or-later": "LGPL-3.0-or-later",
    "LGPLv2": "LGPL-2.0-only",
    "LGPL-2.0": "LGPL-2.0-only",
    "LGPL-2.0-only": "LGPL-2.0-only",
    "LGPL-2.0-or-later": "LGPL-2.0-or-later",
    "BSD": "BSD-3-Clause",
    "BSD-3-Clause": "BSD-3-Clause",
    "BSD-2-Clause": "BSD-2-Clause",
    "BSD-3-Clause-Clear": "BSD-3-Clause-Clear",
    "ISC": "ISC",
    "MPL": "MPL-2.0",
    "MPL-2.0": "MPL-2.0",
    "AGPL": "AGPL-3.0-only",
    "AGPLv3": "AGPL-3.0-only",
    "AGPL-3.0": "AGPL-3.0-only",
    "AGPL-3.0-only": "AGPL-3.0-only",
    "AGPL-3.0-or-later": "AGPL-3.0-or-later",
    "Unlicense": "Unlicense",
    "CC0-1.0": "CC0-1.0",
    "CC0": "CC0-1.0",
    "Proprietary": "Proprietary",
    "WTFPL": "WTFPL",
    "Zlib": "Zlib",
    "EPL": "EPL-1.0",
    "EPL-1.0": "EPL-1.0",
    "EPL-2.0": "EPL-2.0",
}

# SPDX License URL Base
SPDX_LICENSE_URL_BASE = "https://spdx.org/licenses"


def get_spdx_identifier(license_name: str) -> Optional[str]:
    """
    Get SPDX identifier for a license name.

    Args:
        license_name (str): The license name to look up.

    Returns:
        Optional[str]: The SPDX identifier or None if not found.
    """
    if not license_name:
        return None

    # Try exact match first
    if license_name in SPDX_LICENSE_MAP:
        return SPDX_LICENSE_MAP[license_name]

    # Try case-insensitive match
    for key, value in SPDX_LICENSE_MAP.items():
        if key.lower() == license_name.lower():
            return value

    # Try partial match
    license_lower = license_name.lower()
    for key, value in SPDX_LICENSE_MAP.items():
        if key.lower() in license_lower or license_lower in key.lower():
            return value

    return None


def get_spdx_url(spdx_identifier: str) -> str:
    """
    Get the SPDX URL for a license identifier.

    Args:
        spdx_identifier (str): The SPDX identifier.

    Returns:
        str: The SPDX URL.
    """
    return f"{SPDX_LICENSE_URL_BASE}/{spdx_identifier}"


def extract_license_from_github_api(owner: str, repo: str) -> Optional[Dict]:
    """
    Extract license information from GitHub API.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[Dict]: A dictionary with license information or None if not found.
    """
    try:
        repo_info = fetch_repository_info(owner, repo)
        if not repo_info:
            return None

        license_info = repo_info.get("license")
        if not license_info:
            return None

        license_name = license_info.get("name")
        spdx_id = license_info.get("spdx_id")

        if license_name or spdx_id:
            license_dict = {"@type": "CreativeWork"}

            if license_name:
                license_dict["name"] = license_name

            # Use SPDX ID from GitHub API if available
            if spdx_id and spdx_id != "NOASSERTION":
                license_dict["@id"] = get_spdx_url(spdx_id)
            elif license_name:
                # Try to find SPDX ID from name
                spdx_id = get_spdx_identifier(license_name)
                if spdx_id:
                    license_dict["@id"] = get_spdx_url(spdx_id)

            return license_dict

    except Exception:
        pass

    return None


def extract_license_from_license_file(owner: str, repo: str) -> Optional[Dict]:
    """
    Extract license information from LICENSE file in the repository.

    Attempts to detect the license type from the LICENSE file content.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[Dict]: A dictionary with license information or None if not found.
    """
    try:
        # Try common LICENSE file names
        license_files = [
            "LICENSE",
            "LICENSE.md",
            "LICENSE.txt",
            "LICENSE.rst",
            "COPYING",
            "COPYING.md",
        ]

        for license_file in license_files:
            content = fetch_file_content(owner, repo, license_file)
            if content:
                # Detect license type from content
                license_name = detect_license_from_content(content)
                if license_name:
                    license_dict = {"@type": "CreativeWork", "name": license_name}

                    spdx_id = get_spdx_identifier(license_name)
                    if spdx_id:
                        license_dict["@id"] = get_spdx_url(spdx_id)

                    return license_dict

    except Exception:
        pass

    return None


def detect_license_from_content(content: str) -> Optional[str]:
    """
    Detect license type from file content.

    Args:
        content (str): The content of the LICENSE file.

    Returns:
        Optional[str]: The detected license name or None.
    """
    if not content:
        return None

    content_lower = content.lower()

    # Check for common license signatures
    if "gnu general public license" in content_lower:
        if "version 3" in content_lower or "v3" in content_lower:
            return "GPL-3.0-only"
        elif "version 2" in content_lower or "v2" in content_lower:
            return "GPL-2.0-only"
        return "GPL-3.0-only"

    if "gnu lesser general public license" in content_lower:
        if "version 3" in content_lower or "v3" in content_lower:
            return "LGPL-3.0-only"
        elif "version 2" in content_lower or "v2" in content_lower:
            return "LGPL-2.0-only"
        return "LGPL-3.0-only"

    if "gnu affero general public license" in content_lower:
        if "version 3" in content_lower or "v3" in content_lower:
            return "AGPL-3.0-only"
        return "AGPL-3.0-only"

    if "apache license" in content_lower:
        if "version 2" in content_lower or "2.0" in content_lower:
            return "Apache-2.0"
        return "Apache-2.0"

    if "mit license" in content_lower or "permission is hereby granted" in content_lower:
        return "MIT"

    if "bsd" in content_lower:
        if "3-clause" in content_lower:
            return "BSD-3-Clause"
        elif "2-clause" in content_lower:
            return "BSD-2-Clause"
        return "BSD-3-Clause"

    if "mozilla public license" in content_lower:
        if "2.0" in content_lower:
            return "MPL-2.0"
        return "MPL-2.0"

    if "isc license" in content_lower:
        return "ISC"

    if "creative commons" in content_lower:
        if "cc0" in content_lower or "public domain" in content_lower:
            return "CC0-1.0"

    return None


def extract_license_from_setup_py(owner: str, repo: str) -> Optional[Dict]:
    """
    Extract license information from setup.py.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[Dict]: A dictionary with license information or None if not found.
    """
    content = fetch_file_content(owner, repo, "setup.py")
    if not content:
        return None

    # Try to extract license field
    match = re.search(r'license\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        license_name = match.group(1).strip()
        if license_name:
            license_dict = {"@type": "CreativeWork", "name": license_name}

            spdx_id = get_spdx_identifier(license_name)
            if spdx_id:
                license_dict["@id"] = get_spdx_url(spdx_id)

            return license_dict

    return None


def extract_license_from_pyproject_toml(owner: str, repo: str) -> Optional[Dict]:
    """
    Extract license information from pyproject.toml.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[Dict]: A dictionary with license information or None if not found.
    """
    content = fetch_file_content(owner, repo, "pyproject.toml")
    if not content:
        return None

    # Try to extract license from [project] section
    match = re.search(r'\[project\].*?license\s*=\s*["\']([^"\']+)["\']', content, re.DOTALL)
    if match:
        license_name = match.group(1).strip()
        if license_name:
            license_dict = {"@type": "CreativeWork", "name": license_name}

            spdx_id = get_spdx_identifier(license_name)
            if spdx_id:
                license_dict["@id"] = get_spdx_url(spdx_id)

            return license_dict

    return None


def extract_license_from_package_json(owner: str, repo: str) -> Optional[Dict]:
    """
    Extract license information from package.json.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[Dict]: A dictionary with license information or None if not found.
    """
    content = fetch_file_content(owner, repo, "package.json")
    if not content:
        return None

    try:
        package_data = json.loads(content)
        license_name = package_data.get("license")

        if license_name:
            license_dict = {"@type": "CreativeWork", "name": license_name}

            spdx_id = get_spdx_identifier(license_name)
            if spdx_id:
                license_dict["@id"] = get_spdx_url(spdx_id)

            return license_dict

    except (json.JSONDecodeError, ValueError):
        pass

    return None


def get(repository_url: str) -> Dict:
    """
    Extract license information from a GitHub repository.

    This function uses multiple strategies to extract license information:
    1. From GitHub API repository metadata
    2. From LICENSE file in the repository
    3. From setup.py license field
    4. From pyproject.toml license field
    5. From package.json license field

    Each license is represented as a CreativeWork object with:
    - name: The license name
    - @id: The SPDX URL (if available)
    - @type: Always "CreativeWork"

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'license' property and its value.
              Returns an empty dict if no license can be extracted.

    Example:
        >>> result = get("https://github.com/rsiebes/sshoc-nl-codemeta-generator")
        >>> print(result)
        {'license': {'@type': 'CreativeWork', 'name': 'MIT', '@id': 'https://spdx.org/licenses/MIT'}}
    """
    repository_url = normalize_url(repository_url)
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    license_info = None

    # Strategy 1: Try GitHub API (most reliable)
    license_info = extract_license_from_github_api(owner, repo)
    if license_info:
        return {"license": license_info}

    # Strategy 2: Try LICENSE file
    license_info = extract_license_from_license_file(owner, repo)
    if license_info:
        return {"license": license_info}

    # Strategy 3: Try setup.py
    license_info = extract_license_from_setup_py(owner, repo)
    if license_info:
        return {"license": license_info}

    # Strategy 4: Try pyproject.toml
    license_info = extract_license_from_pyproject_toml(owner, repo)
    if license_info:
        return {"license": license_info}

    # Strategy 5: Try package.json
    license_info = extract_license_from_package_json(owner, repo)
    if license_info:
        return {"license": license_info}

    return {}


if __name__ == "__main__":
    test_repos = [
        "https://github.com/rsiebes/sshoc-nl-codemeta-generator",
        "https://github.com/sodascience/osmenrich",
    ]

    for repo_url in test_repos:
        result = get(repo_url)
        if result:
            print(f"Repository: {repo_url}")
            print(f"License: {json.dumps(result, indent=2)}")
            print()
        else:
            print(f"Failed to extract license from {repo_url}")
