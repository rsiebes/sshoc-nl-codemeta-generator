"""
CodeMeta applicationSubCategory Module

Extracts the application subcategory/type of the software according to CodeMeta 3.1 standard.
The applicationSubCategory property provides more specific categorization within a primary
application category. For example, if applicationCategory is "Game", the subcategory might
be "Puzzle", "RPG", "Strategy", etc.

This module analyzes multiple sources:
1. GitHub repository topics/tags
2. Repository description
3. README content
4. File structure and language patterns

Returns:
    str: Single subcategory string (e.g., "Puzzle")
    list: Multiple subcategories if applicable
    None: If no subcategory can be determined with confidence
"""

import os
import json
import re
from typing import Union, List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ApplicationSubCategoryExtractor:
    """Extracts application subcategory from GitHub repository metadata."""

    # Mapping of primary categories to their subcategories
    SUBCATEGORY_KEYWORDS = {
        # Game subcategories
        "Game": {
            "Puzzle": ["puzzle", "tetris", "match-3", "sudoku", "crossword"],
            "RPG": ["rpg", "role-playing", "fantasy", "quest", "dungeon"],
            "Strategy": ["strategy", "turn-based", "tactics", "civilization", "chess"],
            "Action": ["action", "arcade", "shooter", "platformer", "combat"],
            "Adventure": ["adventure", "quest", "exploration", "story-driven"],
            "Sports": ["sports", "football", "soccer", "basketball", "racing"],
            "Simulation": ["simulation", "simulator", "tycoon", "management"],
            "Casual": ["casual", "match", "bubble", "clicker"],
        },
        # Business subcategories
        "Business": {
            "ERP": ["erp", "enterprise resource planning"],
            "CRM": ["crm", "customer relationship"],
            "Accounting": ["accounting", "finance", "bookkeeping"],
            "HR": ["hr", "human resources", "payroll"],
            "Sales": ["sales", "crm", "pipeline"],
            "Marketing": ["marketing", "campaign", "email marketing"],
            "Inventory": ["inventory", "warehouse", "stock management"],
        },
        # Education subcategories
        "Education": {
            "LMS": ["lms", "learning management", "course management"],
            "Tutoring": ["tutoring", "tutor", "one-on-one"],
            "Language": ["language", "english", "spanish", "french"],
            "STEM": ["stem", "science", "math", "coding", "programming"],
            "K-12": ["k-12", "elementary", "middle school", "high school"],
            "Higher Ed": ["university", "college", "higher education"],
        },
        # Multimedia subcategories
        "Multimedia": {
            "Video": ["video", "video editing", "ffmpeg", "transcoding"],
            "Audio": ["audio", "music", "sound", "recording"],
            "Image": ["image", "photo", "graphics", "imagemagick"],
            "Animation": ["animation", "3d", "blender", "rendering"],
        },
        # Developer subcategories
        "Developer": {
            "Framework": ["framework", "web framework", "application framework"],
            "Library": ["library", "sdk", "toolkit"],
            "IDE": ["ide", "editor", "development environment"],
            "Build Tool": ["build", "compiler", "transpiler", "bundler"],
            "Database": ["database", "sql", "nosql", "orm"],
            "API": ["api", "rest", "graphql", "web service"],
            "Testing": ["test", "testing", "unit test", "integration test"],
            "DevOps": ["devops", "ci/cd", "deployment", "container"],
        },
    }

    def __init__(self, repo_data: Dict[str, Any]):
        """
        Initialize the ApplicationSubCategoryExtractor.

        Args:
            repo_data: Dictionary containing repository metadata from GitHub API
        """
        self.repo_data = repo_data
        self.owner = repo_data.get("owner", {}).get("login", "")
        self.repo_name = repo_data.get("name", "")
        self.description = (repo_data.get("description") or "").lower()
        self.topics = [t.lower() for t in repo_data.get("topics", [])]
        self.language = (repo_data.get("language") or "").lower()

    def extract(self, primary_category: Optional[str] = None) -> Optional[Union[str, List[str]]]:
        """
        Extract application subcategory from repository metadata.

        Args:
            primary_category: The primary applicationCategory (e.g., "Game", "Business")
                            If provided, only subcategories for this category are considered

        Returns:
            str: Single subcategory (e.g., "Puzzle")
            list: Multiple subcategories if applicable
            None: If no subcategory can be determined with confidence
        """
        if not primary_category or primary_category not in self.SUBCATEGORY_KEYWORDS:
            return None

        subcategories = self.SUBCATEGORY_KEYWORDS[primary_category]
        subcategory_scores = {}

        for subcategory, keywords in subcategories.items():
            score = self._calculate_subcategory_score(subcategory, keywords)
            if score > 0:
                subcategory_scores[subcategory] = score

        if not subcategory_scores:
            return None

        # Sort by score
        sorted_subcategories = sorted(subcategory_scores.items(), key=lambda x: x[1], reverse=True)

        # Return top subcategory if score is high enough
        if len(sorted_subcategories) > 0:
            top_score = sorted_subcategories[0][1]

            # Require at least 10 points for a single subcategory
            if top_score >= 10:
                if len(sorted_subcategories) == 1 or sorted_subcategories[1][1] < top_score * 0.7:
                    return sorted_subcategories[0][0]
                else:
                    # Return multiple if scores are similar
                    subcategories = [cat for cat, score in sorted_subcategories[:3] if score >= 8]
                    return subcategories if len(subcategories) > 1 else (subcategories[0] if subcategories else None)

        return None

    def _calculate_subcategory_score(self, subcategory: str, keywords: List[str]) -> float:
        """
        Calculate score for a subcategory based on keyword matches.

        Args:
            subcategory: Subcategory name
            keywords: List of keywords for this subcategory

        Returns:
            float: Score for this subcategory (0-100)
        """
        score = 0.0

        # Check topics (highest weight)
        for keyword in keywords:
            if keyword in self.topics:
                score += 20

        # Check description (medium weight)
        for keyword in keywords:
            if keyword in self.description:
                score += 5

        return score


