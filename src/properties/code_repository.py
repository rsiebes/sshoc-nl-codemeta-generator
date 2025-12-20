"""
Code Repository Property Module

Handles extraction and validation of the 'codeRepository' Codemeta property.
This is the URL of the version control repository where the source code is hosted.
"""

from typing import Dict, Any, Optional
import re
from src.base_metadata import BaseMetadata
from src.execution_profiler import profile


class CodeRepositoryMetadata(BaseMetadata):
    """Handles code repository metadata extraction and validation."""

    CODEMETA_PROPERTY = 'codeRepository'
    CODEMETA_TYPE = 'schema:URL'
    REQUIRED = False

    def extract(self) -> Dict[str, Any]:
        """
        Extract code repository URL from raw data.

        The repository URL can come from:
        1. Direct 'code_repository' field in raw data
        2. 'codeRepository' field in raw data
        3. 'repository_url' field
        4. 'repo_url' field
        5. Constructed from owner and repo name

        Returns:
            Dictionary with 'codeRepository' key
        """
        # Try different sources for the repository URL
        repo_url = self._get_value('code_repository')
        
        if not repo_url:
            repo_url = self._get_value('codeRepository')
        
        if not repo_url:
            repo_url = self._get_value('repository_url')
        
        if not repo_url:
            repo_url = self._get_value('repo_url')
        
        # Try to construct from owner and name
        if not repo_url:
            owner = self._get_value('owner')
            repo_name = self._get_value('name')
            if owner and repo_name:
                repo_url = f"https://github.com/{owner}/{repo_name}"

        if not repo_url:
            self.add_warning("Code repository URL could not be extracted from any source")
            return {}

        # Validate the URL
        if not self._is_valid_url(repo_url):
            self.add_error(f"Invalid repository URL format: {repo_url}")
            return {}

        # Normalize the URL
        normalized_url = self._normalize_repo_url(repo_url)
        
        if normalized_url:
            self.metadata[self.CODEMETA_PROPERTY] = normalized_url
            return self.metadata
        else:
            self.add_error("Repository URL could not be normalized")
            return {}

    def _normalize_repo_url(self, url: str) -> Optional[str]:
        """
        Normalize a repository URL.

        Args:
            url: Repository URL to normalize

        Returns:
            Normalized URL or None
        """
        if not url:
            return None
        
        url = url.strip()
        
        # Remove trailing slash first
        while url.endswith('/') and not url.endswith('://'):
            url = url[:-1]
        
        # Remove .git suffix for consistency
        if url.endswith('.git'):
            url = url[:-4]
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://', 'git://', 'ssh://')):
            url = 'https://' + url
        
        return url

    def _validate_metadata(self) -> None:
        """Validate code repository metadata."""
        if not self.metadata:
            if self.REQUIRED:
                self.add_error(f"Required field '{self.CODEMETA_PROPERTY}' is missing")
            return

        repo_url = self.metadata.get(self.CODEMETA_PROPERTY)
        
        # Check if URL exists
        if not repo_url:
            if self.REQUIRED:
                self.add_error(f"'{self.CODEMETA_PROPERTY}' is empty")
            return

        # Check if URL is a string
        if not isinstance(repo_url, str):
            self.add_error(f"'{self.CODEMETA_PROPERTY}' must be a string, got {type(repo_url).__name__}")
            return

        # Check URL format
        if not self._is_valid_url(repo_url):
            self.add_error(f"'{self.CODEMETA_PROPERTY}' is not a valid URL: {repo_url}")
            return

        # Check URL length
        if len(repo_url) > 2048:
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' is very long ({len(repo_url)} characters)")

        # Check for common issues
        if ' ' in repo_url:
            self.add_error(f"'{self.CODEMETA_PROPERTY}' contains spaces")

        # Validate repository URL structure
        if not self._is_valid_repo_url_structure(repo_url):
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' may not be a valid repository URL")

        # Check if it's a known VCS hosting service
        if not self._is_known_vcs_host(repo_url):
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' is not from a known VCS hosting service")

    def _is_valid_repo_url_structure(self, url: str) -> bool:
        """
        Check if URL has valid repository structure.

        Args:
            url: URL to check

        Returns:
            True if valid structure, False otherwise
        """
        # Basic repository URL structure validation
        url_pattern = r'^https?://[a-zA-Z0-9\-._~:/?#\[\]@!$&\'()*+,;=]+/[a-zA-Z0-9\-._]+/[a-zA-Z0-9\-._]+/?$'
        return bool(re.match(url_pattern, url))

    def _is_known_vcs_host(self, url: str) -> bool:
        """
        Check if URL is from a known VCS hosting service.

        Args:
            url: URL to check

        Returns:
            True if from known host, False otherwise
        """
        known_hosts = [
            'github.com',
            'gitlab.com',
            'bitbucket.org',
            'gitea.io',
            'gitee.com',
            'codeberg.org',
            'sourceforge.net',
            'launchpad.net'
        ]
        
        return any(host in url.lower() for host in known_hosts)

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
