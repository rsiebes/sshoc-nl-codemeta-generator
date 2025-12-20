"""
License Property Module

Handles extraction and validation of the 'license' Codemeta property.
The license specifies the terms under which the software is distributed.
"""

from typing import Dict, Any, Optional, Union, List
from src.base_metadata import BaseMetadata
from src.utils import normalize_license, get_spdx_license, get_spdx_license_url
from src.execution_profiler import profile


class LicenseMetadata(BaseMetadata):
    """Handles license metadata extraction and validation."""

    CODEMETA_PROPERTY = 'license'
    CODEMETA_TYPE = 'schema:CreativeWork'
    REQUIRED = False

    def extract(self) -> Dict[str, Any]:
        """
        Extract license from raw data.

        The license can come from:
        1. Direct 'license' field in raw data
        2. License file content from GitHub
        3. License identifier from repository metadata
        4. License URL from repository metadata

        Returns:
            Dictionary with 'license' key containing license object(s)
        """
        # Try different sources for the license
        license_data = self._get_value('license')
        
        if not license_data:
            # Try license file
            license_data = self._get_value('license_file')
        
        if not license_data:
            # Try license identifier
            license_data = self._get_value('license_identifier')
        
        if not license_data:
            # Try license URL
            license_data = self._get_value('license_url')

        if not license_data:
            self.add_warning("License could not be extracted from any source")
            return {}

        # Process and normalize license data
        license_objects = self._process_license(license_data)
        
        if license_objects:
            if isinstance(license_objects, list):
                if len(license_objects) == 1:
                    self.metadata[self.CODEMETA_PROPERTY] = license_objects[0]
                else:
                    self.metadata[self.CODEMETA_PROPERTY] = license_objects
            else:
                self.metadata[self.CODEMETA_PROPERTY] = license_objects
            return self.metadata
        else:
            self.add_warning("License could not be processed")
            return {}

    def _process_license(self, license_data: Any) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """
        Process license data into Codemeta format.

        Args:
            license_data: Raw license data (string, dict, or list)

        Returns:
            License object(s) in Codemeta format or None
        """
        if isinstance(license_data, str):
            # Process string license
            return self._process_license_string(license_data)
        elif isinstance(license_data, dict):
            # Process dict license
            return self._process_license_dict(license_data)
        elif isinstance(license_data, list):
            # Process multiple licenses
            licenses = []
            for item in license_data:
                processed = self._process_license(item)
                if processed:
                    if isinstance(processed, list):
                        licenses.extend(processed)
                    else:
                        licenses.append(processed)
            return licenses if licenses else None
        
        return None

    def _process_license_string(self, license_str: str) -> Optional[Dict[str, Any]]:
        """
        Process a license string.

        Args:
            license_str: License name or identifier

        Returns:
            License object in Codemeta format or None
        """
        if not license_str:
            return None
        
        license_str = license_str.strip()
        
        # Try to normalize to SPDX
        spdx_id, spdx_url = normalize_license(license_str)
        
        if spdx_id:
            license_obj = {
                '@id': spdx_url,
                'name': license_str
            }
            return license_obj
        else:
            # If not SPDX, still create license object with name
            license_obj = {
                'name': license_str
            }
            return license_obj

    def _process_license_dict(self, license_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a license dictionary.

        Args:
            license_dict: License dictionary

        Returns:
            License object in Codemeta format or None
        """
        if not license_dict:
            return None
        
        license_obj = {}
        
        # Extract license name
        name = license_dict.get('name') or license_dict.get('license')
        if name:
            license_obj['name'] = name
        
        # Extract or generate license URL
        url = license_dict.get('url') or license_dict.get('@id')
        if url:
            license_obj['@id'] = url
        elif name:
            # Try to get SPDX URL from name
            spdx_id, spdx_url = normalize_license(name)
            if spdx_url:
                license_obj['@id'] = spdx_url
        
        return license_obj if license_obj else None

    def _validate_metadata(self) -> None:
        """Validate license metadata."""
        if not self.metadata:
            if self.REQUIRED:
                self.add_error(f"Required field '{self.CODEMETA_PROPERTY}' is missing")
            return

        license_data = self.metadata.get(self.CODEMETA_PROPERTY)
        
        # Check if license exists
        if not license_data:
            if self.REQUIRED:
                self.add_error(f"'{self.CODEMETA_PROPERTY}' is empty")
            return

        # Validate single license or list of licenses
        if isinstance(license_data, list):
            for i, lic in enumerate(license_data):
                self._validate_license_object(lic, f"License {i+1}")
        else:
            self._validate_license_object(license_data)

    def _validate_license_object(self, license_obj: Any, label: str = "License") -> None:
        """
        Validate a single license object.

        Args:
            license_obj: License object to validate
            label: Label for error messages
        """
        if not isinstance(license_obj, dict):
            self.add_error(f"'{label}' must be a dictionary, got {type(license_obj).__name__}")
            return

        # Check for name or @id
        has_name = 'name' in license_obj
        has_id = '@id' in license_obj
        
        if not has_name and not has_id:
            self.add_error(f"'{label}' must have either 'name' or '@id' field")
            return

        # Validate name
        if has_name:
            name = license_obj['name']
            if not isinstance(name, str):
                self.add_error(f"'{label}' name must be a string")
            elif not name.strip():
                self.add_error(f"'{label}' name is empty")

        # Validate @id (should be a URL)
        if has_id:
            url = license_obj['@id']
            if not isinstance(url, str):
                self.add_error(f"'{label}' @id must be a string")
            elif not url.startswith('http'):
                self.add_warning(f"'{label}' @id should be a URL")

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
