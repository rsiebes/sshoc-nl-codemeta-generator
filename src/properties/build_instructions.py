"""
Build Instructions Property Module

Handles extraction and validation of the 'buildInstructions' Codemeta property.
Links to installation/build documentation for the software.
"""

from typing import Dict, Any, Optional
from src.base_metadata import BaseMetadata
from src.execution_profiler import profile
import re


class BuildInstructionsMetadata(BaseMetadata):
    """Handles buildInstructions metadata extraction and validation."""

    CODEMETA_PROPERTY = 'buildInstructions'
    CODEMETA_TYPE = 'URL'
    REQUIRED = False

    # Common build instruction file names (case-insensitive)
    BUILD_FILES = [
        'INSTALL.md', 'INSTALL.txt', 'INSTALL.rst', 'INSTALL',
        'BUILD.md', 'BUILDING.md', 'BUILD.txt', 'BUILD.rst', 'BUILD',
        'SETUP.md', 'SETUP.txt', 'SETUP',
        'docs/installation.md', 'docs/install.md', 'docs/building.md', 'docs/build.md',
        'doc/installation.md', 'doc/install.md', 'doc/building.md', 'doc/build.md',
        'CONTRIBUTING.md',  # Often contains build instructions
    ]

    # README section patterns to look for
    README_SECTIONS = [
        'installation', 'install', 'building', 'build', 'build-instructions',
        'getting-started', 'setup', 'compiling', 'compile'
    ]

    def __init__(self, raw_data: Dict[str, Any]):
        """
        Initialize BuildInstructionsMetadata.
        
        Args:
            raw_data: Raw scraped data
        """
        super().__init__(raw_data)

    def extract(self) -> Dict[str, Any]:
        """
        Extract buildInstructions from raw data.

        Build instructions can come from:
        1. Direct 'buildInstructions' field
        2. INSTALL file (INSTALL.md, INSTALL.txt, etc.)
        3. BUILD file (BUILD.md, BUILDING.md, etc.)
        4. README sections (with anchor links)
        5. Documentation folder files
        6. CONTRIBUTING file

        Returns:
            Dictionary with 'buildInstructions' key containing URL
        """
        # Try to extract from raw data first
        build_url = self._get_value('buildInstructions')
        if build_url:
            self.metadata[self.CODEMETA_PROPERTY] = build_url
            return self.metadata

        # Try to construct from repository information
        owner = self._get_value('owner')
        # Handle owner as dict (from enhanced scraper)
        if isinstance(owner, dict):
            owner = owner.get('username') or owner.get('name')
        repo_name = self._get_value('repo_name') or self._get_value('name')
        
        if not owner or not repo_name:
            self.add_warning(f"Optional field '{self.CODEMETA_PROPERTY}' could not be extracted: missing repository info")
            return {}

        # Try to find build instruction files
        build_url = self._find_build_file(owner, repo_name)
        
        if build_url:
            self.metadata[self.CODEMETA_PROPERTY] = build_url
            return self.metadata

        # Try to find README section with build instructions
        readme_section_url = self._find_readme_section(owner, repo_name)
        
        if readme_section_url:
            self.metadata[self.CODEMETA_PROPERTY] = readme_section_url
            return self.metadata

        self.add_warning(f"Optional field '{self.CODEMETA_PROPERTY}' could not be extracted")
        return {}

    def _find_build_file(self, owner: str, repo_name: str) -> Optional[str]:
        """
        Find build instruction file in the repository.
        
        Args:
            owner: Repository owner
            repo_name: Repository name
            
        Returns:
            URL to build instruction file or None
        """
        # Get list of files from raw data if available
        files = self._get_value('files') or []
        
        # Check if any build instruction files exist
        for build_file in self.BUILD_FILES:
            # Check in files list (case-insensitive)
            for file_path in files:
                if file_path.lower() == build_file.lower():
                    # Construct GitHub URL
                    # Try main branch first, then master
                    return f"https://github.com/{owner}/{repo_name}/blob/main/{file_path}"
        
        # If no files list available, try common locations
        # Check for explicit build instruction file references
        build_file_ref = self._get_value('build_file')
        if build_file_ref:
            return f"https://github.com/{owner}/{repo_name}/blob/main/{build_file_ref}"
        
        return None

    def _find_readme_section(self, owner: str, repo_name: str) -> Optional[str]:
        """
        Find build instructions section in README.
        
        Args:
            owner: Repository owner
            repo_name: Repository name
            
        Returns:
            URL to README section or None
        """
        # Get README content if available
        readme_content = self._get_value('readme_content')
        
        if not readme_content:
            return None
        
        # Convert to lowercase for case-insensitive matching
        readme_lower = readme_content.lower()
        
        # Look for section headers
        for section in self.README_SECTIONS:
            # Match markdown headers: ## Installation, # Building, etc.
            # Also handle emoji and special characters before section names
            patterns = [
                rf'^#{{1,6}}\s+{section}\s*$',  # ## Installation
                rf'^#{{1,6}}\s+.*?{section}\s*$',  # ## ⚙️ Installation (with emoji)
                rf'^#{{1,6}}\s+{section}\s+instructions?\s*$',  # ## Installation Instructions
                rf'^#{{1,6}}\s+how\s+to\s+{section}\s*$',  # ## How to Install
            ]
            
            for pattern in patterns:
                if re.search(pattern, readme_lower, re.MULTILINE | re.IGNORECASE):
                    # Create anchor link (GitHub style)
                    anchor = section.lower().replace(' ', '-')
                    return f"https://github.com/{owner}/{repo_name}#{anchor}"
        
        return None

    def _validate_metadata(self) -> None:
        """Validate buildInstructions metadata."""
        if not self.metadata:
            return

        value = self.metadata.get(self.CODEMETA_PROPERTY)
        
        if not value:
            return
        
        # Validate it's a string (URL)
        if not isinstance(value, str):
            self.add_error(f"'{self.CODEMETA_PROPERTY}' must be a string (URL)")
            return
        
        # Validate URL format
        if not value.startswith(('http://', 'https://')):
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' should be a complete URL starting with http:// or https://")
        
        # Validate URL is not empty
        if not value.strip():
            self.add_error(f"'{self.CODEMETA_PROPERTY}' cannot be empty")
        
        # Check if it looks like a GitHub URL
        if 'github.com' in value.lower():
            # Validate GitHub URL format
            if not re.match(r'https://github\.com/[^/]+/[^/]+', value):
                self.add_warning(f"'{self.CODEMETA_PROPERTY}' does not appear to be a valid GitHub URL")
