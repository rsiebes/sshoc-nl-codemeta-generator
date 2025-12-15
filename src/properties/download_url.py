"""
Download URL property module for Codemeta 3.1 generator.

This module extracts download URLs for software binaries/packages from repositories.
Supports GitHub, GitLab, Bitbucket, and package registries.
"""

import re
from typing import Dict, Optional
from src.base_metadata import BaseMetadata


class DownloadUrlMetadata(BaseMetadata):
    """Extract download URL from repository metadata."""
    
    PROPERTY_NAME = "downloadUrl"
    SCHEMA_ORG_TYPE = "URL"
    
    def __init__(self, raw_data: Dict):
        """Initialize the DownloadUrlMetadata extractor.
        
        Args:
            raw_data: Raw repository metadata from scraper
        """
        super().__init__(raw_data)
    
    def extract(self) -> Dict:
        """
        Extract download URL from repository metadata.
        
        Extraction sources (priority order):
        1. Direct 'downloadUrl' field
        2. Latest release asset (GitHub/GitLab)
        3. Package registry (PyPI, npm, etc.)
        4. Archive download URL
        5. Releases page URL
        
        Returns:
            Dictionary with downloadUrl or empty dict
        """
        download_url = None
        
        # 1. Check direct downloadUrl field
        direct_url = self._get_value('downloadUrl')
        if direct_url:
            download_url = direct_url
        
        # 2. Check for latest release
        if not download_url:
            download_url = self._extract_from_releases()
        
        # 3. Check for package registry
        if not download_url:
            download_url = self._extract_from_package_registry()
        
        # 4. Construct archive download URL
        if not download_url:
            download_url = self._construct_archive_url()
        
        # 5. Fall back to releases page
        if not download_url:
            download_url = self._construct_releases_page_url()
        
        # Store in metadata
        if download_url:
            self.metadata[self.PROPERTY_NAME] = download_url
        
        return self.metadata
    
    def _extract_from_releases(self) -> Optional[str]:
        """
        Extract download URL from repository releases.
        
        For GitHub: Check latest release assets
        For GitLab: Check release links
        For Bitbucket: Check downloads section
        
        Returns:
            Download URL or None
        """
        # Check if releases data is available
        releases = self._get_value('releases')
        if releases and isinstance(releases, list) and len(releases) > 0:
            # Get the latest release
            latest_release = releases[0]
            if isinstance(latest_release, dict):
                # Check for assets
                assets = latest_release.get('assets', [])
                if assets and len(assets) > 0:
                    # Return the first asset download URL
                    first_asset = assets[0]
                    if isinstance(first_asset, dict):
                        return first_asset.get('browser_download_url')
        
        # Try to construct from code_repository URL
        code_repo = self._get_value('code_repository')
        if not code_repo:
            return None
        
        # GitHub releases
        if 'github.com' in code_repo:
            # Only construct /releases/download/ URL if we know there are assets
            # Otherwise it will 404. Fall through to archive download instead.
            # Note: releases data from scraper doesn't include asset info,
            # so we can't reliably determine if assets exist.
            pass
        
        # GitLab releases
        if 'gitlab' in code_repo:
            latest_tag = self._get_value('version')
            if latest_tag:
                repo_url = code_repo.rstrip('/').replace('.git', '')
                return f"{repo_url}/-/releases/{latest_tag}"
        
        # Bitbucket downloads
        if 'bitbucket.org' in code_repo:
            repo_url = code_repo.rstrip('/').replace('.git', '')
            return f"{repo_url}/downloads/"
        
        return None
    
    def _extract_from_package_registry(self) -> Optional[str]:
        """
        Extract download URL from package registries.
        
        Checks for:
        - PyPI (Python)
        - npm (JavaScript)
        - Maven Central (Java)
        - RubyGems (Ruby)
        - CRAN (R)
        
        Returns:
            Package registry URL or None
        """
        # Check programming language
        prog_lang = self._get_value('programmingLanguage')
        if not prog_lang:
            return None
        
        # Get package name (usually same as repository name)
        name = self._get_value('name')
        if not name:
            return None
        
        # Normalize language
        if isinstance(prog_lang, list):
            prog_lang = prog_lang[0] if prog_lang else None
        
        if isinstance(prog_lang, dict):
            prog_lang = prog_lang.get('name', '')
        
        lang_lower = str(prog_lang).lower()
        
        # PyPI for Python
        if 'python' in lang_lower:
            return f"https://pypi.org/project/{name}/"
        
        # npm for JavaScript/TypeScript
        if any(js in lang_lower for js in ['javascript', 'typescript', 'node']):
            return f"https://www.npmjs.com/package/{name}"
        
        # RubyGems for Ruby
        if 'ruby' in lang_lower:
            return f"https://rubygems.org/gems/{name}"
        
        # CRAN for R
        if lang_lower == 'r':
            return f"https://cran.r-project.org/package={name}"
        
        return None
    
    def _construct_archive_url(self) -> Optional[str]:
        """
        Construct archive download URL.
        
        For GitHub: /archive/refs/tags/{version}.zip
        For GitLab: /-/archive/{version}/{name}-{version}.tar.gz
        For Bitbucket: /get/{version}.zip
        
        Returns:
            Archive download URL or None
        """
        code_repo = self._get_value('code_repository')
        if not code_repo:
            return None
        
        version = self._get_value('version')
        name = self._get_value('name')
        
        # GitHub archive
        if 'github.com' in code_repo:
            repo_url = code_repo.rstrip('/').replace('.git', '')
            if version:
                return f"{repo_url}/archive/refs/tags/{version}.zip"
            else:
                # Default to main/master branch
                return f"{repo_url}/archive/refs/heads/main.zip"
        
        # GitLab archive
        if 'gitlab' in code_repo:
            repo_url = code_repo.rstrip('/').replace('.git', '')
            if version and name:
                return f"{repo_url}/-/archive/{version}/{name}-{version}.tar.gz"
            elif version:
                return f"{repo_url}/-/archive/{version}/archive.tar.gz"
        
        # Bitbucket archive
        if 'bitbucket.org' in code_repo:
            repo_url = code_repo.rstrip('/').replace('.git', '')
            if version:
                return f"{repo_url}/get/{version}.zip"
        
        return None
    
    def _construct_releases_page_url(self) -> Optional[str]:
        """
        Construct releases page URL as fallback.
        
        Returns:
            Releases page URL or None
        """
        code_repo = self._get_value('code_repository')
        if not code_repo:
            return None
        
        # GitHub releases page
        if 'github.com' in code_repo:
            repo_url = code_repo.rstrip('/').replace('.git', '')
            return f"{repo_url}/releases"
        
        # GitLab releases page
        if 'gitlab' in code_repo:
            repo_url = code_repo.rstrip('/').replace('.git', '')
            return f"{repo_url}/-/releases"
        
        # Bitbucket downloads page
        if 'bitbucket.org' in code_repo:
            repo_url = code_repo.rstrip('/').replace('.git', '')
            return f"{repo_url}/downloads/"
        
        return None
    
    def _validate_metadata(self) -> None:
        """
        Validate the extracted download URL.
        
        Raises:
            ValueError: If download URL is invalid
        """
        if self.PROPERTY_NAME not in self.metadata:
            return
        
        download_url = self.metadata[self.PROPERTY_NAME]
        
        # Check if it's a valid string
        if not isinstance(download_url, str):
            raise ValueError(f"Download URL must be a string, got {type(download_url)}")
        
        # Check if it's a valid URL
        if not download_url.startswith(('http://', 'https://')):
            raise ValueError(f"Download URL must be a valid URL starting with http:// or https://")
        
        # Warn if it's just a releases page (not a direct download)
        if any(keyword in download_url for keyword in ['/releases', '/downloads', '/packages']):
            if not any(ext in download_url for ext in ['.zip', '.tar.gz', '.tar', '.exe', '.dmg', '.pkg', '.deb', '.rpm']):
                self.warnings.append(f"Download URL points to a releases page rather than a direct download: {download_url}")
