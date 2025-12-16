"""
Application Sub Category Property Module

Handles extraction and validation of the 'applicationSubCategory' Codemeta property.
Creates domain-specific subcategories based on repository content analysis.
"""

from typing import Optional, Tuple, Dict, List, Any
from src.base_metadata import BaseMetadata
import re


class ApplicationSubCategoryMetadata(BaseMetadata):
    """Handles applicationSubCategory metadata extraction using domain-specific analysis."""

    CODEMETA_PROPERTY = 'applicationSubCategory'
    CODEMETA_TYPE = 'schema:Text'
    REQUIRED = False

    # Domain-specific subcategories with keywords and identifiers
    DOMAIN_SUBCATEGORIES = {
        # Web/Internet subcategories
        'VocabularyAligner': {
            'keywords': ['vocabulary', 'alignment', 'mapping', 'skos', 'rdf', 'semantic', 'ontology', 'linked data'],
            'identifier': 'https://example.org/VocabularyAligner',
            'wikidata': 'Q6423319'
        },
        'SemanticWebTool': {
            'keywords': ['semantic web', 'rdf', 'owl', 'sparql', 'linked data', 'knowledge graph'],
            'identifier': 'https://example.org/SemanticWebTool',
            'wikidata': 'Q6423319'
        },
        'WebFramework': {
            'keywords': ['web framework', 'framework', 'django', 'flask', 'rails', 'express', 'fastapi', 'spring', 'wsgi', 'asgi', 'web app'],
            'identifier': 'https://schema.org/WebApplication',
            'wikidata': 'Q7397'
        },
        'ContentManagementSystem': {
            'keywords': ['cms', 'content management', 'wordpress', 'drupal', 'joomla'],
            'identifier': 'https://schema.org/WebApplication',
            'wikidata': 'Q7397'
        },
        # Data Science & ML subcategories
        'MachineLearningLibrary': {
            'keywords': ['machine learning', 'tensorflow', 'pytorch', 'sklearn', 'keras', 'xgboost', 'ml'],
            'identifier': 'https://example.org/MachineLearningLibrary',
            'wikidata': 'Q11019'
        },
        'DeepLearningFramework': {
            'keywords': ['deep learning', 'neural network', 'tensorflow', 'pytorch', 'keras', 'cnn', 'rnn'],
            'identifier': 'https://example.org/DeepLearningFramework',
            'wikidata': 'Q11019'
        },
        'NaturalLanguageProcessing': {
            'keywords': ['nlp', 'natural language', 'text processing', 'nltk', 'spacy', 'bert', 'language model'],
            'identifier': 'https://example.org/NLP',
            'wikidata': 'Q11019'
        },
        'ComputerVision': {
            'keywords': ['computer vision', 'image processing', 'opencv', 'image classification', 'object detection'],
            'identifier': 'https://example.org/ComputerVision',
            'wikidata': 'Q11019'
        },
        # Developer Tools subcategories
        'ProgrammingLanguage': {
            'keywords': ['programming language', 'compiler', 'interpreter', 'language implementation'],
            'identifier': 'https://schema.org/SoftwareApplication',
            'wikidata': 'Q7397'
        },
        'BuildTool': {
            'keywords': ['build tool', 'build system', 'cmake', 'maven', 'gradle', 'make', 'bazel'],
            'identifier': 'https://schema.org/SoftwareApplication',
            'wikidata': 'Q7397'
        },
        'TestingFramework': {
            'keywords': ['testing', 'test framework', 'unit test', 'pytest', 'jest', 'junit', 'rspec'],
            'identifier': 'https://schema.org/SoftwareApplication',
            'wikidata': 'Q7397'
        },
        'VersionControl': {
            'keywords': ['version control', 'git', 'svn', 'mercurial', 'source control'],
            'identifier': 'https://schema.org/SoftwareApplication',
            'wikidata': 'Q7397'
        },
        'DatabaseSystem': {
            'keywords': ['database', 'sql', 'nosql', 'mongodb', 'postgres', 'mysql', 'sqlite'],
            'identifier': 'https://schema.org/SoftwareApplication',
            'wikidata': 'Q7397'
        },
        'APILibrary': {
            'keywords': ['api', 'library', 'sdk', 'client library', 'wrapper'],
            'identifier': 'https://schema.org/SoftwareApplication',
            'wikidata': 'Q7397'
        },
        # Multimedia subcategories
        'AudioProcessing': {
            'keywords': ['audio', 'sound', 'music', 'daw', 'audio editor', 'synthesis'],
            'identifier': 'https://schema.org/MultimediaObject',
            'wikidata': 'Q6004'
        },
        'VideoProcessing': {
            'keywords': ['video', 'video editor', 'ffmpeg', 'codec', 'streaming'],
            'identifier': 'https://schema.org/MultimediaObject',
            'wikidata': 'Q6004'
        },
        'ImageProcessing': {
            'keywords': ['image', 'image processing', 'photo', 'graphics', 'opencv'],
            'identifier': 'https://schema.org/MultimediaObject',
            'wikidata': 'Q6004'
        },
    }

    def extract(self) -> None:
        """Extract applicationSubCategory from repository metadata."""
        result = self._detect_subcategory()
        if result:
            self.metadata = result[0]
            self.confidence = result[1]
        else:
            self.metadata = None

    def _detect_subcategory(self) -> Optional[Tuple[str, float]]:
        """
        Detect application subcategory using domain-specific keyword analysis.

        Returns:
            Tuple of (subcategory, confidence) or None if not detected
        """
        # Collect text from multiple sources
        description = self._get_value('description') or ''
        readme_content = self._get_value('readme_content') or ''
        topics = self._get_value('topics') or []
        keywords = self._get_value('keywords') or []
        programming_languages = self._get_value('programmingLanguage') or []

        # Combine all text, prioritizing README
        all_text = f"{readme_content} {description} {' '.join(topics)} {' '.join(keywords)} {' '.join(programming_languages)}".lower()

        if not all_text.strip():
            return None

        # Score all subcategories
        subcategory_scores = {}
        for subcategory, config in self.DOMAIN_SUBCATEGORIES.items():
            score = self._score_subcategory(all_text, config['keywords'])
            if score > 0:
                subcategory_scores[subcategory] = score

        if not subcategory_scores:
            return None

        # Get best match
        best_subcategory = max(subcategory_scores, key=subcategory_scores.get)
        confidence = min(subcategory_scores[best_subcategory], 1.0)

        # Only return if confidence is reasonable
        if confidence >= 0.20:
            return best_subcategory, confidence

        return None

    def _score_subcategory(self, text: str, keywords: List[str]) -> float:
        """
        Score how well a subcategory matches the given text.

        Args:
            text: Combined text from all sources (lowercase)
            keywords: List of keywords for this subcategory

        Returns:
            Score between 0 and 1
        """
        if not keywords:
            return 0.0

        matches = sum(1 for kw in keywords if kw in text)
        return matches / len(keywords)

    def _validate_metadata(self) -> None:
        """Validate applicationSubCategory metadata."""
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
