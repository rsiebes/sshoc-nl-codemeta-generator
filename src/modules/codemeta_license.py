#!/usr/bin/env python3
"""
CodeMeta property module for extracting license information.

This module extracts license information from a GitHub repository using
multiple strategies:
1. From LICENSE file content in the repository (most reliable)
2. From GitHub API repository metadata
3. From setup.py license field
4. From pyproject.toml license field
5. From package.json license field

The module maps license names to SPDX identifiers for standardization and
analyzes LICENSE file content for custom or modified licenses.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import re
import json
import requests

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.github_api import parse_repository_url, fetch_repository_info, fetch_file_content, get_github_token
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

    # Try partial match (for cases like "Apache License 2.0" matching "Apache 2.0")
    license_lower = license_name.lower()
    for key, value in SPDX_LICENSE_MAP.items():
        if key.lower() in license_lower or license_lower in key.lower():
            return value

    return None


def detect_license_from_content(content: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Detect license type and name from LICENSE file content.

    This function analyzes the LICENSE file content to identify the license type
    and any modifications or custom terms.

    Args:
        content (str): The content of the LICENSE file.

    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple of (license_name, description)
    """
    if not content:
        return None, None

    content_lower = content.lower()
    lines = content.split('\n')
    first_line = lines[0].lower() if lines else ""

    # Check for common license patterns in the first few lines
    # Modified MIT License
    if "modified mit" in first_line or "modified mit" in content_lower[:200]:
        return "Modified MIT License", "MIT (modified)"
    
    # Standard MIT License
    if "mit license" in first_line or ("permission is hereby granted" in content_lower and "mit" in first_line):
        return "MIT License", "MIT"

    # Apache License
    if "apache license" in first_line or "apache license" in content_lower[:200]:
        if "2.0" in content_lower[:200]:
            return "Apache License 2.0", "Apache-2.0"
        else:
            return "Apache License", "Apache-2.0"

    # GPL Licenses
    if "gnu general public license" in content_lower[:200]:
        if "version 3" in content_lower or "v3" in content_lower or "gpl-3" in content_lower:
            return "GNU General Public License v3", "GPL-3.0-only"
        elif "version 2" in content_lower or "v2" in content_lower or "gpl-2" in content_lower:
            return "GNU General Public License v2", "GPL-2.0-only"
        else:
            return "GNU General Public License", "GPL-3.0-only"

    # BSD License
    if "bsd license" in first_line or "bsd license" in content_lower[:200]:
        if "3-clause" in content_lower or "three clause" in content_lower:
            return "BSD 3-Clause License", "BSD-3-Clause"
        elif "2-clause" in content_lower or "two clause" in content_lower:
            return "BSD 2-Clause License", "BSD-2-Clause"
        else:
            return "BSD License", "BSD-3-Clause"

    # LGPL License
    if "gnu lesser general public license" in content_lower[:200] or "lgpl" in first_line:
        if "version 3" in content_lower or "v3" in content_lower:
            return "GNU Lesser General Public License v3", "LGPL-3.0-only"
        elif "version 2" in content_lower or "v2" in content_lower:
            return "GNU Lesser General Public License v2", "LGPL-2.0-only"
        else:
            return "GNU Lesser General Public License", "LGPL-3.0-only"

    # AGPL License
    if "gnu affero general public license" in content_lower[:200] or "agpl" in first_line:
        if "version 3" in content_lower or "v3" in content_lower:
            return "GNU Affero General Public License v3", "AGPL-3.0-only"
        else:
            return "GNU Affero General Public License", "AGPL-3.0-only"

    # ISC License
    if "isc license" in first_line or "isc license" in content_lower[:200]:
        return "ISC License", "ISC"

    # MPL License
    if "mozilla public license" in content_lower[:200]:
        if "2.0" in content_lower[:200]:
            return "Mozilla Public License 2.0", "MPL-2.0"
        else:
            return "Mozilla Public License", "MPL-2.0"

    # Unlicense
    if "unlicense" in first_line or "unlicense" in content_lower[:200]:
        return "Unlicense", "Unlicense"

    # Check if it's a custom license
    if len(content) > 100:
        return "Custom License", None

    return None, None


