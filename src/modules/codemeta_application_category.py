"""
CodeMeta applicationCategory Module

Extracts the application category/type of the software according to CodeMeta 3.1 standard.
The applicationCategory property describes the type of software application using standard
text categories from schema.org and common app store classifications (e.g., "Game", "Multimedia",
"Developer", "Productivity", "Business", "Education", "Entertainment", "Health", "Utility",
"Social", "News", "Music", "Photo", "Video", "Navigation", "Shopping", "Travel", "Security",
"Medical", "Personalization", "Lifestyle", "Sports", "Reference").

This module uses a conservative approach - it only assigns categories when there is strong
evidence from multiple sources. If uncertain, it returns None/empty.

This module analyzes multiple sources:
1. GitHub repository topics/tags (highest weight)
2. Repository description (medium weight)
3. Homepage URL (low weight)
4. Programming language patterns (contextual)

Returns:
    str: Single category string (e.g., "Developer")
    list: Multiple categories if applicable (only if high confidence)
    None: If no category can be determined with confidence
"""

import os
import json
import re
from typing import Union, List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ApplicationCategoryExtractor:
    """Extracts application category from GitHub repository metadata."""

    # Mapping of keywords to application categories
    # Using more specific keywords to avoid false positives
    CATEGORY_KEYWORDS = {
        "Developer": [
            "compiler", "debugger", "editor", "ide", "library",
            "linter", "parser", "sdk", "test", "testing",
            "version control", "ci/cd", "deployment", "devops",
            "api", "rest", "graphql", "database", "orm",
            "framework", "toolkit", "tool"
        ],
        "Multimedia": [
            "audio", "video", "image", "graphics", "animation",
            "ffmpeg", "imagemagick", "blender",
            "streaming", "podcast", "rendering"
        ],
        "Productivity": [
            "productivity", "office", "document", "spreadsheet", "presentation",
            "note", "todo", "calendar", "email", "collaboration",
            "project management", "task", "workflow"
        ],
        "Business": [
            "erp", "crm", "accounting", "finance", "sales",
            "marketing", "inventory", "supply chain", "ecommerce", "retail"
        ],
        "Education": [
            "education", "learning", "course", "tutorial", "training",
            "school", "university", "exam", "quiz", "textbook"
        ],
        "Entertainment": [
            "entertainment", "streaming", "movies", "videos",
            "sports", "ticket", "theatre", "concert"
        ],
        "Game": [
            "game", "gaming", "game engine", "unity", "unreal", "godot",
            "arcade", "puzzle", "rpg", "mmo"
        ],
        "Health": [
            "health", "fitness", "workout", "yoga", "running",
            "diet", "nutrition", "wellness", "exercise"
        ],
        "Medical": [
            "medical", "healthcare", "hospital", "clinic", "doctor",
            "medicine", "pharmacy", "symptom", "disease"
        ],
        "Music": [
            "music", "audio", "song", "track", "album",
            "recording", "streaming", "radio", "synthesizer"
        ],
        "News": [
            "news", "blog", "article", "journalism", "publication",
            "rss", "feed", "newspaper", "magazine"
        ],
        "Photo": [
            "photo", "image", "photography", "editing", "gallery",
            "album", "sharing", "filter", "camera"
        ],
        "Video": [
            "video", "movie", "film", "streaming", "playback",
            "editing", "codec", "transcoding", "player"
        ],
        "Navigation": [
            "navigation", "map", "gps", "location", "route",
            "direction", "driving", "walking", "atlas"
        ],
        "Shopping": [
            "shopping", "store", "ecommerce", "marketplace", "cart",
            "checkout", "payment", "product", "catalog", "retail"
        ],
        "Travel": [
            "travel", "booking", "hotel", "flight", "car rental",
            "tourism", "destination", "itinerary", "accommodation"
        ],
        "Social": [
            "social", "social media", "chat", "messaging", "forum",
            "community", "network", "collaboration", "team", "meeting"
        ],
        "Security": [
            "security", "antivirus", "vpn", "encryption", "password",
            "protection", "firewall", "threat", "malware"
        ],
        "Utility": [
            "utility", "tool", "system", "monitor", "backup",
            "compression", "cleaner", "optimizer", "converter"
        ],
        "Reference": [
            "reference", "dictionary", "encyclopedia", "manual",
            "documentation", "guide", "handbook", "knowledge",
            "vocabulary", "ontology", "taxonomy"
        ],
        "Communication": [
            "communication", "messaging", "chat", "email", "voice",
            "video call", "conference", "collaboration"
        ],
        "Kids": [
            "kids", "children", "family", "educational",
            "interactive", "story", "playbook", "learning"
        ],
        "Personalization": [
            "personalization", "theme", "wallpaper", "ringtone",
            "customization", "appearance", "settings"
        ],
        "Lifestyle": [
            "lifestyle", "hobby", "interest", "diy", "fashion",
            "home", "garden", "automotive", "style"
        ],
        "Sports": [
            "sports", "athletic", "score", "statistics", "team",
            "player", "league", "tournament", "fitness"
        ]
    }

    def __init__(self, repo_data: Dict[str, Any]):
        """
        Initialize the ApplicationCategoryExtractor.

        Args:
            repo_data: Dictionary containing repository metadata from GitHub API
        """
        self.repo_data = repo_data
        self.owner = repo_data.get("owner", {}).get("login", "")
        self.repo_name = repo_data.get("name", "")
        self.description = (repo_data.get("description") or "").lower()
        self.topics = [t.lower() for t in repo_data.get("topics", [])]
        self.language = (repo_data.get("language") or "").lower()
        self.homepage = (repo_data.get("homepage") or "").lower()

    def extract(self) -> Optional[Union[str, List[str]]]:
        """
        Extract application category from repository metadata.

        Uses a conservative approach - only returns categories with strong evidence.

        Returns:
            str: Single category (e.g., "Developer")
            list: Multiple categories if applicable (only if high confidence)
            None: If no category can be determined with confidence
        """
        # Score each category based on multiple signals
        category_scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = self._calculate_category_score(category, keywords)
            if score > 0:
                category_scores[category] = score

        if not category_scores:
            return None

        # Sort by score
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)

        # Conservative threshold: only return if we have strong confidence
        # Require at least 15 points for a single category
        # Require at least 10 points for multiple categories
        if len(sorted_categories) > 0:
            top_score = sorted_categories[0][1]

            # If top score is very high and significantly higher than others, return single category
            if top_score >= 15 and (len(sorted_categories) == 1 or sorted_categories[1][1] < top_score * 0.6):
                return sorted_categories[0][0]
            # If we have multiple categories with similar high scores, return them
            elif top_score >= 10 and len(sorted_categories) > 1 and sorted_categories[1][1] >= 8:
                categories = [cat for cat, score in sorted_categories[:3] if score >= 8]
                return categories if len(categories) > 1 else (categories[0] if categories else None)

        # If we don't have strong confidence, return None
        return None

    def _calculate_category_score(self, category: str, keywords: List[str]) -> float:
        """
        Calculate score for a category based on keyword matches.

        Args:
            category: Category name
            keywords: List of keywords for this category

        Returns:
            float: Score for this category (0-100)
        """
        score = 0.0

        # Check topics (highest weight - exact matches only)
        for keyword in keywords:
            if keyword in self.topics:
                score += 20  # Exact topic match is very strong

        # Check description (medium weight - must be clear context)
        # Only count if keyword appears in description
        for keyword in keywords:
            if keyword in self.description:
                score += 3

        # Check homepage (low weight)
        for keyword in keywords:
            if keyword in self.homepage:
                score += 1

        # Check programming language patterns
        language_category_map = {
            "python": {"Developer": 5, "Education": 3},
            "javascript": {"Developer": 5},
            "java": {"Developer": 5, "Business": 3},
            "csharp": {"Developer": 5, "Game": 3},
            "cpp": {"Developer": 5, "Game": 3, "Multimedia": 3},
            "go": {"Developer": 5},
            "rust": {"Developer": 5, "Security": 3},
            "swift": {"Developer": 5},
            "kotlin": {"Developer": 5},
            "ruby": {"Developer": 5},
            "php": {"Developer": 5},
            "r": {"Education": 5},
            "matlab": {"Education": 5},
            "julia": {"Education": 5},
        }

        if self.language in language_category_map:
            lang_scores = language_category_map[self.language]
            if category in lang_scores:
                score += lang_scores[category]

        return score