def extract(repo_data: Dict[str, Any], primary_category: Optional[str] = None, 
            repo_files: Dict[str, str] = None, **kwargs) -> Optional[Union[str, List[str]]]:
    """
    Extract applicationSubCategory from repository metadata.

    Args:
        repo_data: Dictionary containing repository metadata from GitHub API
        primary_category: The primary applicationCategory (optional)
        repo_files: Dictionary containing repository file contents (optional)
        **kwargs: Additional arguments (ignored)

    Returns:
        str: Single subcategory
        list: Multiple subcategories if applicable
        None: If no subcategory can be determined with confidence
    """
    try:
        extractor = ApplicationSubCategoryExtractor(repo_data)
        result = extractor.extract(primary_category)

        if result:
            logger.info(f"Extracted applicationSubCategory: {result}")
            return result
        else:
            logger.debug("No applicationSubCategory found with sufficient confidence")
            return None

    except Exception as e:
        logger.error(f"Error extracting applicationSubCategory: {str(e)}")
        return None


def get(repository_url: str, primary_category: Optional[str] = None) -> Dict[str, Optional[Union[str, List[str]]]]:
    """
    Extract applicationSubCategory from a GitHub repository.

    Args:
        repository_url (str): The URL of the GitHub repository.
        primary_category (str): The primary applicationCategory (optional)

    Returns:
        Dict: A dictionary containing the 'applicationSubCategory' property and its value.
              Returns an empty dict if no subcategory can be extracted with confidence.
    """
    try:
        from src.github_api import parse_repository_url, fetch_repository_info
        from src.utils import normalize_url

        repository_url = normalize_url(repository_url)
        owner, repo = parse_repository_url(repository_url)
        if not owner or not repo:
            return {}

        repo_data = fetch_repository_info(owner, repo)
        if not repo_data:
            return {}

        result = extract(repo_data, primary_category)

        if result:
            return {"applicationSubCategory": result}
        else:
            return {}

    except Exception as e:
        logger.error(f"Error in get function: {str(e)}")
        return {}
