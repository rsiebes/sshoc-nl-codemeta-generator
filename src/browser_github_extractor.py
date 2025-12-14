"""
Browser-based GitHub repository data extraction.

This module extracts metadata from GitHub repositories by visiting the web pages
directly, avoiding the need for GitHub API authentication.
"""

import re
from typing import Optional, Dict, List, Any
from pathlib import Path


def extract_github_metadata(markdown_content: str, repo_url: str) -> Dict[str, Any]:
    """
    Extract GitHub repository metadata from the markdown content of a GitHub page.
    
    Args:
        markdown_content (str): The markdown content extracted from the GitHub page
        repo_url (str): The GitHub repository URL
        
    Returns:
        Dict[str, Any]: Extracted metadata
    """
    metadata = {
        'url': repo_url,
        'codeRepository': repo_url,
    }
    
    # Extract repository name from URL
    parts = repo_url.rstrip('/').split('/')
    if len(parts) >= 2:
        metadata['name'] = parts[-1]
        metadata['owner'] = parts[-2]
    
    # Extract description from the "About" section
    description = extract_description(markdown_content)
    if description:
        metadata['description'] = description
    
    # Extract programming languages
    languages = extract_programming_languages(markdown_content)
    if languages:
        metadata['programmingLanguage'] = languages
    
    # Extract license information
    license_info = extract_license(markdown_content)
    if license_info:
        metadata['license'] = license_info
    
    # Extract topics/keywords
    topics = extract_topics(markdown_content)
    if topics:
        metadata['keywords'] = topics
    
    # Extract repository statistics
    stats = extract_repository_stats(markdown_content)
    metadata.update(stats)
    
    return metadata


def extract_description(markdown_content: str) -> Optional[str]:
    """
    Extract the repository description from the About section.
    
    Args:
        markdown_content (str): The markdown content from GitHub page
        
    Returns:
        Optional[str]: The description or None
    """
    # Try to extract from the first paragraph of README (before any code blocks)
    readme_match = re.search(r'^# .+?\n\n(.+?)(?:\n\n```|\n\n#|\n\n## )', markdown_content, re.MULTILINE | re.DOTALL)
    if readme_match:
        first_para = readme_match.group(1).strip()
        # Get first sentence or first 200 chars
        sentences = first_para.split('.')
        if sentences:
            description = sentences[0].strip()
            if len(description) > 10:
                return description + '.'
    
    # Look for the About section
    about_match = re.search(r'## About\n\n(.+?)(?:\n\n##|\Z)', markdown_content, re.DOTALL)
    if about_match:
        description = about_match.group(1).strip()
        # Filter out "No description, website, or topics provided" placeholder
        if description and not description.startswith('No description') and len(description) > 10:
            return description[:200]
    
    return None


def extract_programming_languages(markdown_content: str) -> Optional[List[str]]:
    """
    Extract programming languages from the Languages section.
    
    Args:
        markdown_content (str): The markdown content from GitHub page
        
    Returns:
        Optional[List[str]]: List of programming languages or None
    """
    languages = []
    
    # Look for language percentages like "Python 95.7%"
    language_pattern = r'\*   \[([A-Za-z#\+]+)\s+[\d.]+%\]'
    matches = re.findall(language_pattern, markdown_content)
    
    if matches:
        return list(set(matches))  # Remove duplicates
    
    # Alternative pattern for languages section
    lang_section = re.search(r'## Languages\n\n(.+?)(?:\n\n##|\Z)', markdown_content, re.DOTALL)
    if lang_section:
        lang_text = lang_section.group(1)
        # Extract language names
        lang_matches = re.findall(r'\[([A-Za-z#\+]+)\s+', lang_text)
        if lang_matches:
            return list(set(lang_matches))
    
    return None


def extract_license(markdown_content: str) -> Optional[Dict[str, str]]:
    """
    Extract license information.
    
    Args:
        markdown_content (str): The markdown content from GitHub page
        
    Returns:
        Optional[Dict[str, str]]: License information or None
    """
    # Look for MIT, Apache, GPL, etc. - prioritize exact matches
    if re.search(r'\bMIT\s+License\b', markdown_content):
        return {
            'name': 'MIT License',
            'url': 'https://opensource.org/licenses/MIT'
        }
    elif re.search(r'\bApache\s+License\s+2\.0\b', markdown_content):
        return {
            'name': 'Apache License 2.0',
            'url': 'https://opensource.org/licenses/Apache-2.0'
        }
    elif re.search(r'\bGPL\b', markdown_content):
        return {
            'name': 'GNU General Public License',
            'url': 'https://www.gnu.org/licenses/'
        }
    elif re.search(r'\bBSD\b', markdown_content):
        return {
            'name': 'BSD License',
            'url': 'https://opensource.org/licenses/BSD-3-Clause'
        }
    
    return None