def extract_license_from_license_file(owner: str, repo: str) -> Optional[Dict]:
    """
    Extract license information from LICENSE file in the repository.

    This function attempts to fetch and analyze the LICENSE file from the repository.
    It tries multiple branch names (main, master, develop) and multiple file names
    (LICENSE, LICENSE.md, LICENSE.txt, COPYING).

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[Dict]: A dictionary with license information or None if not found.
    """
    # Try different branch names
    branches = ["main", "master", "develop", "trunk"]
    
    # Try different license file names
    license_files = ["LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "COPYING.md"]

    for branch in branches:
        for license_file in license_files:
            try:
                content = fetch_file_content(owner, repo, license_file, branch=branch)
                if content:
                    # Analyze the license file content
                    license_name, spdx_id = detect_license_from_content(content)
                    
                    if license_name:
                        license_dict = {
                            "@type": "CreativeWork",
                            "name": license_name,
                        }
                        
                        # Add SPDX identifier if found
                        if spdx_id:
                            license_dict["@id"] = f"{SPDX_LICENSE_URL_BASE}/{spdx_id}"
                        
                        return license_dict
            except Exception:
                # Silently continue to next option
                continue

    return None


def extract_license_from_github_api(owner: str, repo: str) -> Optional[Dict]:
    """
    Extract license information from GitHub API repository metadata.

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

        license_data = repo_info.get("license")
        if not license_data:
            return None

        license_name = license_data.get("name", "")
        spdx_id = license_data.get("spdx_id")

        if not license_name:
            return None

        license_dict = {
            "@type": "CreativeWork",
            "name": license_name,
        }

        # Use SPDX ID from GitHub API if available
        if spdx_id and spdx_id != "NOASSERTION":
            license_dict["@id"] = f"{SPDX_LICENSE_URL_BASE}/{spdx_id}"
        else:
            # Try to get SPDX ID from our mapping
            mapped_spdx = get_spdx_identifier(license_name)
            if mapped_spdx:
                license_dict["@id"] = f"{SPDX_LICENSE_URL_BASE}/{mapped_spdx}"

        return license_dict

    except Exception:
        return None


def extract_license_from_setup_py(owner: str, repo: str) -> Optional[Dict]:
    """
    Extract license information from setup.py file.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[Dict]: A dictionary with license information or None if not found.
    """
    try:
        content = fetch_file_content(owner, repo, "setup.py")
        if not content:
            return None

        # Look for license= parameter
        match = re.search(r'license\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            license_name = match.group(1).strip()
            spdx_id = get_spdx_identifier(license_name)

            license_dict = {
                "@type": "CreativeWork",
                "name": license_name,
            }

            if spdx_id:
                license_dict["@id"] = f"{SPDX_LICENSE_URL_BASE}/{spdx_id}"

            return license_dict

    except Exception:
        pass

    return None


def extract_license_from_pyproject_toml(owner: str, repo: str) -> Optional[Dict]:
    """
    Extract license information from pyproject.toml file.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[Dict]: A dictionary with license information or None if not found.
    """
    try:
        content = fetch_file_content(owner, repo, "pyproject.toml")
        if not content:
            return None

        # Look for license field
        match = re.search(r'license\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            license_name = match.group(1).strip()
            spdx_id = get_spdx_identifier(license_name)

            license_dict = {
                "@type": "CreativeWork",
                "name": license_name,
            }

            if spdx_id:
                license_dict["@id"] = f"{SPDX_LICENSE_URL_BASE}/{spdx_id}"

            return license_dict

    except Exception:
        pass

    return None


def extract_license_from_package_json(owner: str, repo: str) -> Optional[Dict]:
    """
    Extract license information from package.json file.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[Dict]: A dictionary with license information or None if not found.
    """
    try:
        content = fetch_file_content(owner, repo, "package.json")
        if not content:
            return None

        package_data = json.loads(content)
        license_name = package_data.get("license")

        if not license_name:
            return None

        spdx_id = get_spdx_identifier(license_name)

        license_dict = {
            "@type": "CreativeWork",
            "name": license_name,
        }

        if spdx_id:
            license_dict["@id"] = f"{SPDX_LICENSE_URL_BASE}/{spdx_id}"

        return license_dict

    except Exception:
        pass

    return None


def get(repository_url: str) -> Dict:
    """
    Extract license information from a GitHub repository.

    This function uses multiple strategies to extract license information:
    1. From LICENSE file content in the repository (most reliable)
    2. From GitHub API repository metadata
    3. From setup.py license field
    4. From pyproject.toml license field
    5. From package.json license field

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'license' property and its value.
              Returns an empty dict if no license can be extracted.

    Example:
        >>> result = get("https://github.com/rsiebes/sshoc-nl-codemeta-generator")
        >>> print(result)
        {'license': {'@type': 'CreativeWork', 'name': 'MIT License', '@id': 'https://spdx.org/licenses/MIT'}}
    """
    repository_url = normalize_url(repository_url)
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    license_info = None

    # Strategy 1: Try LICENSE file first (most reliable)
    license_info = extract_license_from_license_file(owner, repo)
    if license_info:
        return {"license": license_info}

    # Strategy 2: Try GitHub API
    license_info = extract_license_from_github_api(owner, repo)
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
        "https://github.com/openai/gpt-2",
    ]

    for repo_url in test_repos:
        print(f"\nTesting: {repo_url}")
        result = get(repo_url)
        if result:
            print(f"License: {result}")
        else:
            print("No license found")
