"""
GitHub Contributors Scraper Module

Scrapes contributor information from GitHub repository pages using web scraping.
Works with the GitHub web interface without relying on the API.

Strategies:
1. Scrape the repository main page for contributor links in sidebar
2. Scrape the contributors graph page for detailed contributor information
3. Parse commit history from the repository to extract committer information
4. Extract contributor mentions from README and documentation
"""

import re
import sys
import asyncio
from typing import Dict, List, Optional, Set, Tuple
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Optional Playwright import for JavaScript rendering
async_playwright = None

def _check_playwright_available():
    """Check if Playwright is available at runtime."""
    try:
        from playwright.async_api import async_playwright as pw
        return True, pw
    except ImportError:
        return False, None

def _get_playwright():
    """Get Playwright async_playwright function if available."""
    global async_playwright
    if async_playwright is None:
        available, async_playwright = _check_playwright_available()
    return async_playwright

def is_playwright_available():
    """Check if Playwright is available (dynamic check)."""
    try:
        import playwright
        return True
    except ImportError:
        return False


class GitHubContributorsScraper:
    """Scrapes GitHub repository contributors using web scraping only."""

    def __init__(self, timeout: int = 10):
        """
        Initialize the contributors scraper.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_contributors(self, owner: str, repo_name: str) -> List[Dict[str, str]]:
        """
        Scrape contributors from a GitHub repository.

        Uses multiple strategies to extract contributor information:
        1. Main repository page sidebar
        2. Contributors graph page
        3. Commit history
        4. README mentions

        Args:
            owner: Repository owner
            repo_name: Repository name

        Returns:
            List of contributor dictionaries with username and name
        """
        contributors = {}  # Use dict to avoid duplicates (keyed by username)

        # Strategy 1: Scrape main repository page
        main_contributors = self._scrape_main_page(owner, repo_name)
        for contrib in main_contributors:
            username = contrib.get('username', '').lower()
            if username:
                contributors[username] = contrib

        # Strategy 2: Scrape contributors graph page
        graph_contributors = self._scrape_contributors_graph(owner, repo_name)
        for contrib in graph_contributors:
            username = contrib.get('username', '').lower()
            if username:
                # Merge with existing data, preferring more complete info
                if username in contributors:
                    # Merge the data
                    contributors[username].update({k: v for k, v in contrib.items() if v})
                else:
                    contributors[username] = contrib

        # Strategy 3: Scrape commit history
        commit_contributors = self._scrape_commit_history(owner, repo_name)
        for contrib in commit_contributors:
            username = contrib.get('username', '').lower()
            if username:
                if username in contributors:
                    contributors[username].update({k: v for k, v in contrib.items() if v})
                else:
                    contributors[username] = contrib

        # Strategy 4: Scrape pull requests
        pr_contributors = self._scrape_pull_requests(owner, repo_name)
        for contrib in pr_contributors:
            username = contrib.get('username', '').lower()
            if username:
                if username in contributors:
                    contributors[username].update({k: v for k, v in contrib.items() if v})
                else:
                    contributors[username] = contrib

        # Strategy 5: Scrape issues
        issue_contributors = self._scrape_issues(owner, repo_name)
        for contrib in issue_contributors:
            username = contrib.get('username', '').lower()
            if username:
                if username in contributors:
                    contributors[username].update({k: v for k, v in contrib.items() if v})
                else:
                    contributors[username] = contrib

        return list(contributors.values())

    def _scrape_main_page(self, owner: str, repo_name: str) -> List[Dict[str, str]]:
        """
        Scrape contributors from the main repository page.

        Args:
            owner: Repository owner
            repo_name: Repository name

        Returns:
            List of contributor dictionaries
        """
        contributors = []
        repo_url = f"https://github.com/{owner}/{repo_name}"

        try:
            # Use Playwright to render JavaScript content
            soup = self._fetch_page(repo_url, use_playwright=True)
            if not soup:
                return contributors

            # Look for contributor links with data-hovercard-type="user"
            user_links = soup.find_all('a', {'data-hovercard-type': 'user'})

            seen_usernames = set()
            for link in user_links:
                href = link.get('href', '')
                # Accept both relative paths (/username) and absolute URLs (https://github.com/username)
                if not href or (not href.startswith('/') and not href.startswith('http')):
                    continue

                # Extract username from href (e.g., "/jgarciab" or "https://github.com/jgarciab")
                if href.startswith('http'):
                    # Full URL
                    username = href.rstrip('/').split('/')[-1]
                else:
                    # Relative path
                    username = href.strip('/').split('/')[-1]

                # Skip non-usernames (e.g., login, signup)
                if not username or username in ['login', 'signup', 'search', 'notifications']:
                    continue

                if username not in seen_usernames:
                    seen_usernames.add(username)
                    
                    # Try to get display name from parent element
                    display_name = ''
                    parent = link.parent
                    if parent:
                        # Look for span with display name (usually the second span)
                        spans = parent.find_all('span', recursive=False)
                        if len(spans) > 1:
                            # The second span usually contains the display name
                            display_name = spans[-1].get_text(strip=True)
                        elif len(spans) == 1:
                            # If only one span, get all text from parent except username
                            parent_text = parent.get_text(strip=True)
                            # Remove username from parent text
                            display_name = parent_text.replace(username, '').strip()
                    
                    # Fallback to link text or title
                    if not display_name:
                        display_name = link.get_text(strip=True)
                    if not display_name:
                        display_name = link.get('title', '')

                    contributors.append({
                        'username': username,
                        'name': display_name or username,
                        'url': f"https://github.com/{username}",
                        'source': 'main_page'
                    })

        except Exception as e:
            print(f"Error scraping main page: {e}", file=sys.stderr)
            sys.stderr.flush()

        return contributors

    def _scrape_contributors_graph(self, owner: str, repo_name: str) -> List[Dict[str, str]]:
        """
        Scrape contributors from the GitHub contributors graph page.

        The page is dynamically rendered but contains contributor information
        in data attributes and HTML structure.

        Args:
            owner: Repository owner
            repo_name: Repository name

        Returns:
            List of contributor dictionaries
        """
        contributors = []
        graph_url = f"https://github.com/{owner}/{repo_name}/graphs/contributors"

        try:
            soup = self._fetch_page(graph_url)
            if not soup:
                return contributors

            # Strategy 1: Look for user profile links
            # The page contains links like /username with contributor info
            user_links = soup.find_all('a', href=re.compile(r'^/[a-zA-Z0-9_-]+/?$'))

            seen_usernames = set()
            for link in user_links:
                href = link.get('href', '')
                # Accept both relative paths (/username) and absolute URLs (https://github.com/username)
                if not href or (not href.startswith('/') and not href.startswith('http')):
                    continue

                username = href.strip('/').split('/')[0]

                # Skip non-usernames
                if not username or username in ['login', 'signup', 'search', 'notifications', 'settings']:
                    continue

                # Skip if already seen
                if username in seen_usernames:
                    continue

                seen_usernames.add(username)

                # Get display name from link text or nearby elements
                display_name = link.get_text(strip=True)
                
                # Try to extract full name from nearby elements
                parent = link.parent
                if parent:
                    # Look for text nodes near the link
                    parent_text = parent.get_text(strip=True)
                    # Extract name if it's in parentheses or after username
                    match = re.search(rf'{re.escape(username)}\s+(.+?)(?:\s+\d+\s+contributions?)?$', parent_text)
                    if match:
                        display_name = match.group(1).strip()

                if not display_name:
                    display_name = username

                contributors.append({
                    'username': username,
                    'name': display_name,
                    'url': f"https://github.com/{username}",
                    'source': 'contributors_graph'
                })

            # Strategy 2: Look for data attributes containing contributor info
            # GitHub may store contributor data in data attributes
            elements_with_data = soup.find_all(attrs={'data-contributor': True})
            for elem in elements_with_data:
                data = elem.get('data-contributor', '')
                if data:
                    # Parse contributor data if available
                    username = elem.get('data-username', '')
                    if username and username not in seen_usernames:
                        seen_usernames.add(username)
                        contributors.append({
                            'username': username,
                            'name': elem.get('data-name', username),
                            'url': f"https://github.com/{username}",
                            'source': 'contributors_graph_data'
                        })

        except Exception as e:
            print(f"Error scraping contributors graph: {e}", file=sys.stderr)
            sys.stderr.flush()

        return contributors

    def _scrape_commit_history(self, owner: str, repo_name: str) -> List[Dict[str, str]]:
        """
        Scrape contributors from the commit history page.

        Extracts committer information from the commits page.

        Args:
            owner: Repository owner
            repo_name: Repository name

        Returns:
            List of contributor dictionaries
        """
        contributors = []
        commits_url = f"https://github.com/{owner}/{repo_name}/commits"

        try:
            soup = self._fetch_page(commits_url)
            if not soup:
                return contributors

            # Look for commit author links
            # Format: /username or href="/username"
            author_links = soup.find_all('a', href=re.compile(r'^/[a-zA-Z0-9_-]+/?$'))

            seen_usernames = set()
            for link in author_links:
                href = link.get('href', '')
                if not href or (not href.startswith('/') and not href.startswith('http')):
                    continue

                username = href.strip('/').split('/')[0]

                # Skip non-usernames
                if not username or username in ['login', 'signup', 'search', 'notifications', 'settings']:
                    continue

                if username not in seen_usernames:
                    seen_usernames.add(username)

                    display_name = link.get_text(strip=True)
                    if not display_name:
                        display_name = username

                    contributors.append({
                        'username': username,
                        'name': display_name,
                        'url': f"https://github.com/{username}",
                        'source': 'commit_history'
                    })

        except Exception as e:
            print(f"Error scraping commit history: {e}", file=sys.stderr)
            sys.stderr.flush()

        return contributors

    def _fetch_page(self, url: str, use_playwright: bool = False) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a GitHub page.

        Args:
            url: URL to fetch
            use_playwright: If True, use Playwright to render JavaScript content

        Returns:
            BeautifulSoup object or None if fetch fails
        """
        if use_playwright:
            return self._fetch_page_with_playwright(url)
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}", file=sys.stderr)
            sys.stderr.flush()
            return None

    def _fetch_page_with_playwright(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a GitHub page using Playwright for JavaScript rendering.

        Args:
            url: URL to fetch

        Returns:
            BeautifulSoup object or None if fetch fails
        """
        if not is_playwright_available():
            print(f"Warning: Playwright not available, falling back to regular HTTP request", file=sys.stderr)
            sys.stderr.flush()
            return self._fetch_page(url, use_playwright=False)
        
        try:
            # Run the async function
            html_content = asyncio.run(self._async_fetch_with_playwright(url))
            if html_content:
                return BeautifulSoup(html_content, 'html.parser')
            return None
        except Exception as e:
            print(f"Error fetching {url} with Playwright: {e}", file=sys.stderr)
            sys.stderr.flush()
            # Fallback to regular HTTP request
            return self._fetch_page(url, use_playwright=False)

    async def _async_fetch_with_playwright(self, url: str) -> Optional[str]:
        """
        Async function to fetch page content using Playwright.

        Args:
            url: URL to fetch

        Returns:
            HTML content or None if fetch fails
        """
        if not is_playwright_available():
            return None
        
        try:
            from playwright.async_api import async_playwright as pw
            async with pw() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                try:
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                    await page.wait_for_timeout(1000)
                    html_content = await page.content()
                    return html_content
                finally:
                    await browser.close()
        except Exception as e:
            print(f"Playwright error for {url}: {e}", file=sys.stderr)
            sys.stderr.flush()
            return None



    def _scrape_pull_requests(self, owner: str, repo_name: str) -> List[Dict[str, str]]:
        """
        Scrape contributors from pull requests.

        Args:
            owner: Repository owner
            repo_name: Repository name

        Returns:
            List of contributor dictionaries
        """
        contributors = []
        pr_url = f"https://github.com/{owner}/{repo_name}/pulls"

        try:
            soup = self._fetch_page(pr_url)
            if not soup:
                return contributors

            # Look for PR author links
            author_links = soup.find_all('a', href=re.compile(r'^/[a-zA-Z0-9_-]+/?$'))

            seen_usernames = set()
            for link in author_links:
                href = link.get('href', '')
                if not href or (not href.startswith('/') and not href.startswith('http')):
                    continue

                username = href.strip('/').split('/')[0]

                # Skip non-usernames
                if not username or username in ['login', 'signup', 'search', 'notifications', 'settings']:
                    continue

                if username not in seen_usernames:
                    seen_usernames.add(username)

                    display_name = link.get_text(strip=True)
                    if not display_name:
                        display_name = username

                    contributors.append({
                        'username': username,
                        'name': display_name,
                        'url': f"https://github.com/{username}",
                        'source': 'pull_requests'
                    })

        except Exception as e:
            print(f"Error scraping pull requests: {e}", file=sys.stderr)
            sys.stderr.flush()

        return contributors

    def _scrape_issues(self, owner: str, repo_name: str) -> List[Dict[str, str]]:
        """
        Scrape contributors from issues.

        Args:
            owner: Repository owner
            repo_name: Repository name

        Returns:
            List of contributor dictionaries
        """
        contributors = []
        issues_url = f"https://github.com/{owner}/{repo_name}/issues"

        try:
            soup = self._fetch_page(issues_url)
            if not soup:
                return contributors

            # Look for issue author links
            author_links = soup.find_all('a', href=re.compile(r'^/[a-zA-Z0-9_-]+/?$'))

            seen_usernames = set()
            for link in author_links:
                href = link.get('href', '')
                if not href or (not href.startswith('/') and not href.startswith('http')):
                    continue

                username = href.strip('/').split('/')[0]

                # Skip non-usernames
                if not username or username in ['login', 'signup', 'search', 'notifications', 'settings']:
                    continue

                if username not in seen_usernames:
                    seen_usernames.add(username)

                    display_name = link.get_text(strip=True)
                    if not display_name:
                        display_name = username

                    contributors.append({
                        'username': username,
                        'name': display_name,
                        'url': f"https://github.com/{username}",
                        'source': 'issues'
                    })

        except Exception as e:
            print(f"Error scraping issues: {e}", file=sys.stderr)
            sys.stderr.flush()

        return contributors

    def scrape_user_profile(self, username: str) -> Optional[Dict[str, str]]:
        """
        Scrape user profile information from GitHub.

        Args:
            username: GitHub username

        Returns:
            Dictionary with user profile information or None
        """
        profile_url = f"https://github.com/{username}"

        try:
            soup = self._fetch_page(profile_url)
            if not soup:
                return None

            profile = {
                'username': username,
                'url': profile_url
            }

            # Extract full name
            name_elem = soup.find('span', {'class': re.compile(r'.*\bp-nickname\b.*')})
            if name_elem:
                profile['name'] = name_elem.get_text(strip=True)

            # Extract bio/description
            bio_elem = soup.find('div', {'class': re.compile(r'.*\bp-note\b.*')})
            if bio_elem:
                profile['bio'] = bio_elem.get_text(strip=True)

            # Extract email if public
            email_elem = soup.find('a', {'href': re.compile(r'^mailto:')})
            if email_elem:
                profile['email'] = email_elem.get_text(strip=True)

            # Extract company
            company_elem = soup.find('span', {'class': re.compile(r'.*\bp-org\b.*')})
            if company_elem:
                profile['company'] = company_elem.get_text(strip=True)

            # Extract location
            location_elem = soup.find('span', {'class': re.compile(r'.*\bp-label\b.*')})
            if location_elem:
                profile['location'] = location_elem.get_text(strip=True)

            return profile

        except Exception as e:
            print(f"Error scraping user profile {username}: {e}", file=sys.stderr)
            sys.stderr.flush()
            return None
