"""
GitHub API Client

Provides methods to fetch repository data using the GitHub REST API.
Handles rate limiting, authentication, and error handling.
"""

import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime


class GitHubAPIClient:
    """Client for interacting with GitHub REST API."""
    
    # GitHub API base URL
    API_BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub API client.
        
        Args:
            token: GitHub personal access token (optional, for higher rate limits)
        """
        self.token = token or os.environ.get('GITHUB_TOKEN')
        self.session = requests.Session()
        
        if self.token:
            self.session.headers.update({
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            })
        else:
            self.session.headers.update({
                'Accept': 'application/vnd.github.v3+json'
            })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a request to GitHub API.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters
        
        Returns:
            Response JSON
        
        Raises:
            requests.HTTPError: If request fails
        """
        url = f"{self.API_BASE_URL}{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"GitHub API request failed: {e}")
    
    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get repository information.
        
        Args:
            owner: Repository owner
            repo: Repository name
        
        Returns:
            Repository data
        """
        return self._make_request(f"/repos/{owner}/{repo}")
    
    def get_contributors(self, owner: str, repo: str, per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Get list of contributors for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            per_page: Number of results per page (max 100)
        
        Returns:
            List of contributor data
        """
        contributors = []
        page = 1
        
        while True:
            data = self._make_request(
                f"/repos/{owner}/{repo}/contributors",
                params={'per_page': per_page, 'page': page}
            )
            
            if not data:
                break
            
            contributors.extend(data)
            
            # Check if there are more pages
            if len(data) < per_page:
                break
            
            page += 1
        
        return contributors
    
    def get_user(self, username: str) -> Dict[str, Any]:
        """
        Get user information.
        
        Args:
            username: GitHub username
        
        Returns:
            User data
        """
        return self._make_request(f"/users/{username}")
    
    def get_commits(self, owner: str, repo: str, per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Get list of commits for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            per_page: Number of results per page (max 100)
        
        Returns:
            List of commit data
        """
        commits = []
        page = 1
        
        while True:
            data = self._make_request(
                f"/repos/{owner}/{repo}/commits",
                params={'per_page': per_page, 'page': page}
            )
            
            if not data:
                break
            
            commits.extend(data)
            
            # Check if there are more pages
            if len(data) < per_page:
                break
            
            page += 1
        
        return commits
    
    def get_issues(self, owner: str, repo: str, state: str = 'all', per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Get list of issues for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state ('open', 'closed', 'all')
            per_page: Number of results per page (max 100)
        
        Returns:
            List of issue data
        """
        issues = []
        page = 1
        
        while True:
            data = self._make_request(
                f"/repos/{owner}/{repo}/issues",
                params={'state': state, 'per_page': per_page, 'page': page}
            )
            
            if not data:
                break
            
            issues.extend(data)
            
            # Check if there are more pages
            if len(data) < per_page:
                break
            
            page += 1
        
        return issues
    
    def get_pull_requests(self, owner: str, repo: str, state: str = 'all', per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Get list of pull requests for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: PR state ('open', 'closed', 'all')
            per_page: Number of results per page (max 100)
        
        Returns:
            List of pull request data
        """
        prs = []
        page = 1
        
        while True:
            data = self._make_request(
                f"/repos/{owner}/{repo}/pulls",
                params={'state': state, 'per_page': per_page, 'page': page}
            )
            
            if not data:
                break
            
            prs.extend(data)
            
            # Check if there are more pages
            if len(data) < per_page:
                break
            
            page += 1
        
        return prs
    
    def get_releases(self, owner: str, repo: str, per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Get list of releases for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            per_page: Number of results per page (max 100)
        
        Returns:
            List of release data
        """
        releases = []
        page = 1
        
        while True:
            data = self._make_request(
                f"/repos/{owner}/{repo}/releases",
                params={'per_page': per_page, 'page': page}
            )
            
            if not data:
                break
            
            releases.extend(data)
            
            # Check if there are more pages
            if len(data) < per_page:
                break
            
            page += 1
        
        return releases
    
    def get_topics(self, owner: str, repo: str) -> List[str]:
        """
        Get topics/tags for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
        
        Returns:
            List of topics
        """
        try:
            data = self._make_request(f"/repos/{owner}/{repo}/topics")
            return data.get('names', [])
        except Exception:
            return []
    
    def get_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """
        Get programming languages used in a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
        
        Returns:
            Dictionary of languages and byte counts
        """
        try:
            return self._make_request(f"/repos/{owner}/{repo}/languages")
        except Exception:
            return {}
    
    def get_rate_limit(self) -> Dict[str, Any]:
        """
        Get current rate limit status.
        
        Returns:
            Rate limit information
        """
        try:
            data = self._make_request("/rate_limit")
            return data.get('rate_limit', {})
        except Exception:
            return {}
