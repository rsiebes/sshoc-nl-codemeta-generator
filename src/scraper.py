"""
GitHub Web Scraper Module

This module handles web scraping of GitHub repositories to extract metadata.
It uses requests and BeautifulSoup to parse GitHub pages without using the API.
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


class GitHubScraper:
    """Scrapes GitHub repository metadata from web pages."""

    def __init__(self, timeout: int = 10):
        """
        Initialize the GitHub scraper.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def parse_repo_url(self, url: str) -> Tuple[str, str]:
        """
        Parse a GitHub repository URL to extract owner and repo name.

        Args:
            url: GitHub repository URL

        Returns:
            Tuple of (owner, repo_name)

        Raises:
            ValueError: If URL is not a valid GitHub repository URL
        """
        # Remove trailing slash and .git
        url = url.rstrip('/').rstrip('.git')

        # Extract from various GitHub URL formats
        patterns = [
            r'github\.com/([^/]+)/([^/]+)/?$',  # https://github.com/owner/repo
            r'github\.com/([^/]+)/([^/]+)/tree',  # https://github.com/owner/repo/tree/branch
            r'github\.com/([^/]+)/([^/]+)/blob',  # https://github.com/owner/repo/blob/branch/file
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1), match.group(2)

        raise ValueError(f"Invalid GitHub repository URL: {url}")

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a GitHub page.

        Args:
            url: URL to fetch

        Returns:
            BeautifulSoup object or None if fetch fails
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def scrape_repository(self, repo_url: str) -> Dict:
        """
        Extract all metadata from a GitHub repository.

        Args:
            repo_url: GitHub repository URL

        Returns:
            Dictionary containing extracted metadata
        """
        owner, repo_name = self.parse_repo_url(repo_url)
        base_url = f"https://github.com/{owner}/{repo_name}"

        metadata = {
            'owner': owner,
            'name': repo_name,
            'repo_name': repo_name,
            'code_repository': base_url,
            'url': base_url,
            'description': None,
            'repo_description': None,
            'homepage': None,
            'topics': [],
            'keywords': [],
            'language': None,
            'languages': [],
            'license': None,
            'license_identifier': None,
            'readme': None,
            'releases': [],
            'version': None,
        }

        # Fetch main repository page
        soup = self.fetch_page(base_url)
        if not soup:
            return metadata

        # Extract all metadata
        self._extract_basic_info(soup, metadata)
        self._extract_languages(soup, metadata)
        self._extract_topics(soup, metadata)
        self._extract_license(soup, metadata)
        
        # Fetch README
        metadata['readme'] = self._fetch_readme(base_url, owner, repo_name)

        # Fetch releases
        releases = self._fetch_releases(base_url)
        if releases:
            metadata['releases'] = releases
            # Set latest version
            if releases and isinstance(releases, list) and len(releases) > 0:
                metadata['version'] = releases[0].get('tag', '')

        return metadata

    def _extract_basic_info(self, soup: BeautifulSoup, metadata: Dict) -> None:
        """Extract basic repository information."""
        # Description
        desc_elem = soup.find('p', class_='f4')
        if not desc_elem:
            # Try alternative selectors
            desc_elem = soup.find('p', {'data-pjax': '#repo-content-pjax-container'})
        if desc_elem:
            desc_text = desc_elem.get_text(strip=True)
            metadata['description'] = desc_text
            metadata['repo_description'] = desc_text

        # Homepage URL
        homepage_elem = soup.find('a', {'data-testid': 'home-page-url-link'})
        if not homepage_elem:
            homepage_elem = soup.find('a', class_='text-bold')
        if homepage_elem and homepage_elem.get('href'):
            homepage = homepage_elem.get('href')
            if homepage and not homepage.startswith('#'):
                metadata['homepage'] = homepage

    def _extract_languages(self, soup: BeautifulSoup, metadata: Dict) -> None:
        """Extract programming languages."""
        try:
            # Primary language
            lang_elem = soup.find('span', {'itemprop': 'programmingLanguage'})
            if lang_elem:
                lang = lang_elem.get_text(strip=True)
                metadata['language'] = lang
                metadata['languages'] = [lang]
            
            # Additional languages from language bar
            lang_list = soup.find_all('a', {'data-ga-click': re.compile(r'Repository, language stats')})
            if lang_list:
                languages = []
                for elem in lang_list:
                    lang_text = elem.get_text(strip=True)
                    if lang_text and len(lang_text) < 30:
                        languages.append(lang_text)
                if languages:
                    metadata['languages'] = languages
                    if not metadata['language']:
                        metadata['language'] = languages[0]
                        
        except Exception as e:
            print(f"Error extracting languages: {e}")

    def _extract_topics(self, soup: BeautifulSoup, metadata: Dict) -> None:
        """Extract repository topics/keywords."""
        try:
            topic_elems = soup.find_all('a', class_='topic-tag')
            topics = [elem.get_text(strip=True) for elem in topic_elems if elem.get_text(strip=True)]
            metadata['topics'] = topics
            metadata['keywords'] = topics
        except Exception as e:
            print(f"Error extracting topics: {e}")

    def _extract_license(self, soup: BeautifulSoup, metadata: Dict) -> None:
        """Extract license information."""
        try:
            # Find license link or text
            license_elem = soup.find('a', href=re.compile(r'/blob/.*/LICENSE'))
            if not license_elem:
                license_elem = soup.find('a', string=re.compile(r'License', re.I))
            if not license_elem:
                # Try finding in sidebar
                license_elem = soup.find('svg', class_='octicon-law')
                if license_elem:
                    license_elem = license_elem.find_parent('div')
                    if license_elem:
                        license_elem = license_elem.find('a')
            
            if license_elem:
                license_text = license_elem.get_text(strip=True)
                # Clean up license text
                license_text = re.sub(r'^License:\s*', '', license_text, flags=re.I)
                license_text = re.sub(r'\s+license$', '', license_text, flags=re.I)
                metadata['license'] = license_text
                metadata['license_identifier'] = license_text
                
        except Exception as e:
            print(f"Error extracting license: {e}")

    def _fetch_readme(self, repo_url: str, owner: str, repo_name: str) -> Optional[str]:
        """Fetch README content."""
        try:
            # Try multiple README locations and branches
            branches = ['main', 'master']
            readme_files = ['README.md', 'README.rst', 'README.txt', 'README']
            
            for branch in branches:
                for readme_file in readme_files:
                    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/{readme_file}"
                    try:
                        response = self.session.get(raw_url, timeout=self.timeout)
                        if response.status_code == 200:
                            return response.text
                    except:
                        continue
                        
        except Exception as e:
            print(f"Error fetching README: {e}")
        return None

    def _fetch_releases(self, repo_url: str) -> List[Dict]:
        """Fetch list of releases."""
        releases = []
        try:
            releases_url = f"{repo_url}/releases"
            soup = self.fetch_page(releases_url)
            if soup:
                # Find release tags
                tag_links = soup.find_all('a', href=re.compile(r'/releases/tag/'))
                for link in tag_links[:10]:  # Limit to top 10
                    tag = link.get_text(strip=True)
                    if tag:
                        releases.append({
                            'tag': tag,
                            'version': tag,
                            'url': urljoin(releases_url, link.get('href', ''))
                        })
            
            # If no releases, try tags
            if not releases:
                tags_url = f"{repo_url}/tags"
                soup = self.fetch_page(tags_url)
                if soup:
                    tag_links = soup.find_all('a', href=re.compile(r'/releases/tag/'))
                    for link in tag_links[:10]:
                        tag = link.get_text(strip=True)
                        if tag:
                            releases.append({
                                'tag': tag,
                                'version': tag,
                                'url': urljoin(tags_url, link.get('href', ''))
                            })
                            
        except Exception as e:
            print(f"Error fetching releases: {e}")
        return releases

    @staticmethod
    def _parse_count(count_str: str) -> int:
        """Parse count strings like '1.2k' or '100'."""
        count_str = count_str.strip().lower()
        if 'k' in count_str:
            return int(float(count_str.replace('k', '')) * 1000)
        elif 'm' in count_str:
            return int(float(count_str.replace('m', '')) * 1000000)
        else:
            try:
                return int(count_str.replace(',', ''))
            except ValueError:
                return 0
