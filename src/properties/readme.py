"""
Readme property module for Codemeta metadata extraction.

This module handles the extraction and validation of the readme property,
which provides a URL to the README documentation file.
"""

from typing import Dict, Any, Optional
from src.base_metadata import BaseMetadata
from src.execution_profiler import profile


class ReadmeMetadata(BaseMetadata):
    """
    Handles extraction and validation of readme property.
    
    The readme property should be a URL pointing to the README documentation.
    According to Codemeta 3.1, this is a URL or Text type.
    """
    
    CODEMETA_PROPERTY = "readme"
    CODEMETA_TYPE = "URL"
    REQUIRED = False
    
    def extract(self) -> Dict[str, Any]:
        """
        Extract readme URL from raw data.
        
        Returns:
            Dictionary with readme URL or empty dict if not found
        """
        result = {}
        
        # Try to extract from various sources
        readme_url = None
        
        # Source 1: Direct readme field (should be a URL)
        if 'readme' in self.raw_data and self.raw_data['readme']:
            readme_value = self.raw_data['readme']
            # If it's already a URL, use it
            if isinstance(readme_value, str) and (readme_value.startswith('http://') or readme_value.startswith('https://')):
                readme_url = readme_value
            # If it's text content, construct URL from repository
            elif isinstance(readme_value, str) and 'code_repository' in self.raw_data:
                # Construct README URL from repository URL
                repo_url = self.raw_data['code_repository']
                if repo_url:
                    readme_url = f"{repo_url}#readme"
        
        # Source 2: readme_url field
        if not readme_url and 'readme_url' in self.raw_data:
            readme_url = self.raw_data['readme_url']
        
        # Source 3: documentation field
        if not readme_url and 'documentation' in self.raw_data:
            readme_url = self.raw_data['documentation']
        
        # Source 4: Construct from code_repository
        if not readme_url and 'code_repository' in self.raw_data:
            repo_url = self.raw_data['code_repository']
            if repo_url:
                # For GitHub repositories, construct README URL
                if 'github.com' in repo_url:
                    readme_url = f"{repo_url}#readme"
                elif 'gitlab.com' in repo_url:
                    readme_url = f"{repo_url}#readme"
                elif 'bitbucket.org' in repo_url:
                    readme_url = f"{repo_url}#readme"
        
        if readme_url:
            result['readme'] = readme_url
            self.metadata['readme'] = readme_url
        
        return result
    
    def _validate_metadata(self) -> None:
        """
        Validate the extracted readme metadata.
        
        Checks:
        - readme must be a string (URL)
        - readme must be a valid URL format
        - readme should not be empty
        """
        if not self.metadata:
            return
        
        readme = self.metadata.get('readme')
        
        if readme is None:
            return
        
        # Check type
        if not isinstance(readme, str):
            self.errors.append("readme must be a string (URL)")
            return
        
        # Check not empty
        if not readme.strip():
            self.errors.append("readme URL cannot be empty")
            return
        
        # Check URL format
        if not (readme.startswith('http://') or readme.startswith('https://')):
            self.warnings.append("readme should be a valid URL starting with http:// or https://")
        
        # Check URL length
        if len(readme) > 2000:
            self.warnings.append("readme URL is very long (>2000 characters)")
    
    def to_codemeta_dict(self) -> Dict[str, Any]:
        """
        Convert metadata to Codemeta format.
        
        Returns:
            Dictionary in Codemeta format
        """
        if not self.metadata or 'readme' not in self.metadata:
            return {}
        
        return {
            'readme': self.metadata['readme']
        }
