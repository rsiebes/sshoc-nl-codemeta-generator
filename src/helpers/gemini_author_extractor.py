"""Gemini API integration for author metadata extraction."""

import json
import os
from typing import Optional, Dict, Any

import requests
from dotenv import load_dotenv
from google import genai

from src.core import get_logger

logger = get_logger(__name__)

# Load environment variables from .env file
load_dotenv()


def _fetch_readme_content(repo_url: str) -> Optional[str]:
    """
    Fetch README.md content from a GitHub repository.

    Args:
        repo_url: The GitHub repository URL

    Returns:
        README content as string, or None if not found
    """
    try:
        # Parse repo URL to get owner and repo
        parts = repo_url.rstrip("/").split("/")
        owner = parts[-2]
        repo = parts[-1]

        # GitHub API endpoint for README
        api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        headers = {"Accept": "application/vnd.github.v3.raw"}

        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            logger.debug(f"Successfully fetched README for {owner}/{repo}")
            return response.text
        else:
            logger.warning(f"README not found for {owner}/{repo} (status: {response.status_code})")
            return None
    except Exception as e:
        logger.warning(f"Error fetching README: {str(e)}")
        return None


def _fetch_contributors(repo_url: str) -> Optional[list]:
    """
    Fetch contributor information from a GitHub repository.

    Args:
        repo_url: The GitHub repository URL

    Returns:
        List of contributors with their information, or None if error
    """
    try:
        # Parse repo URL to get owner and repo
        parts = repo_url.rstrip("/").split("/")
        owner = parts[-2]
        repo = parts[-1]

        # GitHub API endpoint for contributors
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
        headers = {"Accept": "application/vnd.github.v3+json"}

        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            contributors = response.json()
            logger.debug(f"Successfully fetched {len(contributors)} contributors for {owner}/{repo}")
            return contributors
        else:
            logger.warning(f"Contributors not found for {owner}/{repo} (status: {response.status_code})")
            return None
    except Exception as e:
        logger.warning(f"Error fetching contributors: {str(e)}")
        return None


def extract_authors(repo_url: str) -> Optional[Dict[str, Any]]:
    """
    Extract author metadata from a GitHub repository using Google Gemini API.

    Fetches README content and contributor information from GitHub API,
    then uses Gemini to identify and enrich author information.

    Args:
        repo_url: The GitHub repository URL

    Returns:
        Dictionary containing author metadata in CodeMeta 3.1 JSON-LD format, or None if extraction fails
    """
    try:
        # Get API key from environment
        api_key = os.getenv("GOOGLE_GEMINI_API_KEY")

        if not api_key:
            logger.error(
                "GOOGLE_GEMINI_API_KEY not found in environment variables"
            )
            return None

        # Initialize Gemini client
        client = genai.Client(api_key=api_key)

        logger.info(f"GEMINI AUTHOR EXTRACTION: Processing repository URL: {repo_url}")

        # Fetch README content
        readme_content = _fetch_readme_content(repo_url)
        if not readme_content:
            logger.warning(f"Could not fetch README for {repo_url}")
            readme_content = "README not available"

        # Fetch contributors information
        contributors = _fetch_contributors(repo_url)
        if not contributors:
            logger.warning(f"Could not fetch contributors for {repo_url}")
            contributors = []

        # Format contributors information
        contributors_info = "GitHub Contributors:\n"
        for contributor in contributors[:20]:  # Limit to top 20
            contributors_info += f"- {contributor.get('login', 'Unknown')}: {contributor.get('contributions', 0)} commits\n"

        # Prepare the user prompt with README content and contributor information
        user_prompt = f"""Extract author information from this GitHub repository: {repo_url}

README.md Content:
```markdown
{readme_content}
```

{contributors_info}

Instructions:
1. Look for an 'Authors' section in the README.md content above
2. Extract ALL author names listed in that section
3. Also consider the top GitHub contributors listed above
4. For each author name found, search for their ORCID identifier
5. Find their institutional affiliation and the corresponding DBpedia URI
6. Return the complete author information in CodeMeta 3.1 JSON-LD format

Important: Include all authors from the README Authors section, not just commit history."""

        # Call Gemini API with README content and contributor information
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=genai.types.GenerateContentConfig(
                system_instruction="You are a CodeMeta 3.1 expert. Extract author information from GitHub repositories. Always prioritize the 'Authors' section in README.md - this is the most reliable source. For each author name found, lookup their ORCID identifier and affiliation information including DBpedia URIs. Return valid JSON-LD in CodeMeta 3.1 schema format.",
                response_mime_type="application/json",
            ),
            contents=user_prompt,
        )

        # Parse the response
        if response and response.text:
            try:
                # Extract JSON from response
                author_data = json.loads(response.text)
                logger.info(
                    f"Successfully extracted author metadata from {repo_url}"
                )
                logger.debug(f"Author data: {json.dumps(author_data, indent=2)}")
                return author_data
            except json.JSONDecodeError as e:
                logger.warning(
                    f"Failed to parse JSON response from Gemini for {repo_url}: {str(e)}"
                )
                logger.debug(f"Response text: {response.text}")
                return None
        else:
            logger.warning(f"No author metadata extracted from {repo_url}")
            return None

    except Exception as e:
        logger.error(f"Error extracting author metadata from {repo_url}: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return None