def extract(repo_data: Dict[str, Any], repo_files: Dict[str, str] = None, **kwargs) -> Optional[Union[str, List[str]]]:
    """
    Extract applicationCategory from repository metadata.

    This function serves as the main entry point for the module, following the
    standard CodeMeta generator pattern.

    Args:
        repo_data: Dictionary containing repository metadata from GitHub API
        repo_files: Dictionary containing repository file contents (optional)
        **kwargs: Additional arguments (ignored)

    Returns:
        str: Single application category (e.g., "Developer")
        list: Multiple categories if applicable
        None: If no category can be determined with confidence
    """
    try:
        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        if result:
            logger.info(f"Extracted applicationCategory: {result}")
            return result
        else:
            logger.debug("No applicationCategory found with sufficient confidence")
            return None

    except Exception as e:
        logger.error(f"Error extracting applicationCategory: {str(e)}")
        return None


def get(repository_url: str) -> Dict[str, Optional[Union[str, List[str]]]]:
    """
    Extract applicationCategory from a GitHub repository.

    This function is the main entry point for the CodeMeta generator framework.
    It fetches repository metadata from GitHub API and extracts the application
    category based on multiple signals (topics, description, language, etc.).

    Uses a conservative approach - returns empty dict if uncertain.

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'applicationCategory' property and its value.
              Returns an empty dict if no category can be extracted with confidence.

    Example:
        >>> result = get("https://github.com/pallets/flask")
        >>> print(result)
        {'applicationCategory': 'Developer'}
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

        result = extract(repo_data)

        if result:
            return {"applicationCategory": result}
        else:
            return {}

    except Exception as e:
        logger.error(f"Error in get function: {str(e)}")
        return {}
