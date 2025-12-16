"""
Application Category Property Module

Handles extraction and validation of the 'applicationCategory' Codemeta property.
Uses external vocabularies (schema.org, Google Play categories) and NLP techniques
to detect software application categories from repository metadata.
"""

from typing import Optional, Tuple, Dict, List, Any
from src.base_metadata import BaseMetadata
import re


class ApplicationCategoryMetadata(BaseMetadata):
    """Handles applicationCategory metadata extraction and validation using NLP and external vocabularies."""

    CODEMETA_PROPERTY = 'applicationCategory'
    CODEMETA_TYPE = 'schema:Text'
    REQUIRED = False

    # Official schema.org and Google Play categories with keywords and identifiers
    CATEGORY_KEYWORDS = {
        'Game': {
            'keywords': ['game', 'gaming', 'play', 'arcade', 'puzzle', 'strategy', 'rpg', 'action', 'sports'],
            'identifier': 'https://schema.org/Game',
            'wikidata': 'Q7889'
        },
        'Multimedia': {
            'keywords': ['audio', 'video', 'media', 'player', 'editor', 'streaming', 'converter', 'ffmpeg', 'codec'],
            'identifier': 'https://schema.org/MultimediaObject',
            'wikidata': 'Q6004'
        },
        'Productivity': {
            'keywords': ['productivity', 'office', 'document', 'spreadsheet', 'presentation', 'word processor', 'note', 'todo', 'task'],
            'identifier': 'https://schema.org/SoftwareApplication',
            'wikidata': 'Q7292'
        },
        'Business': {
            'keywords': ['business', 'enterprise', 'crm', 'erp', 'accounting', 'invoice', 'billing', 'hr', 'management'],
            'identifier': 'https://schema.org/SoftwareApplication',
            'wikidata': 'Q4830453'
        },
        'Education': {
            'keywords': ['education', 'learning', 'course', 'tutorial', 'training', 'school', 'university', 'language', 'math'],
            'identifier': 'https://schema.org/EducationalApplication',
            'wikidata': 'Q8434'
        },
        'DeveloperApplication': {
            'keywords': ['library', 'framework', 'sdk', 'api', 'tool', 'compiler', 'debugger', 'ide', 'version control', 'build', 'testing', 'code', 'development'],
            'identifier': 'https://schema.org/SoftwareApplication',
            'wikidata': 'Q7397'
        },
        'Utilities': {
            'keywords': ['utility', 'tool', 'file manager', 'compression', 'converter', 'monitor', 'system'],
            'identifier': 'https://schema.org/SoftwareApplication',
            'wikidata': 'Q7397'
        },
        'Communication': {
            'keywords': ['communication', 'chat', 'email', 'messaging', 'voip', 'forum', 'social', 'collaboration'],
            'identifier': 'https://schema.org/SoftwareApplication',
            'wikidata': 'Q11027'
        },
        'DataScienceML': {
            'keywords': ['machine learning', 'deep learning', 'neural network', 'ai', 'artificial intelligence', 'data science', 'tensorflow', 'pytorch', 'sklearn', 'nlp', 'computer vision'],
            'identifier': 'https://schema.org/SoftwareApplication',
            'wikidata': 'Q11019'
        },
        'WebApplication': {
            'keywords': ['web', 'web application', 'web app', 'spa', 'progressive web', 'web-based', 'browser', 'html', 'javascript', 'react', 'vue', 'angular'],
            'identifier': 'https://schema.org/WebApplication',
            'wikidata': 'Q7397'
        },
        'SystemInfrastructure': {
            'keywords': ['database', 'cache', 'message queue', 'container', 'kubernetes', 'docker', 'infrastructure', 'devops', 'ci/cd', 'cloud'],
            'identifier': 'https://schema.org/SoftwareApplication',
            'wikidata': 'Q7397'
        },
        'GraphicsDesign': {
            'keywords': ['graphics', 'design', 'image editor', 'photo', 'vector', 'cad', '3d', 'animation', 'gimp', 'blender'],
            'identifier': 'https://schema.org/SoftwareApplication',
            'wikidata': 'Q11019'
        },
    }

    def extract(self) -> None:
        """Extract applicationCategory from repository metadata."""
        # Try to detect category from content
        result = self._detect_category()
        if result:
            self.metadata = result[0]
            self.confidence = result[1]
        else:
            self.metadata = None

    def _detect_category(self) -> Optional[Tuple[str, float]]:
        """
        Detect application category using NLP and keyword matching.

        Returns:
            Tuple of (category, confidence) or None if not detected
        """
        # Collect text from multiple sources
        description = self._get_value('description') or ''
        readme_content = self._get_value('readme_content') or ''
        topics = self._get_value('topics') or []
        keywords = self._get_value('keywords') or []
        programming_languages = self._get_value('programmingLanguage') or []

        # Combine all text
        all_text = f"{readme_content} {description} {' '.join(topics)} {' '.join(keywords)} {' '.join(programming_languages)}".lower()

        if not all_text.strip():
            return None

        # Score categories
        category_scores = {}
        for category, config in self.CATEGORY_KEYWORDS.items():
            score = self._score_category(all_text, config['keywords'])
            if score > 0:
                category_scores[category] = score

        if not category_scores:
            return None

        # Get best match
        best_category = max(category_scores, key=category_scores.get)
        confidence = min(category_scores[best_category], 1.0)

        # Only return if confidence is reasonable
        if confidence >= 0.25:
            return best_category, confidence

        return None

    def _score_category(self, text: str, keywords: List[str]) -> float:
        """
        Score how well a category matches the given text.

        Args:
            text: Combined text from all sources (lowercase)
            keywords: List of keywords for this category

        Returns:
            Score between 0 and 1
        """
        if not keywords:
            return 0.0

        matches = sum(1 for kw in keywords if kw in text)
        return matches / len(keywords)

    def _validate_metadata(self) -> None:
        """Validate applicationCategory metadata."""
        if not self.metadata:
            if self.REQUIRED:
                self.add_error(f"Required field '{self.CODEMETA_PROPERTY}' is missing")
        elif not isinstance(self.metadata, str):
            self.add_error(f"Field '{self.CODEMETA_PROPERTY}' must be a string")
        elif len(self.metadata) > 200:
            self.add_warning(f"Field '{self.CODEMETA_PROPERTY}' is very long ({len(self.metadata)} characters)")

    def to_codemeta_dict(self) -> Optional[str]:
        """Convert to Codemeta format."""
        if self.metadata:
            return self.metadata
        return None
