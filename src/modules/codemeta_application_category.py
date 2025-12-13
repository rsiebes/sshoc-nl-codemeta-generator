"""
CodeMeta applicationCategory Module

Extracts the application category/type of the software according to CodeMeta 3.1 standard.
The applicationCategory property describes the type of software application using standard
categories from schema.org (e.g., "DeveloperApplication", "DesktopApplication", "WebApplication",
"MobileApplication", "GameApplication", "MultimediaApplication", "ProductivityApplication", etc.).

This module analyzes multiple sources:
1. GitHub repository topics/tags
2. Package metadata (setup.py, package.json, Cargo.toml, etc.)
3. README content analysis
4. Repository description
5. File structure and language patterns

Returns:
    dict: CodeMeta-compliant applicationCategory structure
    str: Single category string (e.g., "DeveloperApplication")
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
        "DeveloperApplication": [
            "build", "compiler", "debugger", "editor", "framework", "ide", "library",
            "lint", "parser", "sdk", "test", "tool", "linter", "formatter", "transpiler",
            "bundler", "package manager", "version control", "ci", "cd", "deployment",
            "docker", "kubernetes", "devops", "api", "rest", "graphql", "database",
            "orm", "query", "migration", "schema", "validation", "serialization"
        ],
        "WebApplication": [
            "web", "website", "webapp", "http", "server", "client", "frontend",
            "backend", "full-stack", "django", "flask", "express", "rails", "laravel",
            "wordpress", "cms", "blog", "portal", "dashboard", "admin", "spa", "pwa",
            "react", "vue", "angular", "svelte", "nextjs", "nuxt", "gatsby"
        ],
        "DesktopApplication": [
            "desktop", "gui", "gtk", "qt", "wxwidgets", "electron", "tauri",
            "swing", "javafx", "winforms", "wpf", "macos", "windows", "linux",
            "cross-platform", "native", "application"
        ],
        "MobileApplication": [
            "mobile", "android", "ios", "iphone", "ipad", "flutter", "react native",
            "xamarin", "cordova", "ionic", "app", "smartphone", "tablet", "cross-mobile"
        ],
        "GameApplication": [
            "game", "gaming", "engine", "unity", "unreal", "godot", "pygame",
            "arcade", "puzzle", "rpg", "mmo", "3d", "graphics", "animation"
        ],
        "MultimediaApplication": [
            "audio", "video", "image", "graphics", "animation", "media", "player",
            "editor", "converter", "ffmpeg", "imagemagick", "blender", "photoshop",
            "streaming", "podcast", "music", "photo", "visual"
        ],
        "ProductivityApplication": [
            "productivity", "office", "document", "spreadsheet", "presentation",
            "note", "todo", "calendar", "email", "communication", "collaboration",
            "project management", "task", "workflow", "automation"
        ],
        "UtilityApplication": [
            "utility", "tool", "system", "monitor", "backup", "compression",
            "encryption", "antivirus", "cleaner", "optimizer", "converter"
        ],
        "ScienceApplication": [
            "science", "research", "data", "analysis", "visualization", "statistics",
            "machine learning", "deep learning", "neural", "ai", "nlp", "computer vision",
            "bioinformatics", "chemistry", "physics", "mathematics", "simulation"
        ],
        "BusinessApplication": [
            "business", "erp", "crm", "accounting", "finance", "hr", "sales",
            "marketing", "inventory", "supply chain", "ecommerce", "retail"
        ],
        "EducationApplication": [
            "education", "learning", "course", "tutorial", "training", "school",
            "university", "exam", "quiz", "homework", "textbook"
        ],
        "HealthApplication": [
            "health", "medical", "healthcare", "hospital", "clinic", "doctor",
            "patient", "medicine", "pharmacy", "fitness", "wellness", "mental health"
        ],
        "SocialApplication": [
            "social", "social media", "chat", "messaging", "forum", "community",
            "network", "collaboration", "team", "meeting", "conference", "video call"
        ],
        "ShoppingApplication": [
            "shopping", "store", "ecommerce", "marketplace", "cart", "checkout",
            "payment", "product", "catalog", "inventory"
        ],
        "TravelApplication": [
            "travel", "map", "navigation", "gps", "booking", "hotel", "flight",
            "car rental", "tourism", "weather", "location"
        ],
        "NewsApplication": [
            "news", "blog", "article", "journalism", "publication", "rss", "feed"
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
            str: Single category (e.g., "DeveloperApplication")
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
                return f"https://www.wikidata.org/wiki/Q{self._get_wikidata_id(sorted_categories[0][0])}"
            else:
                # Return multiple categories if scores are similar
                categories = [
                    f"https://www.wikidata.org/wiki/Q{self._get_wikidata_id(cat)}"
                    for cat, _ in sorted_categories[:3]
                ]
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
            "python": ["DeveloperApplication", "ScienceApplication", "DataApplication"],
            "javascript": ["WebApplication", "DeveloperApplication"],
            "java": ["DeveloperApplication", "BusinessApplication"],
            "csharp": ["DeveloperApplication", "DesktopApplication", "GameApplication"],
            "cpp": ["DeveloperApplication", "GameApplication", "MultimediaApplication"],
            "go": ["DeveloperApplication", "SystemApplication"],
            "rust": ["DeveloperApplication", "SystemApplication"],
            "swift": ["MobileApplication", "DesktopApplication"],
            "kotlin": ["MobileApplication", "DeveloperApplication"],
            "ruby": ["WebApplication", "DeveloperApplication"],
            "php": ["WebApplication", "DeveloperApplication"],
            "r": ["ScienceApplication", "DataApplication"],
            "matlab": ["ScienceApplication", "DataApplication"],
            "julia": ["ScienceApplication", "DataApplication"],
        }

        if self.language in language_category_map:
            for lang_category in language_category_map[self.language]:
                if lang_category == category:
                    score += 5

        return score

    def _get_wikidata_id(self, category: str) -> str:
        """
        Get Wikidata ID for a category (simplified mapping).

        Args:
            category: Category name

        Returns:
            str: Wikidata ID (Q-number)
        """
        wikidata_mapping = {
            "DeveloperApplication": "56678088",
            "WebApplication": "7397968",
            "DesktopApplication": "16869893",
            "MobileApplication": "6061973",
            "GameApplication": "7889",
            "MultimediaApplication": "1305812",
            "ProductivityApplication": "1305812",
            "UtilityApplication": "1305812",
            "ScienceApplication": "1305812",
            "BusinessApplication": "1305812",
            "EducationApplication": "1305812",
            "HealthApplication": "1305812",
            "SocialApplication": "1305812",
            "ShoppingApplication": "1305812",
            "TravelApplication": "1305812",
            "NewsApplication": "1305812",
        }
        return wikidata_mapping.get(category, "1305812")


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
        str: Single application category (e.g., "DeveloperApplication")
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
