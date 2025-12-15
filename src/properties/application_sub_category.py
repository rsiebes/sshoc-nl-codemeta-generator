"""
Application Sub Category Property Module

Handles extraction and validation of the 'applicationSubCategory' Codemeta property.
Uses NLP techniques to detect software application subcategories from repository metadata.
"""

from typing import Dict, Any, Optional, Tuple
from src.base_metadata import BaseMetadata
import re


class ApplicationSubCategoryMetadata(BaseMetadata):
    """Handles applicationSubCategory metadata extraction and validation using NLP."""

    CODEMETA_PROPERTY = 'applicationSubCategory'
    CODEMETA_TYPE = 'schema:Text'
    REQUIRED = False

    # Subcategory keywords mapping with parent categories
    SUBCATEGORY_KEYWORDS = {
        'Game': {
            'ActionGame': ['action', 'shooter', 'combat', 'fighting'],
            'StrategyGame': ['strategy', 'turn-based', 'rts', 'tactics'],
            'ArcadeGame': ['arcade', 'retro', 'classic'],
            'PuzzleGame': ['puzzle', 'match-3', 'logic'],
            'RPG': ['rpg', 'role-playing', 'fantasy', 'adventure'],
            'SportsGame': ['sports', 'racing', 'football', 'soccer'],
        },
        'Multimedia': {
            'AudioPlayer': ['audio player', 'music player', 'mp3'],
            'VideoPlayer': ['video player', 'movie player', 'mkv', 'mp4'],
            'AudioEditor': ['audio editor', 'daw', 'music production'],
            'VideoEditor': ['video editor', 'video editing', 'ffmpeg'],
            'ImageEditor': ['image editor', 'photo editor', 'gimp'],
            'MediaConverter': ['converter', 'transcoder', 'encoding'],
        },
        'Productivity': {
            'WordProcessor': ['word processor', 'text editor', 'document'],
            'Spreadsheet': ['spreadsheet', 'excel', 'csv'],
            'PresentationSoftware': ['presentation', 'slides', 'powerpoint'],
            'NoteTaking': ['note', 'notebook', 'wiki'],
            'TaskManagement': ['task', 'todo', 'project management'],
            'Calendar': ['calendar', 'scheduling', 'appointment'],
        },
        'Business': {
            'CRM': ['crm', 'customer relationship'],
            'ERP': ['erp', 'enterprise resource planning'],
            'AccountingSoftware': ['accounting', 'invoice', 'billing'],
            'ProjectManagement': ['project management', 'agile', 'kanban'],
            'HRManagement': ['hr', 'human resources', 'payroll'],
        },
        'Education': {
            'LanguageLearning': ['language', 'learning', 'vocabulary'],
            'MathSoftware': ['math', 'mathematics', 'algebra'],
            'ScienceEducation': ['science', 'physics', 'chemistry'],
            'OnlineCourse': ['course', 'mooc', 'tutorial'],
        },
        'Developer Tools': {
            'IDE': ['ide', 'integrated development', 'vscode', 'intellij'],
            'VersionControl': ['git', 'version control', 'svn'],
            'BuildTool': ['build', 'gradle', 'maven', 'cmake'],
            'TestingFramework': ['test', 'testing', 'unittest', 'pytest'],
            'Debugger': ['debugger', 'debugging'],
            'CodeAnalysis': ['lint', 'analysis', 'static analysis'],
            'Library': ['library', 'sdk', 'framework', 'package'],
            'API': ['api', 'rest', 'graphql', 'rpc'],
        },
        'Utilities': {
            'FileManager': ['file manager', 'explorer'],
            'TextEditor': ['text editor', 'editor', 'vim', 'nano'],
            'Compression': ['compression', 'archive', 'zip', 'tar'],
            'Converter': ['converter', 'conversion', 'transform'],
            'SystemMonitor': ['monitor', 'system', 'performance'],
        },
        'Communication': {
            'EmailClient': ['email', 'mail client', 'smtp'],
            'ChatApplication': ['chat', 'messaging', 'slack', 'discord'],
            'VoIP': ['voip', 'sip', 'call'],
            'ForumSoftware': ['forum', 'discussion', 'community'],
        },
        'Data Science & ML': {
            'MachineLearning': ['machine learning', 'ml', 'model', 'training'],
            'DeepLearning': ['deep learning', 'neural network', 'cnn', 'rnn'],
            'DataAnalysis': ['data analysis', 'analytics', 'statistics'],
            'DataVisualization': ['visualization', 'chart', 'graph', 'plot'],
            'NLP': ['nlp', 'natural language', 'text processing'],
            'ComputerVision': ['computer vision', 'image processing', 'cv'],
        },
        'Web & Internet': {
            'WebBrowser': ['browser', 'chromium', 'firefox'],
            'WebServer': ['web server', 'http server', 'nginx', 'apache'],
            'WebFramework': ['web framework', 'django', 'flask', 'rails'],
            'WebApplication': ['web app', 'spa', 'progressive web'],
            'CMS': ['cms', 'content management', 'wordpress'],
        },
        'System & Infrastructure': {
            'Database': ['database', 'sql', 'nosql', 'mongodb', 'postgres'],
            'Cache': ['cache', 'redis', 'memcached'],
            'MessageQueue': ['message queue', 'kafka', 'rabbitmq'],
            'Containerization': ['docker', 'container', 'oci'],
            'Orchestration': ['kubernetes', 'orchestration', 'k8s'],
            'CI/CD': ['ci', 'cd', 'jenkins', 'gitlab-ci'],
            'CloudPlatform': ['cloud', 'aws', 'azure', 'gcp'],
        },
        'Graphics & Design': {
            'ImageEditor': ['image editor', 'photo editor', 'gimp'],
            '3DModeling': ['3d', 'modeling', 'blender', 'cad'],
            'VectorGraphics': ['vector', 'svg', 'illustrator'],
            'CAD': ['cad', 'autocad', 'design'],
            'Animation': ['animation', 'animator', 'motion'],
        },
    }

    def extract(self) -> Dict[str, Any]:
        """
        Extract applicationSubCategory from raw data using NLP techniques.

        Returns:
            Dictionary with 'applicationSubCategory' key containing the detected value
        """
        # Try explicit field first
        value = self._get_value('applicationSubCategory')

        if not value:
            # Use NLP-based detection
            value = self._detect_subcategory()

        if not value:
            if self.REQUIRED:
                self.add_error(f"Required field '{self.CODEMETA_PROPERTY}' could not be extracted")
            return {}

        # Validate confidence
        if isinstance(value, tuple):
            subcategory, confidence = value
            if confidence < 0.45:
                # Omit uncertain classifications
                self.add_warning(f"'{self.CODEMETA_PROPERTY}' detected with low confidence ({confidence:.2f}), omitting")
                return {}
            value = subcategory

        self.metadata[self.CODEMETA_PROPERTY] = value
        return self.metadata

    def _detect_subcategory(self) -> Optional[Tuple[str, float]]:
        """
        Detect application subcategory using NLP techniques.

        Analyzes description, README, topics, and keywords to determine subcategory.

        Returns:
            Tuple of (subcategory, confidence) or None if not detected
        """
        # First, try to get the parent category
        parent_category = self._get_value('applicationCategory')

        if not parent_category:
            # Try to detect parent category from raw data
            from src.properties.application_category import ApplicationCategoryMetadata
            cat_detector = ApplicationCategoryMetadata(self.raw_data)
            result = cat_detector._detect_category()
            if result:
                parent_category = result[0]

        if not parent_category or parent_category not in self.SUBCATEGORY_KEYWORDS:
            return None

        # Collect text from multiple sources
        description = self._get_value('description') or ''
        readme = self._get_value('readme') or ''
        topics = self._get_value('topics') or []
        keywords = self._get_value('keywords') or []

        # Combine all text
        all_text = f"{description} {readme} {' '.join(topics)} {' '.join(keywords)}".lower()

        if not all_text.strip():
            return None

        # Score subcategories within parent category
        subcategories = self.SUBCATEGORY_KEYWORDS[parent_category]
        subcategory_scores = {}

        for subcategory, keywords_list in subcategories.items():
            score = self._score_subcategory(all_text, keywords_list)
            if score > 0:
                subcategory_scores[subcategory] = score

        if not subcategory_scores:
            return None

        # Get best match
        best_subcategory = max(subcategory_scores, key=subcategory_scores.get)
        confidence = min(subcategory_scores[best_subcategory], 1.0)  # Cap at 1.0

        return best_subcategory, confidence

    def _score_subcategory(self, text: str, keywords_list: list) -> float:
        """
        Score how well a subcategory matches the given text.

        Args:
            text: Combined text from all sources (lowercase)
            keywords_list: List of keywords for this subcategory

        Returns:
            Score between 0 and 1
        """
        if not keywords_list:
            return 0.0

        matches = sum(1 for kw in keywords_list if kw in text)
        return matches / len(keywords_list)

    def _validate_metadata(self) -> None:
        """Validate applicationSubCategory metadata."""
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

        # Validate that value is a known subcategory
        known_subcategories = set()
        for subcats in self.SUBCATEGORY_KEYWORDS.values():
            known_subcategories.update(subcats.keys())

        if value not in known_subcategories:
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' value '{value}' is not a standard subcategory")

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
