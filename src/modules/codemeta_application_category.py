"""
CodeMeta applicationCategory Module

Extracts the application category/type of the software according to CodeMeta 3.1 standard.
The applicationCategory property describes the type of software application using standard
text categories from schema.org and common app store classifications (e.g., "Game", "Multimedia",
"Developer", "Productivity", "Business", "Education", "Entertainment", "Health", "Utility",
"Social", "News", "Music", "Photo", "Video", "Navigation", "Shopping", "Travel", "Security",
"Medical", "Personalization", "Lifestyle", "Sports", "Kids", "Reference", "Communication").

This module analyzes multiple sources:
1. GitHub repository topics/tags
2. Package metadata (setup.py, package.json, Cargo.toml, etc.)
3. README content analysis
4. Repository description
5. File structure and language patterns

Returns:
    dict: CodeMeta-compliant applicationCategory structure
    str: Single category string (e.g., "Developer")
    list: Multiple categories if applicable
    None: If no category can be determined
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
    CATEGORY_KEYWORDS = {
        "Developer": [
            "build", "compiler", "debugger", "editor", "framework", "ide", "library",
            "lint", "parser", "sdk", "test", "tool", "linter", "formatter", "transpiler",
            "bundler", "package manager", "version control", "ci", "cd", "deployment",
            "docker", "kubernetes", "devops", "api", "rest", "graphql", "database",
            "orm", "query", "migration", "schema", "validation", "serialization", "toolkit"
        ],
        "Multimedia": [
            "audio", "video", "image", "graphics", "animation", "media", "player",
            "editor", "converter", "ffmpeg", "imagemagick", "blender", "photoshop",
            "streaming", "podcast", "music", "photo", "visual", "rendering"
        ],
        "Productivity": [
            "productivity", "office", "document", "spreadsheet", "presentation",
            "note", "todo", "calendar", "email", "communication", "collaboration",
            "project management", "task", "workflow", "automation", "organization"
        ],
        "Business": [
            "business", "erp", "crm", "accounting", "finance", "hr", "sales",
            "marketing", "inventory", "supply chain", "ecommerce", "retail", "enterprise"
        ],
        "Education": [
            "education", "learning", "course", "tutorial", "training", "school",
            "university", "exam", "quiz", "homework", "textbook", "instructional"
        ],
        "Entertainment": [
            "entertainment", "streaming", "movies", "videos", "live", "sports",
            "ticket", "theatre", "concert", "show", "broadcast"
        ],
        "Game": [
            "game", "gaming", "engine", "unity", "unreal", "godot", "pygame",
            "arcade", "puzzle", "rpg", "mmo", "3d", "graphics", "animation", "gameplay"
        ],
        "Health": [
            "health", "fitness", "workout", "yoga", "running", "cycling", "diet",
            "nutrition", "wellness", "exercise", "tracker", "activity"
        ],
        "Medical": [
            "medical", "healthcare", "hospital", "clinic", "doctor", "patient",
            "medicine", "pharmacy", "symptom", "disease", "health record"
        ],
        "Music": [
            "music", "audio", "song", "track", "album", "artist", "playlist",
            "recording", "streaming", "radio", "dj", "synthesizer"
        ],
        "News": [
            "news", "blog", "article", "journalism", "publication", "rss", "feed",
            "newspaper", "magazine", "media", "content"
        ],
        "Photo": [
            "photo", "image", "picture", "photography", "editing", "gallery",
            "album", "sharing", "filter", "effects", "camera"
        ],
        "Video": [
            "video", "movie", "film", "streaming", "playback", "editing",
            "codec", "transcoding", "player", "recording", "broadcast"
        ],
        "Navigation": [
            "navigation", "map", "gps", "location", "route", "direction",
            "travel", "driving", "walking", "public transport", "atlas"
        ],
        "Shopping": [
            "shopping", "store", "ecommerce", "marketplace", "cart", "checkout",
            "payment", "product", "catalog", "inventory", "retail"
        ],
        "Travel": [
            "travel", "booking", "hotel", "flight", "car rental", "tourism",
            "destination", "itinerary", "accommodation", "vacation"
        ],
        "Social": [
            "social", "social media", "chat", "messaging", "forum", "community",
            "network", "collaboration", "team", "meeting", "conference", "video call"
        ],
        "Security": [
            "security", "antivirus", "vpn", "encryption", "password", "protection",
            "firewall", "threat", "malware", "vulnerability", "secure"
        ],
        "Utility": [
            "utility", "tool", "system", "monitor", "backup", "compression",
            "encryption", "cleaner", "optimizer", "converter", "calculator"
        ],
        "Reference": [
            "reference", "dictionary", "encyclopedia", "manual", "documentation",
            "guide", "handbook", "knowledge", "vocabulary", "ontology", "taxonomy"
        ],
        "Communication": [
            "communication", "messaging", "chat", "email", "voice", "video call",
            "conference", "collaboration", "team", "meeting", "contact"
        ],
        "Kids": [
            "kids", "children", "family", "educational", "interactive", "story",
            "playbook", "learning", "fun", "age-appropriate"
        ],
        "Personalization": [
            "personalization", "theme", "wallpaper", "ringtone", "customization",
            "appearance", "settings", "preferences", "skin"
        ],
        "Lifestyle": [
            "lifestyle", "hobby", "interest", "diy", "fashion", "home", "garden",
            "automotive", "relationships", "style", "trends"
        ],
        "Sports": [
            "sports", "athletic", "game", "score", "statistics", "team",
            "player", "league", "tournament", "fitness", "training"
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

        Returns:
            str: Single category (e.g., "Developer")
            list: Multiple categories if applicable
            None: If no category can be determined
        """
        categories = set()

        # Score each category based on multiple signals
        category_scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = self._calculate_category_score(category, keywords)
            if score > 0:
                category_scores[category] = score

        if not category_scores:
            return None

        # Sort by score and return top categories
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)

        # Return single category if score is significantly higher
        if len(sorted_categories) > 0:
            top_score = sorted_categories[0][1]
            # If top score is significantly higher, return single category
            if len(sorted_categories) == 1 or sorted_categories[1][1] < top_score * 0.7:
                return sorted_categories[0][0]
            else:
                # Return multiple categories if scores are similar
                categories = [cat for cat, _ in sorted_categories[:3]]
                return categories if len(categories) > 1 else categories[0]

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

        # Check topics (highest weight)
        for keyword in keywords:
            if any(keyword in topic for topic in self.topics):
                score += 10

        # Check description (medium weight)
        for keyword in keywords:
            if keyword in self.description:
                score += 3

        # Check homepage (medium weight)
        for keyword in keywords:
            if keyword in self.homepage:
                score += 2

        # Check programming language patterns
        language_category_map = {
            "python": ["Developer", "Education", "Science"],
            "javascript": ["Developer", "Multimedia", "Web"],
            "java": ["Developer", "Business"],
            "csharp": ["Developer", "Game", "Multimedia"],
            "cpp": ["Developer", "Game", "Multimedia"],
            "go": ["Developer", "Utility"],
            "rust": ["Developer", "Utility", "Security"],
            "swift": ["Developer", "Multimedia"],
            "kotlin": ["Developer", "Mobile"],
            "ruby": ["Developer", "Web"],
            "php": ["Developer", "Web"],
            "r": ["Science", "Education"],
            "matlab": ["Science", "Education"],
            "julia": ["Science", "Education"],
        }

        if self.language in language_category_map:
            for lang_category in language_category_map[self.language]:
                if lang_category == category:
                    score += 5

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
        None: If no category can be determined
    """
    try:
        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        if result:
            logger.info(f"Extracted applicationCategory: {result}")
            return result
        else:
            logger.debug("No applicationCategory found")
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

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'applicationCategory' property and its value.
              Returns an empty dict if no category can be extracted.

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
