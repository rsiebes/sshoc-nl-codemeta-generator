#!/usr/bin/env python3
"""
CodeMeta property module for extracting keywords from a GitHub repository.

This module extracts keywords from a GitHub repository using multiple strategies:
1. From GitHub repository topics (most reliable)
2. From README.md content (text analysis)
3. From repository description
4. From programming languages detected in the repository
5. From common patterns in file names and directory structure

Keywords are extracted and deduplicated to provide a comprehensive list of
relevant terms that describe the repository.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, List, Set
import re
import json

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.github_api import parse_repository_url, fetch_repository_info, fetch_file_content
from src.utils import normalize_url


# Common programming-related keywords to extract from text
PROGRAMMING_KEYWORDS = {
    "machine learning", "deep learning", "neural network", "tensorflow", "pytorch",
    "data science", "data analysis", "visualization", "analytics",
    "web framework", "api", "rest", "graphql", "microservice",
    "database", "sql", "nosql", "mongodb", "postgresql",
    "cloud", "aws", "azure", "gcp", "kubernetes", "docker", "container",
    "devops", "ci/cd", "continuous integration", "continuous deployment",
    "testing", "unit test", "integration test", "test automation",
    "security", "encryption", "authentication", "authorization",
    "performance", "optimization", "scalability", "distributed",
    "mobile", "ios", "android", "react native",
    "frontend", "backend", "full stack", "web development",
    "game development", "graphics", "3d", "rendering",
    "compiler", "interpreter", "parser", "language",
    "cli", "command line", "terminal", "shell",
    "documentation", "tutorial", "guide", "example",
    "library", "framework", "toolkit", "sdk",
    "open source", "community", "collaboration",
    "monitoring", "logging", "debugging", "profiling",
    "algorithm", "data structure", "pattern", "design pattern",
}

# Common domain-specific keywords
DOMAIN_KEYWORDS = {
    "bioinformatics", "genomics", "biology", "chemistry",
    "physics", "astronomy", "climate", "weather",
    "finance", "trading", "investment", "cryptocurrency",
    "healthcare", "medical", "clinical", "diagnosis",
    "education", "learning", "training", "course",
    "nlp", "natural language", "text processing", "sentiment",
    "computer vision", "image processing", "object detection",
    "audio", "speech", "voice", "music",
    "game", "gaming", "entertainment",
    "social", "social network", "messaging", "communication",
    "e-commerce", "shopping", "marketplace",
    "iot", "internet of things", "embedded", "sensor",
    "robotics", "automation", "control",
    "geospatial", "gis", "mapping", "location",
}

# Combine all keywords
ALL_KEYWORDS = PROGRAMMING_KEYWORDS | DOMAIN_KEYWORDS


def extract_keywords_from_topics(owner: str, repo: str) -> Set[str]:
    """
    Extract keywords from GitHub repository topics.

    GitHub topics are user-defined tags that describe the repository.
    This is the most reliable source of keywords.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Set[str]: A set of keywords extracted from topics.
    """
    try:
        repo_info = fetch_repository_info(owner, repo)
        if not repo_info:
            return set()

        topics = repo_info.get("topics", [])
        if not topics:
            return set()

        # Convert topics to a set and normalize them
        keywords = set()
        for topic in topics:
            if isinstance(topic, str):
                # Clean up the topic (remove hyphens, convert to lowercase)
                cleaned = topic.lower().replace("-", " ").replace("_", " ")
                keywords.add(cleaned)

        return keywords

    except Exception:
        return set()


def extract_keywords_from_description(description: str) -> Set[str]:
    """
    Extract keywords from repository description text.

    This function analyzes the description text to find relevant keywords
    by matching against known programming and domain keywords.

    Args:
        description (str): The repository description text.

    Returns:
        Set[str]: A set of keywords found in the description.
    """
    if not description:
        return set()

    description_lower = description.lower()
    keywords = set()

    # Look for known keywords in the description
    for keyword in ALL_KEYWORDS:
        if keyword in description_lower:
            keywords.add(keyword)

    return keywords


def extract_keywords_from_readme(owner: str, repo: str) -> Set[str]:
    """
    Extract keywords from README.md content.

    This function analyzes the README file to find relevant keywords
    by matching against known programming and domain keywords.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Set[str]: A set of keywords found in the README.
    """
    try:
        # Try to fetch README from different branches
        branches = ["main", "master", "develop"]
        readme_content = None

        for branch in branches:
            readme_content = fetch_file_content(owner, repo, "README.md", branch=branch)
            if readme_content:
                break

        if not readme_content:
            return set()

        readme_lower = readme_content.lower()
        keywords = set()

        # Look for known keywords in the README
        for keyword in ALL_KEYWORDS:
            if keyword in readme_lower:
                keywords.add(keyword)

        return keywords

    except Exception:
        return set()


def extract_keywords_from_languages(owner: str, repo: str) -> Set[str]:
    """
    Extract keywords from programming languages used in the repository.

    This function fetches the programming languages used in the repository
    and returns them as keywords.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Set[str]: A set of programming language keywords.
    """
    try:
        repo_info = fetch_repository_info(owner, repo)
        if not repo_info:
            return set()

        # Get the primary language
        language = repo_info.get("language")
        if language:
            return {language.lower()}

        return set()

    except Exception:
        return set()


def extract_keywords_from_package_json(owner: str, repo: str) -> Set[str]:
    """
    Extract keywords from package.json file (for Node.js projects).

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Set[str]: A set of keywords from package.json.
    """
    try:
        content = fetch_file_content(owner, repo, "package.json")
        if not content:
            return set()

        package_data = json.loads(content)
        keywords = package_data.get("keywords", [])

        if not keywords:
            return set()

        # Convert to set and normalize
        return {k.lower().replace("-", " ").replace("_", " ") for k in keywords if isinstance(k, str)}

    except Exception:
        return set()


def extract_keywords_from_setup_py(owner: str, repo: str) -> Set[str]:
    """
    Extract keywords from setup.py file (for Python projects).

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Set[str]: A set of keywords from setup.py.
    """
    try:
        content = fetch_file_content(owner, repo, "setup.py")
        if not content:
            return set()

        # Look for keywords parameter
        match = re.search(r'keywords\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            keywords_str = match.group(1)
            # Split by comma or space
            keywords = re.split(r'[,\s]+', keywords_str)
            return {k.lower().strip() for k in keywords if k.strip()}

        return set()

    except Exception:
        return set()


def extract_keywords_from_pyproject_toml(owner: str, repo: str) -> Set[str]:
    """
    Extract keywords from pyproject.toml file (for modern Python projects).

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Set[str]: A set of keywords from pyproject.toml.
    """
    try:
        content = fetch_file_content(owner, repo, "pyproject.toml")
        if not content:
            return set()

        # Look for keywords field
        match = re.search(r'keywords\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if match:
            keywords_str = match.group(1)
            # Extract quoted strings
            keywords = re.findall(r'["\']([^"\']+)["\']', keywords_str)
            return {k.lower().strip() for k in keywords if k.strip()}

        return set()

    except Exception:
        return set()


def deduplicate_and_normalize_keywords(keywords: Set[str]) -> List[str]:
    """
    Deduplicate and normalize keywords.

    This function removes duplicates, filters out very short keywords,
    and sorts the results alphabetically.

    Args:
        keywords (Set[str]): A set of keywords to normalize.

    Returns:
        List[str]: A sorted list of normalized keywords.
    """
    # Filter out very short keywords (less than 3 characters) and empty strings
    filtered = {k.strip() for k in keywords if k and len(k.strip()) >= 3}

    # Remove duplicates and sort
    return sorted(list(filtered))


def get(repository_url: str) -> Dict:
    """
    Extract keywords from a GitHub repository.

    This function uses multiple strategies to extract keywords:
    1. From GitHub repository topics (most reliable)
    2. From README.md content
    3. From repository description
    4. From programming languages
    5. From package.json (Node.js projects)
    6. From setup.py (Python projects)
    7. From pyproject.toml (modern Python projects)

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'keywords' property and its value.
              Returns an empty dict if no keywords can be extracted.

    Example:
        >>> result = get("https://github.com/rsiebes/sshoc-nl-codemeta-generator")
        >>> print(result)
        {'keywords': ['codemeta', 'metadata', 'github', 'python']}
    """
    repository_url = normalize_url(repository_url)
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    all_keywords = set()

    # Strategy 1: Extract from GitHub topics (highest priority)
    all_keywords.update(extract_keywords_from_topics(owner, repo))

    # Strategy 2: Extract from repository description
    try:
        repo_info = fetch_repository_info(owner, repo)
        if repo_info and repo_info.get("description"):
            all_keywords.update(extract_keywords_from_description(repo_info.get("description")))
    except Exception:
        pass

    # Strategy 3: Extract from README
    all_keywords.update(extract_keywords_from_readme(owner, repo))

    # Strategy 4: Extract from programming languages
    all_keywords.update(extract_keywords_from_languages(owner, repo))

    # Strategy 5: Extract from package.json
    all_keywords.update(extract_keywords_from_package_json(owner, repo))

    # Strategy 6: Extract from setup.py
    all_keywords.update(extract_keywords_from_setup_py(owner, repo))

    # Strategy 7: Extract from pyproject.toml
    all_keywords.update(extract_keywords_from_pyproject_toml(owner, repo))

    # Deduplicate and normalize
    normalized_keywords = deduplicate_and_normalize_keywords(all_keywords)

    if not normalized_keywords:
        return {}

    return {"keywords": normalized_keywords}


if __name__ == "__main__":
    test_repos = [
        "https://github.com/rsiebes/sshoc-nl-codemeta-generator",
        "https://github.com/openai/gpt-2",
        "https://github.com/tensorflow/tensorflow",
    ]

    for repo_url in test_repos:
        print(f"\nTesting: {repo_url}")
        result = get(repo_url)
        if result:
            print(f"Keywords: {result.get('keywords', [])}")
        else:
            print("No keywords found")
