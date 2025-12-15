"""
Application Category Property Module

Handles extraction and validation of the 'applicationCategory' Codemeta property.
Uses NLP techniques to detect software application categories from repository metadata.
"""

from typing import Dict, Any, Optional, Tuple
from src.base_metadata import BaseMetadata
import re


class ApplicationCategoryMetadata(BaseMetadata):
    """Handles applicationCategory metadata extraction and validation using NLP."""

    CODEMETA_PROPERTY = 'applicationCategory'
    CODEMETA_TYPE = 'schema:Text'
    REQUIRED = False

    # Category keywords mapping with confidence weights
    CATEGORY_KEYWORDS = {
        'Game': {
            'keywords': ['game', 'gaming', 'arcade', 'puzzle', 'strategy', 'action', 'rpg', 'moba', 'fps'],
            'patterns': [r'game\s+(engine|framework|dev)', r'(arcade|puzzle|strategy|action)\s+game'],
        },
        'Multimedia': {
            'keywords': ['audio', 'video', 'media', 'player', 'editor', 'streaming', 'codec', 'ffmpeg'],
            'patterns': [r'(audio|video|media)\s+(player|editor|processor)', r'multimedia'],
        },
        'Productivity': {
            'keywords': ['office', 'document', 'spreadsheet', 'presentation', 'note', 'todo', 'task', 'calendar'],
            'patterns': [r'(word|text)\s+processor', r'spreadsheet', r'presentation'],
        },
        'Business': {
            'keywords': ['crm', 'erp', 'accounting', 'invoice', 'billing', 'sales', 'inventory', 'enterprise'],
            'patterns': [r'(crm|erp|accounting|billing)\s+(system|software)', r'business\s+(management|intelligence)'],
        },
        'Education': {
            'keywords': ['learning', 'education', 'course', 'tutorial', 'quiz', 'exam', 'school', 'university'],
            'patterns': [r'(language|math|science)\s+learning', r'educational\s+(software|platform)'],
        },
        'Developer Tools': {
            'keywords': ['ide', 'compiler', 'debugger', 'build', 'test', 'lint', 'format', 'parser', 'generator',
                        'framework', 'library', 'sdk', 'api', 'cli', 'tool', 'dev', 'development'],
            'patterns': [r'(ide|compiler|debugger|build\s+tool)', r'development\s+(tool|framework)',
                        r'(python|javascript|java|rust|go)\s+(library|framework)'],
        },
        'Utilities': {
            'keywords': ['file', 'manager', 'compression', 'archive', 'converter', 'utility', 'tool', 'system'],
            'patterns': [r'(file|archive|compression)\s+(manager|tool)', r'(converter|utility)'],
        },
        'Communication': {
            'keywords': ['email', 'chat', 'messaging', 'mail', 'slack', 'discord', 'telegram', 'communication'],
            'patterns': [r'(email|chat|messaging)\s+(client|application|platform)', r'communication\s+tool'],
        },
        'Data Science & ML': {
            'keywords': ['machine learning', 'ml', 'deep learning', 'neural', 'tensorflow', 'pytorch', 'sklearn',
                        'data science', 'nlp', 'computer vision', 'ai', 'artificial intelligence', 'classification',
                        'prediction', 'analysis', 'analytics'],
            'patterns': [r'(machine|deep)\s+learning', r'(tensorflow|pytorch|sklearn|keras)',
                        r'(nlp|computer\s+vision|data\s+science)', r'neural\s+network'],
        },
        'Web & Internet': {
            'keywords': ['browser', 'web', 'http', 'server', 'website', 'webapp', 'internet', 'html', 'css',
                        'javascript', 'react', 'vue', 'angular', 'node'],
            'patterns': [r'web\s+(browser|server|framework|application)', r'(react|vue|angular|node)\s+(app|framework)',
                        r'(http|rest|graphql)\s+(server|api)'],
        },
        'System & Infrastructure': {
            'keywords': ['database', 'sql', 'nosql', 'mongodb', 'postgres', 'mysql', 'redis', 'docker', 'kubernetes',
                        'devops', 'ci/cd', 'cloud', 'infrastructure', 'os', 'kernel', 'system'],
            'patterns': [r'(database|sql|nosql)\s+(system|engine)', r'(docker|kubernetes|devops)',
                        r'(ci|cd|continuous\s+(integration|deployment))'],
        },
        'Graphics & Design': {
            'keywords': ['image', 'graphics', 'design', 'editor', 'modeling', '3d', 'vector', 'cad', 'blender',
                        'photoshop', 'gimp', 'drawing', 'paint'],
            'patterns': [r'(image|graphics)\s+(editor|processing)', r'(3d|vector)\s+(modeling|graphics)',
                        r'(cad|design)\s+(software|tool)'],
        },
    }

    def extract(self) -> Dict[str, Any]:
        """
        Extract applicationCategory from raw data using NLP techniques.

        Returns:
            Dictionary with 'applicationCategory' key containing the detected value
        """
        # Try explicit field first
        value = self._get_value('applicationCategory')

        if not value:
            # Use NLP-based detection
            value = self._detect_category()

        if not value:
            if self.REQUIRED:
                self.add_error(f"Required field '{self.CODEMETA_PROPERTY}' could not be extracted")
            return {}

        # Validate confidence
        if isinstance(value, tuple):
            category, confidence = value
            if confidence < 0.45:
                # Omit uncertain classifications
                self.add_warning(f"'{self.CODEMETA_PROPERTY}' detected with low confidence ({confidence:.2f}), omitting")
                return {}
            value = category

        self.metadata[self.CODEMETA_PROPERTY] = value
        return self.metadata

    def _detect_category(self) -> Optional[Tuple[str, float]]:
        """
        Detect application category using NLP techniques.

        Analyzes description, README, topics, and keywords to determine category.

        Returns:
            Tuple of (category, confidence) or None if not detected
        """
        # Collect text from multiple sources
        description = self._get_value('description') or ''
        readme = self._get_value('readme') or ''
        topics = self._get_value('topics') or []
        keywords = self._get_value('keywords') or []

        # Combine all text
        all_text = f"{description} {readme} {' '.join(topics)} {' '.join(keywords)}".lower()

        if not all_text.strip():
            return None

        # Score each category
        category_scores = {}
        for category, config in self.CATEGORY_KEYWORDS.items():
            score = self._score_category(all_text, config)
            if score > 0:
                category_scores[category] = score

        if not category_scores:
            return None

        # Get best match
        best_category = max(category_scores, key=category_scores.get)
        confidence = min(category_scores[best_category], 1.0)  # Cap at 1.0

        return best_category, confidence

    def _score_category(self, text: str, config: Dict[str, Any]) -> float:
        """
        Score how well a category matches the given text.

        Args:
            text: Combined text from all sources (lowercase)
            config: Category configuration with keywords and patterns

        Returns:
            Score between 0 and 1
        """
        score = 0.0

        # Keyword matching (weight: 0.4)
        keywords = config.get('keywords', [])
        if keywords:
            keyword_matches = sum(1 for kw in keywords if kw in text)
            # Use logarithmic scaling to handle categories with many keywords
            import math
            keyword_score = min(math.log(keyword_matches + 1) / math.log(len(keywords) + 1), 1.0)
            score += keyword_score * 0.4

        # Pattern matching (weight: 0.6)
        patterns = config.get('patterns', [])
        if patterns:
            pattern_matches = sum(1 for pattern in patterns if re.search(pattern, text))
            # Use logarithmic scaling to handle categories with many patterns
            import math
            pattern_score = min(math.log(pattern_matches + 1) / math.log(len(patterns) + 1), 1.0)
            score += pattern_score * 0.6

        return min(score, 1.0)

    def _validate_metadata(self) -> None:
        """Validate applicationCategory metadata."""
        if not self.metadata:
            if self.REQUIRED:
                self.add_error(f"Required field '{self.CODEMETA_PROPERTY}' is missing")
            return

        value = self.metadata.get(self.CODEMETA_PROPERTY)

        if not value:
            if self.REQUIRED:
                self.add_error(f"'{self.CODEMETA_PROPERTY}' is empty")
            return

        # Validate that value is a string
        if not isinstance(value, str):
            self.add_error(f"'{self.CODEMETA_PROPERTY}' must be a string, got {type(value).__name__}")
            return

        # Validate that value is a known category
        known_categories = set(self.CATEGORY_KEYWORDS.keys())
        if value not in known_categories:
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' value '{value}' is not a standard category")

    def to_codemeta_dict(self) -> Dict[str, Any]:
        """
        Convert to Codemeta format.

        Returns:
            Dictionary in Codemeta format
        """
        if not self.metadata:
            return {}

        return {
            self.CODEMETA_PROPERTY: self.metadata[self.CODEMETA_PROPERTY]
        }