def extract_topics(markdown_content: str) -> Optional[List[str]]:
    """
    Extract topics/keywords from the repository.
    
    Args:
        markdown_content (str): The markdown content from GitHub page
        
    Returns:
        Optional[List[str]]: List of topics or None
    """
    topics = []
    
    # Look for topics in the About section
    topics_match = re.search(r'Topics?\n\n(.+?)(?:\n\n|## |\Z)', markdown_content, re.DOTALL)
    if topics_match:
        topics_text = topics_match.group(1)
        # Extract topic links - look for patterns like [topic]
        topic_links = re.findall(r'\[([a-z0-9\-_]+)\]', topics_text, re.IGNORECASE)
        if topic_links:
            topics.extend(topic_links)
    
    # Extract from project description and README
    keywords = set()
    
    # Common keywords from project descriptions
    keyword_patterns = [
        (r'machine learning', 'machine-learning'),
        (r'deep learning', 'deep-learning'),
        (r'neural network', 'neural-network'),
        (r'web framework', 'web-framework'),
        (r'web application', 'web-application'),
        (r'web server', 'web-server'),
        (r'data analysis', 'data-analysis'),
        (r'data processing', 'data-processing'),
        (r'data visualization', 'data-visualization'),
        (r'REST API', 'rest-api'),
        (r'GraphQL', 'graphql'),
        (r'database', 'database'),
        (r'testing', 'testing'),
        (r'CI/CD', 'ci-cd'),
        (r'DevOps', 'devops'),
        (r'authentication', 'authentication'),
        (r'security', 'security'),
        (r'documentation', 'documentation'),
    ]
    
    for pattern, keyword in keyword_patterns:
        if re.search(pattern, markdown_content, re.IGNORECASE):
            keywords.add(keyword)
    
    if keywords:
        topics.extend(list(keywords))
    
    return list(set(topics)) if topics else None


def extract_repository_stats(markdown_content: str) -> Dict[str, Any]:
    """
    Extract repository statistics (stars, forks, commits, etc.).
    
    Args:
        markdown_content (str): The markdown content from GitHub page
        
    Returns:
        Dict[str, Any]: Repository statistics
    """
    stats = {}
    
    # Extract star count - look for "Star 0" or "Star 123" pattern
    star_match = re.search(r'\bStar\s+(\d+)\b', markdown_content)
    if star_match:
        stats['stars'] = int(star_match.group(1))
    
    # Extract fork count - look for "Fork 2" pattern
    fork_match = re.search(r'\bFork\s+(\d+)\b', markdown_content)
    if fork_match:
        stats['forks'] = int(fork_match.group(1))
    
    # Extract commit count - look for "30 Commits" pattern
    commit_match = re.search(r'(\d+)\s+Commits?\b', markdown_content)
    if commit_match:
        stats['commits'] = int(commit_match.group(1))
    
    # Extract branch count - look for "2 Branches" pattern
    branch_match = re.search(r'(\d+)\s+Branches?\b', markdown_content)
    if branch_match:
        stats['branches'] = int(branch_match.group(1))
    
    # Extract release count
    release_match = re.search(r'(\d+)\s+releases?\b', markdown_content)
    if release_match:
        stats['releases'] = int(release_match.group(1))
    
    return stats


def extract_readme_content(markdown_content: str) -> Optional[str]:
    """
    Extract the README content from the markdown.
    
    Args:
        markdown_content (str): The markdown content from GitHub page
        
    Returns:
        Optional[str]: The README content or None
    """
    # Find the main content between title and About section
    readme_match = re.search(r'^# .+?\n\n(.*?)(?:\n\n## About|\Z)', markdown_content, re.MULTILINE | re.DOTALL)
    if readme_match:
        return readme_match.group(1).strip()
    
    return None


def extract_contributors(markdown_content: str) -> Optional[List[str]]:
    """
    Extract contributor names from the markdown.
    
    Args:
        markdown_content (str): The markdown content from GitHub page
        
    Returns:
        Optional[List[str]]: List of contributor names or None
    """
    contributors = []
    
    # Look for contributor section
    contrib_match = re.search(r'## Contributors?\n\n(.+?)(?:\n\n##|\Z)', markdown_content, re.DOTALL)
    if contrib_match:
        contrib_text = contrib_match.group(1)
        # Extract names from links like [name](url)
        names = re.findall(r'\[([^\]]+)\]', contrib_text)
        contributors.extend(names)
    
    # Look for author mentions in README
    author_match = re.search(r'(?:Author|Created by|Maintained by):\s*([^\n]+)', markdown_content, re.IGNORECASE)
    if author_match:
        author = author_match.group(1).strip()
        contributors.append(author)
    
    return list(set(contributors)) if contributors else None
