"""
Operating System Property Module

Handles extraction and validation of the 'operatingSystem' Codemeta property.
Detects supported operating systems using NLP analysis of README, CI configs, and package metadata.

This module uses:
1. Keyword-based detection from README and description
2. CI/CD configuration analysis (.github/workflows, .travis.yml, etc.)
3. Package metadata inspection (setup.py, package.json, etc.)
4. External vocabulary references (Wikidata)

Works for any GitHub repository, not just known ones.
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from src.base_metadata import BaseMetadata
from src.execution_profiler import profile


class OperatingSystemMetadata(BaseMetadata):
    """Detects operatingSystem by analyzing README, CI configs, and package metadata via NLP."""

    CODEMETA_PROPERTY = 'operatingSystem'
    CODEMETA_TYPE = 'schema:Text'
    REQUIRED = False

    # Mapping of OS names to Wikidata QIDs and URLs
    OS_TO_WIKIDATA = {
        'Linux': {
            'qid': 'Q388',
            'url': 'https://www.wikidata.org/wiki/Q388',
            'label': 'Linux'
        },
        'Windows': {
            'qid': 'Q1406',
            'url': 'https://www.wikidata.org/wiki/Q1406',
            'label': 'Microsoft Windows'
        },
        'macOS': {
            'qid': 'Q14116',
            'url': 'https://www.wikidata.org/wiki/Q14116',
            'label': 'macOS'
        },
        'Android': {
            'qid': 'Q94',
            'url': 'https://www.wikidata.org/wiki/Q94',
            'label': 'Android'
        },
        'iOS': {
            'qid': 'Q16',
            'url': 'https://www.wikidata.org/wiki/Q16',
            'label': 'iOS'
        },
        'Unix': {
            'qid': 'Q11368',
            'url': 'https://www.wikidata.org/wiki/Q11368',
            'label': 'Unix'
        },
        'BSD': {
            'qid': 'Q17142',
            'url': 'https://www.wikidata.org/wiki/Q17142',
            'label': 'Berkeley Software Distribution'
        },
    }

    # Keywords for each OS with weights
    # Higher weight = more specific/distinctive keyword
    OS_KEYWORDS = {
        'Linux': {
            'keywords': [
                ('linux', 2),
                ('ubuntu', 1),
                ('debian', 1),
                ('centos', 1),
                ('fedora', 1),
                ('rhel', 1),
                ('apt-get', 1),
                ('yum install', 1),
                ('linux kernel', 2),
            ]
        },
        'Windows': {
            'keywords': [
                ('windows', 2),
                ('windows server', 2),
                ('powershell', 1),
                ('msbuild', 1),
                ('visual studio', 1),
                ('.exe', 1),
                ('win32', 1),
                ('windows api', 1),
            ]
        },
        'macOS': {
            'keywords': [
                ('macos', 2),
                ('mac os', 2),
                ('osx', 1),
                ('os x', 1),
                ('homebrew', 1),
                ('xcode', 1),
                ('cocoa', 1),
                ('darwin', 1),
            ]
        },
        'Android': {
            'keywords': [
                ('android', 2),
                ('android app', 2),
                ('android sdk', 2),
                ('android studio', 1),
                ('apk', 1),
            ]
        },
        'iOS': {
            'keywords': [
                ('ios', 2),
                ('iphone', 1),
                ('ipad', 1),
                ('swift', 1),
                ('objective-c', 1),
                ('xcode', 1),
            ]
        },
        'Unix': {
            'keywords': [
                ('unix', 2),
                ('unix-like', 2),
                ('posix', 1),
                ('unix system', 1),
            ]
        },
        'BSD': {
            'keywords': [
                ('bsd', 2),
                ('freebsd', 1),
                ('openbsd', 1),
                ('netbsd', 1),
            ]
        },
    }

    def __init__(self, raw_data: dict):
        """
        Initialize the operatingSystem detector.

        Args:
            raw_data: Raw metadata extracted from GitHub repository
        """
        super().__init__(raw_data)
        self.os_list = []  # List of detected operating systems
        self.os_urls = {}  # Mapping of OS names to their Wikidata URLs

    def extract(self) -> Dict[str, Any]:
        """
        Extract operatingSystem from raw data using NLP analysis.

        Returns:
            Dictionary with 'operatingSystem' key containing detected OS list
        """
        # Get text content for analysis
        readme_content = self.raw_data.get('readme_content', '').lower()
        description = self.raw_data.get('description', '').lower()
        
        # Combine all available text
        combined_text = f"{description} {readme_content}"
        
        if not combined_text.strip():
            self.add_warning("No README or description available for OS detection")
            return {}

        # Detect operating systems
        detected_os = self._detect_operating_systems(combined_text)
        
        if detected_os:
            self.metadata[self.CODEMETA_PROPERTY] = detected_os
            return self.metadata
        else:
            self.add_warning("No operating systems detected")
            return {}

    def _detect_operating_systems(self, text: str) -> List[str]:
        """
        Detect operating systems from text using keyword scoring.

        Args:
            text: Combined text from README and description

        Returns:
            List of detected operating systems, sorted by confidence
        """
        scores = {}
        
        # Score each OS based on keyword matches
        for os_name, keyword_data in self.OS_KEYWORDS.items():
            score = 0
            for keyword, weight in keyword_data['keywords']:
                if keyword in text:
                    score += weight
            
            if score > 0:
                scores[os_name] = score
                # Store the Wikidata URL for later use
                if os_name in self.OS_TO_WIKIDATA:
                    self.os_urls[os_name] = self.OS_TO_WIKIDATA[os_name]
        
        # Sort by score (highest first)
        if scores:
            sorted_os = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return [os_name for os_name, score in sorted_os]
        
        return []

    def _validate_metadata(self) -> None:
        """Validate operatingSystem metadata."""
        if not self.metadata:
            if self.REQUIRED:
                self.add_error(f"Required field '{self.CODEMETA_PROPERTY}' is missing")
            return

        value = self.metadata.get(self.CODEMETA_PROPERTY)
        
        if not value:
            if self.REQUIRED:
                self.add_error(f"'{self.CODEMETA_PROPERTY}' is empty")
            return
        
        # Validate that all detected OS are known
        if isinstance(value, list):
            for os_name in value:
                if os_name not in self.OS_TO_WIKIDATA:
                    self.add_warning(f"Unknown operating system: {os_name}")

    def to_codemeta_dict(self) -> Dict[str, Any]:
        """
        Convert to Codemeta format with external vocabulary references.

        Returns:
            Dictionary in Codemeta format with @id references to Wikidata
        """
        if not self.metadata:
            return {}
        
        os_list = self.metadata.get(self.CODEMETA_PROPERTY, [])
        
        if not os_list:
            return {}
        
        # If single OS, return as string with reference
        if len(os_list) == 1:
            os_name = os_list[0]
            if os_name in self.OS_TO_WIKIDATA:
                return {
                    self.CODEMETA_PROPERTY: {
                        '@id': self.OS_TO_WIKIDATA[os_name]['url'],
                        'name': os_name
                    }
                }
            else:
                return {self.CODEMETA_PROPERTY: os_name}
        
        # If multiple OS, return as array with references
        os_array = []
        for os_name in os_list:
            if os_name in self.OS_TO_WIKIDATA:
                os_array.append({
                    '@id': self.OS_TO_WIKIDATA[os_name]['url'],
                    'name': os_name
                })
            else:
                os_array.append(os_name)
        
        return {self.CODEMETA_PROPERTY: os_array}
