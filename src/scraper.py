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

    def get_repo_metadata(self, repo_url: str) -> Dict:
        """
        Extract metadata from a GitHub repository page.

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
            'url': base_url,
            'description': None,
            'homepage': None,
            'topics': [],
            'language': None,
            'stars': 0,
            'forks': 0,
            'watchers': 0,
            'license': None,
            'created_at': None,
            'updated_at': None,
            'pushed_at': None,
            'readme': None,
            'contributors': [],
            'releases': [],
        }

        # Fetch main repository page
        soup = self.fetch_page(base_url)
        if not soup:
            return metadata

        # Extract basic metadata from main page
        self._extract_basic_info(soup, metadata)
        self._extract_dates(soup, metadata)
        self._extract_languages(soup, metadata)
        self._extract_topics(soup, metadata)
        self._extract_license(soup, metadata)

        # Fetch README
        metadata['readme'] = self._fetch_readme(base_url)

        # Fetch contributors
        metadata['contributors'] = self._fetch_contributors(base_url)

        # Fetch releases
        metadata['releases'] = self._fetch_releases(base_url)

        return metadata

    def _extract_basic_info(self, soup: BeautifulSoup, metadata: Dict) -> None:
        """Extract basic repository information."""
        # Description
        desc_elem = soup.find('p', class_='f4')
        if desc_elem:
            metadata['description'] = desc_elem.get_text(strip=True)

        # Homepage
        homepage_elem = soup.find('a', {'data-test-selector': 'about-website-link'})
        if homepage_elem:
            metadata['homepage'] = homepage_elem.get('href')

        # Stars, forks, watchers
        try:
            # Look for star count
            star_elem = soup.find('a', {'href': re.compile(r'/stargazers$')})
            if star_elem:
                star_text = star_elem.get_text(strip=True)
                metadata['stars'] = self._parse_count(star_text)

            # Look for fork count
            fork_elem = soup.find('a', {'href': re.compile(r'/network/members$')})
            if fork_elem:
                fork_text = fork_elem.get_text(strip=True)
                metadata['forks'] = self._parse_count(fork_text)
        except Exception as e:
            print(f"Error extracting counts: {e}")

    def _extract_dates(self, soup: BeautifulSoup, metadata: Dict) -> None:
        """Extract creation and modification dates."""
        try:
            # Look for date information in the about section
            date_elements = soup.find_all('relative-time')
            if date_elements:
                for elem in date_elements:
                    datetime_str = elem.get('datetime')
                    if datetime_str:
                        # Try to parse as ISO format
                        try:
                            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                            if not metadata['updated_at']:
                                metadata['updated_at'] = dt.isoformat()
                        except ValueError:
                            pass
        except Exception as e:
            print(f"Error extracting dates: {e}")

    def _extract_languages(self, soup: BeautifulSoup, metadata: Dict) -> None:
        """Extract programming languages."""
        try:
            lang_elem = soup.find('span', {'itemprop': 'programmingLanguage'})
            if lang_elem:
                metadata['language'] = lang_elem.get_text(strip=True)
        except Exception as e:
            print(f"Error extracting languages: {e}")

    def _extract_topics(self, soup: BeautifulSoup, metadata: Dict) -> None:
        """Extract repository topics/tags."""
        try:
            topic_elems = soup.find_all('a', {'data-test-selector': 'topic-tag'})
            metadata['topics'] = [elem.get_text(strip=True) for elem in topic_elems]
        except Exception as e:
            print(f"Error extracting topics: {e}")

    def _extract_license(self, soup: BeautifulSoup, metadata: Dict) -> None:
        """Extract license information."""
        try:
            license_elem = soup.find('a', {'data-test-selector': 'license-link'})
            if license_elem:
                metadata['license'] = license_elem.get_text(strip=True)
        except Exception as e:
            print(f"Error extracting license: {e}")

    def _fetch_readme(self, repo_url: str) -> Optional[str]:
        """Fetch README content."""
        try:
            readme_url = f"{repo_url}/blob/main/README.md"
            soup = self.fetch_page(readme_url)
            if soup:
                # Try to find raw content
                raw_url = readme_url.replace('/blob/', '/raw/')
                response = self.session.get(raw_url, timeout=self.timeout)
                if response.status_code == 200:
                    return response.text
        except Exception as e:
            print(f"Error fetching README: {e}")
        return None

    def _fetch_contributors(self, repo_url: str) -> List[Dict]:
        """Fetch list of contributors."""
        contributors = []
        try:
            contributors_url = f"{repo_url}/graphs/contributors-data"
            # This endpoint returns JSON data
            response = self.session.get(contributors_url, timeout=self.timeout)
            if response.status_code == 200:
                # Parse JSON response
                data = response.json()
                for contributor in data[:10]:  # Limit to top 10
                    contributors.append({
                        'name': contributor.get('name'),
                        'url': contributor.get('url'),
                        'contributions': contributor.get('contributions', 0)
                    })
        except Exception as e:
            print(f"Error fetching contributors: {e}")
        return contributors

    def _fetch_releases(self, repo_url: str) -> List[Dict]:
        """Fetch list of releases."""
        releases = []
        try:
            releases_url = f"{repo_url}/releases"
            soup = self.fetch_page(releases_url)
            if soup:
                release_items = soup.find_all('a', {'data-test-selector': 'release-tag-link'})
                for item in release_items[:10]:  # Limit to top 10
                    releases.append({
                        'tag': item.get_text(strip=True),
                        'url': urljoin(releases_url, item.get('href', ''))
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
