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

    def fetch_page(self, url: str, silent: bool = False) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a GitHub page.

        Args:
            url: URL to fetch
            silent: If True, suppress error messages (useful for optional resources)

        Returns:
            BeautifulSoup object or None if fetch fails
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            if not silent:
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
        
        # Fetch README and content
        readme_content = self._fetch_readme(base_url, owner, repo_name)
        if readme_content:
            metadata['readme_content'] = readme_content
            # Also construct README URL
            metadata['readme'] = f"{base_url}#readme"
        
        # Fetch file list for build instructions
        files = self._fetch_file_list(owner, repo_name)
        if files:
            metadata['files'] = files

        # Fetch releases
        releases = self._fetch_releases(base_url)
        if releases:
            metadata['releases'] = releases
            # Set latest version
            if releases and isinstance(releases, list) and len(releases) > 0:
                metadata['version'] = releases[0].get('tag', '')
        
        # Fetch owner profile information
        owner_profile = self._fetch_user_profile(owner)
        if owner_profile:
            # Update owner info with profile data
            metadata['owner'] = owner_profile
        
        # Fetch commit information to get email addresses
        commit_info = self._fetch_commit_info(base_url)
        if commit_info:
            metadata['commit_authors'] = commit_info
        
        # Fetch repository dates
        dates = self._fetch_repository_dates(owner, repo_name)
        if dates['date_created']:
            metadata['date_created'] = dates['date_created']
        if dates['date_modified']:
            metadata['date_modified'] = dates['date_modified']
        
        # Fetch contributors with profile enrichment
        contributors = self._fetch_contributors(owner, repo_name)
        if contributors:
            metadata['contributors'] = contributors

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
        """Extract programming languages with percentages."""
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
                    # Get all text content including the percentage
                    lang_text = elem.get_text(strip=True)
                    if lang_text and len(lang_text) < 50:
                        # The text should be like "Python 85.5 percent" or just "Python"
                        languages.append(lang_text)
                if languages:
                    metadata['languages'] = languages
                    if not metadata['language']:
                        # Extract just the language name from the first entry
                        first_lang = languages[0]
                        lang_name = first_lang.split()[0] if first_lang else ''
                        metadata['language'] = lang_name
                        
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
                    href = link.get('href', '')
                    # Extract tag from URL: /releases/tag/V1.0.0 -> V1.0.0
                    tag_match = re.search(r'/releases/tag/([^/]+)', href)
                    if tag_match:
                        tag = tag_match.group(1)
                        # Try to find release date
                        date = None
                        # Method 1: Look for relative-time in broader context
                        section = link.find_parent('section') or link.find_parent('div', class_=re.compile(r'Box|release'))
                        if section:
                            time_elem = section.find('relative-time')
                            if time_elem and time_elem.get('datetime'):
                                date = time_elem.get('datetime').split('T')[0]  # Get YYYY-MM-DD
                        
                        # Method 2: If no date found, fetch the individual release page
                        if not date:
                            release_page_url = urljoin(releases_url, href)
                            release_soup = self.fetch_page(release_page_url, silent=True)
                            if release_soup:
                                time_elem = release_soup.find('relative-time')
                                if time_elem and time_elem.get('datetime'):
                                    date = time_elem.get('datetime').split('T')[0]
                        releases.append({
                            'tag': tag,
                            'version': tag,
                            'url': urljoin(releases_url, href),
                            'date': date
                        })
            
            # If no releases, try tags
            if not releases:
                tags_url = f"{repo_url}/tags"
                soup = self.fetch_page(tags_url)
                if soup:
                    tag_links = soup.find_all('a', href=re.compile(r'/releases/tag/'))
                    for link in tag_links[:10]:
                        href = link.get('href', '')
                        # Extract tag from URL: /releases/tag/V1.0.0 -> V1.0.0
                        tag_match = re.search(r'/releases/tag/([^/]+)', href)
                        if tag_match:
                            tag = tag_match.group(1)
                            releases.append({
                                'tag': tag,
                                'version': tag,
                                'url': urljoin(tags_url, href)
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

    def _fetch_user_profile(self, username: str) -> Optional[Dict]:
        """
        Fetch user profile information from GitHub.
        
        Args:
            username: GitHub username
        
        Returns:
            Dictionary with user profile information or None
        """
        try:
            profile_url = f"https://github.com/{username}"
            soup = self.fetch_page(profile_url)
            if not soup:
                return None
            
            profile_data = {
                'username': username,
                'name': None,
                'email': None,
                'organization': None,
                'location': None,
                'bio': None,
                'website': None,
            }
            
            # Extract full name
            name_elem = soup.find('span', {'itemprop': 'name'})
            if not name_elem:
                name_elem = soup.find('h1', class_='vcard-names')
            if name_elem:
                full_name = name_elem.get_text(strip=True)
                if full_name and full_name != username:
                    profile_data['name'] = full_name
            
            # Extract organization/company
            org_elem = soup.find('span', {'itemprop': 'worksFor'})
            if not org_elem:
                org_elem = soup.find('li', {'itemprop': 'worksFor'})
            if org_elem:
                org_text = org_elem.get_text(strip=True)
                if org_text:
                    profile_data['organization'] = org_text
            
            # Extract location
            loc_elem = soup.find('span', {'itemprop': 'homeLocation'})
            if not loc_elem:
                loc_elem = soup.find('li', {'itemprop': 'homeLocation'})
            if loc_elem:
                location = loc_elem.get_text(strip=True)
                if location:
                    profile_data['location'] = location
            
            # Extract bio
            bio_elem = soup.find('div', {'data-bio-text': True})
            if bio_elem:
                bio = bio_elem.get_text(strip=True)
                if bio:
                    profile_data['bio'] = bio
            
            # Extract website
            website_elem = soup.find('a', {'itemprop': 'url'})
            if website_elem and website_elem.get('href'):
                website = website_elem.get('href')
                if website and not website.startswith('https://github.com'):
                    profile_data['website'] = website
            
            # Extract email from profile (if public)
            email_elem = soup.find('a', {'itemprop': 'email'})
            if not email_elem:
                email_elem = soup.find('a', href=re.compile(r'^mailto:'))
            if email_elem:
                email = email_elem.get('href', '').replace('mailto:', '')
                if email and '@' in email:
                    profile_data['email'] = email
            
            return profile_data
            
        except Exception as e:
            print(f"Error fetching user profile for {username}: {e}")
            return None
    
    def _fetch_commit_info(self, repo_url: str) -> Optional[List[Dict]]:
        """
        Fetch commit information to extract author names and emails.
        
        Args:
            repo_url: Repository URL
        
        Returns:
            List of commit author information or None
        """
        try:
            commits_url = f"{repo_url}/commits"
            soup = self.fetch_page(commits_url)
            if not soup:
                return None
            
            commit_authors = []
            seen_authors = set()
            
            # Find commit author links
            author_links = soup.find_all('a', {'data-hovercard-type': 'user'})
            for link in author_links[:20]:  # Limit to first 20 commits
                username = link.get('href', '').strip('/').split('/')[-1]
                author_name = link.get_text(strip=True)
                
                if username and username not in seen_authors:
                    seen_authors.add(username)
                    commit_authors.append({
                        'username': username,
                        'name': author_name if author_name != username else None
                    })
            
            # Try to get email from commit patches
            # Note: This requires accessing individual commit pages
            # For now, we'll just return the usernames and names
            
            return commit_authors if commit_authors else None
            
        except Exception as e:
            print(f"Error fetching commit info: {e}")
            return None

    def _fetch_repository_dates(self, owner: str, repo_name: str) -> Dict[str, Optional[str]]:
        """
        Fetch repository creation and modification dates from commits page.
        
        Returns:
            Dict with 'date_created' and 'date_modified' keys containing ISO 8601 timestamps
        """
        dates = {
            'date_created': None,
            'date_modified': None
        }
        
        try:
            commits_url = f"https://github.com/{owner}/{repo_name}/commits"
            response = self.session.get(commits_url, timeout=self.timeout)
            
            if response.status_code == 200:
                html = response.text
                
                # Extract ISO 8601 dates from HTML using regex
                # relative-time elements are rendered by JavaScript, so we extract from HTML source
                import re
                date_pattern = r'20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z'
                found_dates = re.findall(date_pattern, html)
                
                if found_dates:
                    # Remove duplicates while preserving order
                    unique_dates = []
                    seen = set()
                    for date in found_dates:
                        if date not in seen:
                            unique_dates.append(date)
                            seen.add(date)
                    
                    if unique_dates:
                        # First unique date is typically the most recent (dateModified)
                        dates['date_modified'] = unique_dates[0]
                        
                        # Last unique date is typically the oldest (dateCreated)
                        dates['date_created'] = unique_dates[-1] if len(unique_dates) > 1 else unique_dates[0]
                
        except Exception as e:
            print(f"Error fetching repository dates: {e}")
        
        return dates
    
    def _fetch_first_commit_date(self, owner: str, repo_name: str, commits_soup: BeautifulSoup) -> Optional[str]:
        """
        Try to fetch the first (oldest) commit date.
        
        This checks if there's pagination and tries to get the last page.
        """
        try:
            # Check if there's pagination
            pagination = commits_soup.find('div', class_='pagination')
            if pagination:
                # If there's pagination, we need to navigate to the last page
                # For simplicity, we'll try to find the "Oldest" button or last page link
                # GitHub doesn't always show this, so we'll use the API approach instead
                pass
            
            # Alternative: Use the GitHub API endpoint (public, no auth needed)
            # Get the first commit from the repository
            api_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"
            headers = {'Accept': 'application/vnd.github.v3+json'}
            
            # Get commits in ascending order (oldest first) with per_page=1
            params = {'per_page': 1, 'sha': 'HEAD'}
            
            # First, get the total number of commits to calculate the last page
            response = self.session.get(api_url, headers=headers, params={'per_page': 1}, timeout=self.timeout)
            
            if response.status_code == 200:
                # Check if there's a Link header with pagination info
                link_header = response.headers.get('Link', '')
                
                # Try to extract the last page number
                import re
                last_page_match = re.search(r'page=(\d+)>; rel="last"', link_header)
                
                if last_page_match:
                    last_page = int(last_page_match.group(1))
                    # Fetch the last page to get the first commit
                    response = self.session.get(api_url, headers=headers, params={'per_page': 1, 'page': last_page}, timeout=self.timeout)
                    
                    if response.status_code == 200:
                        commits = response.json()
                        if commits and len(commits) > 0:
                            # Get the commit date
                            commit_date = commits[0].get('commit', {}).get('committer', {}).get('date')
                            return commit_date
                else:
                    # Only one page of commits, so the last commit on the page is the first commit
                    commits = response.json()
                    if commits and len(commits) > 0:
                        # This is actually the latest commit, we need to get all commits
                        # Let's try a different approach: get commits with per_page=100 and navigate to last
                        pass
            
        except Exception as e:
            print(f"Error fetching first commit date: {e}")
        
        return None

    def _fetch_contributors(self, owner: str, repo_name: str) -> List[Dict]:
        """
        Fetch contributors from GitHub repository page sidebar and enrich with profile data.
        
        Args:
            owner: Repository owner
            repo_name: Repository name
            
        Returns:
            List of contributor dictionaries with enriched profile data
        """
        contributors = []
        repo_url = f"https://github.com/{owner}/{repo_name}"
        
        try:
            soup = self.fetch_page(repo_url)
            if not soup:
                return contributors
            
            # Find contributor links from the sidebar
            # GitHub shows contributors with data-hovercard-type="user" attribute
            contributor_links = soup.find_all('a', {'data-hovercard-type': 'user'})
            
            # Also try to find avatar images with @username alt text
            if not contributor_links:
                avatar_imgs = soup.find_all('img', {'alt': re.compile(r'^@\w+')})
                # Extract usernames from alt text
                for img in avatar_imgs:
                    alt = img.get('alt', '')
                    username = alt.strip('@')
                    if username:
                        # Create a fake link structure for consistency
                        contributor_links.append({'href': f'/{username}'})
            
            seen_usernames = set()
            for link in contributor_links:
                # Handle both BeautifulSoup Tag and dict
                if hasattr(link, 'get'):
                    href = link.get('href', '')
                else:
                    href = link.get('href', '') if isinstance(link, dict) else ''
                
                # Extract username from href
                if href and href.startswith('https://github.com/'):
                    username = href.replace('https://github.com/', '').strip('/')
                elif href and href.startswith('/'):
                    username = href.strip('/')
                else:
                    continue
                
                # Skip if not a simple username (contains /)
                if '/' in username or '?' in username:
                    continue
                
                if username and username not in seen_usernames and len(username) < 40:
                    seen_usernames.add(username)
                    # Fetch profile for each contributor
                    profile = self._fetch_user_profile(username)
                    if profile:
                        contributors.append(profile)
                    
                    # Limit to first 10 contributors to avoid too many requests
                    if len(contributors) >= 10:
                        break
            
            return contributors
            
        except Exception as e:
            print(f"Error fetching contributors: {e}")
            return contributors

    def _fetch_file_list(self, owner: str, repo_name: str) -> Optional[List[str]]:
        """
        Fetch list of files in the repository root.
        
        Args:
            owner: Repository owner
            repo_name: Repository name
            
        Returns:
            List of file paths or None
        """
        try:
            # Try main branch first, then master
            branches = ['main', 'master']
            
            for branch in branches:
                repo_url = f"https://github.com/{owner}/{repo_name}"
                tree_url = f"{repo_url}/tree/{branch}"
                # Use silent=True to avoid 404 errors when trying different branches
                soup = self.fetch_page(tree_url, silent=True)
                
                if not soup:
                    continue
                
                files = []
                
                # Find file links in the file list
                # GitHub uses different selectors, try multiple approaches
                file_links = soup.find_all('a', class_='js-navigation-open')
                
                for link in file_links:
                    file_path = link.get_text(strip=True)
                    if file_path:
                        files.append(file_path)
                
                # Also check for files in common documentation folders
                doc_folders = ['docs', 'doc', 'documentation']
                for folder in doc_folders:
                    folder_url = f"{repo_url}/tree/{branch}/{folder}"
                    folder_soup = self.fetch_page(folder_url, silent=True)
                    if folder_soup:
                        folder_links = folder_soup.find_all('a', class_='js-navigation-open')
                        for link in folder_links:
                            file_name = link.get_text(strip=True)
                            if file_name:
                                files.append(f"{folder}/{file_name}")
                
                if files:
                    return files
            
            return None
            
        except Exception as e:
            print(f"Error fetching file list: {e}")
            return None


    def scrape_repository_fast(self, repo_url: str) -> Dict:
        """
        Extract minimal metadata for fast category detection.
        Only fetches README, description, and topics - skips contributors, commits, etc.

        Args:
            repo_url: GitHub repository URL

        Returns:
            Dictionary containing essential metadata for category detection
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
            'topics': [],
            'keywords': [],
            'languages': [],
            'readme_content': None,
        }

        # Fetch main repository page (fast)
        soup = self.fetch_page(base_url)
        if not soup:
            return metadata

        # Extract only essential info for category detection
        self._extract_basic_info(soup, metadata)
        self._extract_languages(soup, metadata)
        self._extract_topics(soup, metadata)
        
        # Fetch README content (most important for category detection)
        readme_content = self._fetch_readme(base_url, owner, repo_name)
        if readme_content:
            metadata['readme_content'] = readme_content

        return metadata
