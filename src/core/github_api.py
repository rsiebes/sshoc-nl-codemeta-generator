"""GitHub API interactions for fetching repository metadata."""

import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from .errors import InvalidRepositoryError, RepositoryNotFoundError, GitHubAPIError
from .logger import get_logger
from .rate_limiter import RateLimiter

logger = get_logger(__name__)


class GitHubAPI:
    """Class for interacting with the GitHub API."""

    BASE_URL = "https://api.github.com"
    REPO_URL_PATTERN = r"https://github\.com/([^/]+)/([^/]+)(?:\.git)?/?$"

    def __init__(self, wait_on_rate_limit: bool = True):
        """Initialize GitHub API client.
        
        Args:
            wait_on_rate_limit: If True, wait when rate limit is hit; if False, raise error
        """
        try:
            import requests
            self.requests = requests
        except ImportError:
            raise GitHubAPIError(
                "requests library is required. Install it with: pip install requests"
            )
        
        self.rate_limiter = RateLimiter(
            api_name="github",
            wait_on_limit=wait_on_rate_limit
        )

    def parse_repo_url(self, url: str) -> tuple[str, str]:
        """
        Parse GitHub repository URL to extract owner and repo name.

        Args:
            url: GitHub repository URL

        Returns:
            Tuple of (owner, repo_name)

        Raises:
            InvalidRepositoryError: If URL is invalid
        """
        match = re.match(self.REPO_URL_PATTERN, url)
        if not match:
            raise InvalidRepositoryError(
                f"Invalid GitHub repository URL: {url}. "
                "Expected format: https://github.com/owner/repo"
            )

        owner, repo = match.groups()
        return owner, repo

    def get_repository_data(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Fetch repository data from GitHub API.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Dictionary containing repository data

        Raises:
            RepositoryNotFoundError: If repository is not found
            GitHubAPIError: If there is an API error
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        endpoint = f"repos/{owner}/{repo}"

        logger.debug(f"Fetching repository data from: {url}")

        try:
            # Check rate limit before making request
            self.rate_limiter.wait_if_needed(endpoint)
            
            response = self.requests.get(url, timeout=10)
            
            # Record rate limit info from response headers
            self.rate_limiter.record_request(endpoint, dict(response.headers))

            if response.status_code == 404:
                raise RepositoryNotFoundError(
                    f"Repository not found: {owner}/{repo}"
                )

            if response.status_code != 200:
                raise GitHubAPIError(
                    f"GitHub API error: {response.status_code} - {response.reason}"
                )

            data = response.json()
            logger.debug(f"Successfully fetched repository data for {owner}/{repo}")
            
            # Log rate limit status
            status = self.rate_limiter.get_status(endpoint)
            if "rate_limit_info" in status:
                logger.debug(f"GitHub rate limit status: {status['rate_limit_info']}")
            
            return data

        except self.requests.exceptions.Timeout:
            raise GitHubAPIError(f"Timeout while fetching repository data for {owner}/{repo}")
        except self.requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Error fetching repository data: {str(e)}")

    def get_repository_info(self, repo_url: str) -> Dict[str, Any]:
        """
        Get complete repository information from GitHub URL.

        Args:
            repo_url: GitHub repository URL

        Returns:
            Dictionary containing repository information

        Raises:
            InvalidRepositoryError: If URL is invalid
            RepositoryNotFoundError: If repository is not found
            GitHubAPIError: If there is an API error
        """
        owner, repo = self.parse_repo_url(repo_url)
        logger.info(f"Fetching repository information for {owner}/{repo}")

        repo_data = self.get_repository_data(owner, repo)

        return {
            "owner": owner,
            "repo": repo,
            "url": repo_url,
            "data": repo_data
        }
