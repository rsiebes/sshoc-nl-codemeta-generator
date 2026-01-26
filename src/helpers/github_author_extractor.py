"""GitHub API helper to extract unique author information from commit history."""

import json
from typing import Optional, List, Dict, Any
from collections import OrderedDict

import requests

from src.core import get_logger

logger = get_logger(__name__)


def extract_unique_authors(repo_url: str, per_page: int = 50) -> Optional[str]:
    """
    Extract unique author information from GitHub repository commit history.

    Fetches commits from the GitHub API and extracts unique authors based on:
    - GitHub login (if available)
    - Author name (from commit metadata)
    - Author email (from commit metadata)

    Args:
        repo_url: The GitHub repository URL (e.g., https://github.com/jrvosse/amalgame)
        per_page: Number of commits to fetch per page (default: 50, max: 100)

    Returns:
        JSON string containing unique author information, or None if extraction fails

    Example:
        >>> authors_json = extract_unique_authors("https://github.com/jrvosse/amalgame")
        >>> print(authors_json)
        {
            "authors": [
                {
                    "login": "jrvosse",
                    "name": "Jacco van Ossenbruggen",
                    "email": "jacco.van.ossenbruggen@vu.nl"
                },
                ...
            ]
        }
    """
    try:
        # Parse repository URL to get owner and repo name
        # Expected format: https://github.com/owner/repo
        parts = repo_url.rstrip('/').split('/')
        if len(parts) < 2:
            logger.error(f"Invalid GitHub URL format: {repo_url}")
            return None

        owner = parts[-2]
        repo = parts[-1]

        logger.info(f"GITHUB AUTHOR EXTRACTION: Fetching commits for {owner}/{repo}")

        # Build GitHub API URL
        api_url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page={per_page}"

        # Fetch commits from GitHub API
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()

        commits = response.json()

        if not isinstance(commits, list):
            logger.warning(f"Unexpected response format from GitHub API for {owner}/{repo}")
            return None

        # Extract unique authors
        # Use OrderedDict to maintain insertion order and avoid duplicates
        unique_authors = OrderedDict()

        for commit in commits:
            # Get GitHub user info (if available)
            github_author = commit.get('author', {})
            github_login = github_author.get('login') if isinstance(github_author, dict) else None

            # Get commit author info
            commit_author = commit.get('commit', {}).get('author', {})
            author_name = commit_author.get('name')
            author_email = commit_author.get('email')

            if not author_name or not author_email:
                logger.debug(f"Skipping commit with incomplete author info")
                continue

            # Create a unique key based on email (most reliable identifier)
            author_key = author_email.lower()

            # Only add if we haven't seen this author before
            if author_key not in unique_authors:
                author_info = {
                    "name": author_name,
                    "email": author_email,
                }

                # Add login if available
                if github_login:
                    author_info["login"] = github_login

                unique_authors[author_key] = author_info
                logger.debug(f"Found author: {author_name} ({author_email})")

        # Convert to list
        authors_list = list(unique_authors.values())

        if not authors_list:
            logger.warning(f"No authors found in commit history for {owner}/{repo}")
            return None

        # Create result JSON
        result = {
            "repository": f"{owner}/{repo}",
            "authors": authors_list,
            "total_unique_authors": len(authors_list),
        }

        result_json = json.dumps(result, indent=2)
        logger.info(
            f"Successfully extracted {len(authors_list)} unique authors from {owner}/{repo}"
        )
        logger.debug(f"Authors JSON: {result_json}")

        return result_json

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching commits from GitHub API: {str(e)}")
        return None
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error(f"Error parsing GitHub API response: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error extracting authors from {repo_url}: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return None
