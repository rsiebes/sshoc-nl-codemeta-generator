"""
Utility functions for Codemeta metadata generation.

Includes license mapping, URL normalization, and other helper functions.
"""

from typing import Dict, Optional, Tuple


# SPDX License mapping - common licenses to SPDX identifiers
SPDX_LICENSE_MAP = {
    'MIT': 'MIT',
    'MIT License': 'MIT',
    'Apache': 'Apache-2.0',
    'Apache 2.0': 'Apache-2.0',
    'Apache License 2.0': 'Apache-2.0',
    'Apache Software License': 'Apache-2.0',
    'GPL': 'GPL-3.0-only',
    'GPLv3': 'GPL-3.0-only',
    'GPL v3': 'GPL-3.0-only',
    'GPL-3.0': 'GPL-3.0-only',
    'GPL-3.0-only': 'GPL-3.0-only',
    'GNU General Public License v3': 'GPL-3.0-only',
    'GNU General Public License v3.0': 'GPL-3.0-only',
    'GNU General Public License (GPL) v3': 'GPL-3.0-only',
    'GPLv2': 'GPL-2.0-only',
    'GPL v2': 'GPL-2.0-only',
    'GPL-2.0': 'GPL-2.0-only',
    'GPL-2.0-only': 'GPL-2.0-only',
    'GNU General Public License v2': 'GPL-2.0-only',
    'GNU General Public License v2.0': 'GPL-2.0-only',
    'LGPL': 'LGPL-3.0-only',
    'LGPLv3': 'LGPL-3.0-only',
    'LGPL v3': 'LGPL-3.0-only',
    'LGPL-3.0': 'LGPL-3.0-only',
    'LGPL-3.0-only': 'LGPL-3.0-only',
    'GNU Lesser General Public License v3': 'LGPL-3.0-only',
    'LGPLv2': 'LGPL-2.0-only',
    'LGPL v2': 'LGPL-2.0-only',
    'LGPL-2.0': 'LGPL-2.0-only',
    'LGPL-2.0-only': 'LGPL-2.0-only',
    'GNU Lesser General Public License v2': 'LGPL-2.0-only',
    'BSD': 'BSD-3-Clause',
    'BSD-3-Clause': 'BSD-3-Clause',
    'BSD 3-Clause': 'BSD-3-Clause',
    'BSD License': 'BSD-3-Clause',
    'New BSD License': 'BSD-3-Clause',
    'BSD-2-Clause': 'BSD-2-Clause',
    'BSD 2-Clause': 'BSD-2-Clause',
    'Simplified BSD License': 'BSD-2-Clause',
    'ISC': 'ISC',
    'ISC License': 'ISC',
    'MPL': 'MPL-2.0',
    'MPL-2.0': 'MPL-2.0',
    'Mozilla Public License 2.0': 'MPL-2.0',
    'AGPL': 'AGPL-3.0-only',
    'AGPLv3': 'AGPL-3.0-only',
    'AGPL v3': 'AGPL-3.0-only',
    'AGPL-3.0': 'AGPL-3.0-only',
    'AGPL-3.0-only': 'AGPL-3.0-only',
    'GNU Affero General Public License v3': 'AGPL-3.0-only',
    'Unlicense': 'Unlicense',
    'Public Domain': 'Unlicense',
    'CC0': 'CC0-1.0',
    'CC0-1.0': 'CC0-1.0',
    'Creative Commons Zero': 'CC0-1.0',
    'Proprietary': 'Proprietary',
    'Proprietary License': 'Proprietary',
    'Closed Source': 'Proprietary',
}

# SPDX license URL base
SPDX_LICENSE_URL_BASE = 'https://spdx.org/licenses/'


def get_spdx_license(license_name: Optional[str]) -> Optional[str]:
    """
    Get SPDX license identifier from license name.

    Args:
        license_name: License name or identifier

    Returns:
        SPDX license identifier or None
    """
    if not license_name:
        return None
    
    license_name = license_name.strip()
    
    # Direct match
    if license_name in SPDX_LICENSE_MAP:
        return SPDX_LICENSE_MAP[license_name]
    
    # Case-insensitive match
    for key, value in SPDX_LICENSE_MAP.items():
        if key.lower() == license_name.lower():
            return value
    
    # Check if it's already a SPDX identifier
    if license_name and license_name[0].isupper() and '-' in license_name:
        # Looks like SPDX format, return as-is
        return license_name
    
    return None


def get_spdx_license_url(spdx_id: Optional[str]) -> Optional[str]:
    """
    Get SPDX license URL from SPDX identifier.

    Args:
        spdx_id: SPDX license identifier

    Returns:
        SPDX license URL or None
    """
    if not spdx_id:
        return None
    
    spdx_id = spdx_id.strip()
    
    # Special case for Proprietary
    if spdx_id.lower() == 'proprietary':
        return None
    
    # Construct SPDX URL
    return f"{SPDX_LICENSE_URL_BASE}{spdx_id}"


def normalize_license(license_input: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Normalize license input to SPDX identifier and URL.

    Args:
        license_input: License name, identifier, or URL

    Returns:
        Tuple of (SPDX identifier, SPDX URL)
    """
    if not license_input:
        return None, None
    
    license_input = license_input.strip()
    
    # If it's a URL, try to extract license from it
    if license_input.startswith('http'):
        # Try to extract SPDX ID from URL
        if 'spdx.org/licenses/' in license_input:
            # Extract license ID from URL
            parts = license_input.split('spdx.org/licenses/')
            if len(parts) > 1:
                spdx_id = parts[1].rstrip('/')
                return spdx_id, license_input
        # If it's a GitHub license URL, try to extract license name
        if 'github.com' in license_input and '/blob/' in license_input:
            # Extract filename
            parts = license_input.split('/')
            if parts[-1].upper() in ['LICENSE', 'LICENSE.MD', 'LICENSE.TXT']:
                # Can't determine license from URL alone
                return None, None
        return None, None
    
    # Try to get SPDX identifier
    spdx_id = get_spdx_license(license_input)
    if spdx_id:
        spdx_url = get_spdx_license_url(spdx_id)
        return spdx_id, spdx_url
    
    return None, None


def is_valid_spdx_license(spdx_id: Optional[str]) -> bool:
    """
    Check if a string is a valid SPDX license identifier.

    Args:
        spdx_id: SPDX license identifier to check

    Returns:
        True if valid SPDX identifier, False otherwise
    """
    if not spdx_id:
        return False
    
    # Check if it's in our known licenses
    if spdx_id in SPDX_LICENSE_MAP.values():
        return True
    
    # Check if it looks like SPDX format (contains - and uppercase)
    if '-' in spdx_id and any(c.isupper() for c in spdx_id):
        return True
    
    return False
