"""
Version Property Module

Handles extraction and validation of the 'version' Codemeta property.
The version identifies the current release of the software.
"""

from typing import Dict, Any, Optional
import re
from src.base_metadata import BaseMetadata
from src.execution_profiler import profile


class VersionMetadata(BaseMetadata):
    """Handles version metadata extraction and validation."""

    CODEMETA_PROPERTY = 'version'
    CODEMETA_TYPE = 'schema:version'
    REQUIRED = False

    def extract(self) -> Dict[str, Any]:
        """
        Extract version from raw data.

        The version can come from:
        1. Direct 'version' field in raw data
        2. Latest release tag from GitHub
        3. Software version field
        4. Package version from setup.py or package.json

        Returns:
            Dictionary with 'version' key
        """
        # Try different sources for the version
        version = self._get_value('version')
        
        if not version:
            # Try latest release
            releases = self._get_value('releases')
            if releases and isinstance(releases, list) and len(releases) > 0:
                # Get the first release (latest)
                latest_release = releases[0]
                if isinstance(latest_release, dict):
                    version = latest_release.get('tag')
                elif isinstance(latest_release, str):
                    version = latest_release
        
        if not version:
            # Try software version
            version = self._get_value('software_version')
        
        if not version:
            # Try package version
            version = self._get_value('package_version')

        if not version:
            self.add_warning("Version could not be extracted from any source")
            return {}

        # Clean and validate the value
        cleaned_version = self._clean_version(version)
        
        if cleaned_version:
            self.metadata[self.CODEMETA_PROPERTY] = cleaned_version
            return self.metadata
        else:
            self.add_error("Version is empty or invalid")
            return {}

    def _clean_version(self, version: Any) -> Optional[str]:
        """
        Clean and normalize version string.

        Args:
            version: Raw version value

        Returns:
            Cleaned version string or None
        """
        if not version:
            return None
        
        # Convert to string
        version_str = str(version).strip()
        
        if not version_str:
            return None
        
        # Remove common prefixes
        if version_str.startswith('v'):
            version_str = version_str[1:]
        
        # Remove leading zeros from version numbers
        # e.g., "01.02.03" -> "1.2.3"
        parts = version_str.split('.')
        cleaned_parts = []
        for part in parts:
            # Extract numeric part
            numeric_match = re.match(r'^(\d+)', part)
            if numeric_match:
                cleaned_parts.append(str(int(numeric_match.group(1))))
            else:
                cleaned_parts.append(part)
        
        version_str = '.'.join(cleaned_parts)
        
        return version_str if version_str else None

    def _validate_metadata(self) -> None:
        """Validate version metadata."""
        if not self.metadata:
            if self.REQUIRED:
                self.add_error(f"Required field '{self.CODEMETA_PROPERTY}' is missing")
            return

        version = self.metadata.get(self.CODEMETA_PROPERTY)
        
        # Check if version exists
        if not version:
            if self.REQUIRED:
                self.add_error(f"'{self.CODEMETA_PROPERTY}' is empty")
            return

        # Check if version is a string
        if not isinstance(version, str):
            self.add_error(f"'{self.CODEMETA_PROPERTY}' must be a string, got {type(version).__name__}")
            return

        # Check minimum length
        if len(version) < 1:
            self.add_error(f"'{self.CODEMETA_PROPERTY}' must not be empty")
            return

        # Check maximum length
        if len(version) > 100:
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' is very long ({len(version)} characters)")

        # Check for invalid characters
        if version.startswith(' ') or version.endswith(' '):
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' has leading or trailing whitespace")

        # Validate version format (semantic versioning or similar)
        if not self._is_valid_version_format(version):
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' may not follow standard versioning format: {version}")

    def _is_valid_version_format(self, version: str) -> bool:
        """
        Check if version follows standard format.

        Args:
            version: Version string to check

        Returns:
            True if valid format, False otherwise
        """
        # Check for semantic versioning (X.Y.Z)
        semver_pattern = r'^\d+(\.\d+)*([a-zA-Z0-9\-\.]*)?$'
        return bool(re.match(semver_pattern, version))

    def to_codemeta_dict(self) -> Dict[str, Any]:
        """
        Convert to Codemeta format.

        Returns:
            Dictionary in Codemeta format
        """
        if not self.metadata:
            return {}
        
        return {
            self.CODEMETA_PROPERTY: self.metadata[self.CODEMETA_PROPERTY]
        }

    def get_codemeta_type(self) -> str:
        """
        Get the Codemeta type for this property.

        Returns:
            Codemeta type string
        """
        return self.CODEMETA_TYPE

    def is_required(self) -> bool:
        """
        Check if this property is required.

        Returns:
            True if required, False otherwise
        """
        return self.REQUIRED
