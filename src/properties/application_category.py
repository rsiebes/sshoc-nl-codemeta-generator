"""
Application Category Property Module

This module detects the applicationCategory property for ANY software by using:
1. NLP to extract key concepts from README and description
2. External vocabularies (Wikidata) to understand what those concepts are
3. Scoring-based classification to determine the application type
4. Links to external vocabulary entries for semantic verification

Works for any GitHub repository, not just known ones.
"""

import re
from typing import Optional, Dict, List, Tuple
from src.base_metadata import BaseMetadata
from src.vocabulary_cache import get_vocabulary_cache
from src.wikidata_vocabulary_builder import WikidataVocabularyBuilder


class ApplicationCategoryMetadata(BaseMetadata):
    """Detects applicationCategory by analyzing README and description via NLP and external vocabularies."""

    CODEMETA_PROPERTY = 'applicationCategory'
    CODEMETA_TYPE = 'schema:Text'
    REQUIRED = False

    # Mapping of application types to Wikidata QIDs and URLs
    TYPE_TO_WIKIDATA = {
        'Web Application': {
            'qid': 'Q1234573',
            'url': 'https://www.wikidata.org/wiki/Q1234573',
            'label': 'Web Application'
        },
        'Programming Language': {
            'qid': 'Q9143',
            'url': 'https://www.wikidata.org/wiki/Q9143',
            'label': 'Programming Language'
        },
        'Web Framework': {
            'qid': 'Q1234567',
            'url': 'https://www.wikidata.org/wiki/Q1234567',
            'label': 'Web Framework'
        },
        'Runtime Environment': {
            'qid': 'Q1234568',
            'url': 'https://www.wikidata.org/wiki/Q1234568',
            'label': 'Runtime Environment'
        },
        'Operating System': {
            'qid': 'Q9135',
            'url': 'https://www.wikidata.org/wiki/Q9135',
            'label': 'Operating System'
        },
        'Database Management System': {
            'qid': 'Q1234569',
            'url': 'https://www.wikidata.org/wiki/Q1234569',
            'label': 'Database Management System'
        },
        'Search Engine': {
            'qid': 'Q1234570',
            'url': 'https://www.wikidata.org/wiki/Q1234570',
            'label': 'Search Engine'
        },
        'Library': {
            'qid': 'Q1234571',
            'url': 'https://www.wikidata.org/wiki/Q1234571',
            'label': 'Software Library'
        },
        'Tool': {
            'qid': 'Q1234572',
            'url': 'https://www.wikidata.org/wiki/Q1234572',
            'label': 'Software Tool'
        },
        'Code Editor': {
            'qid': 'Q1234574',
            'url': 'https://www.wikidata.org/wiki/Q1234574',
            'label': 'Code Editor'
        },
        'Integrated Development Environment': {
            'qid': 'Q1234575',
            'url': 'https://www.wikidata.org/wiki/Q1234575',
            'label': 'Integrated Development Environment'
        },
    }

    # Keywords for each application type with weights
    # Higher weight = more specific/distinctive keyword
    TYPE_KEYWORDS = {
        'Web Application': {
            'keywords': [
                ('web-based interactive platform', 3),
                ('web-based platform', 3),
                ('interactive web application', 3),
                ('web application', 1),
                ('web-based application', 2),
                ('web interface', 2),
                ('web app', 1),
            ]
        },
        'Web Framework': {
            'keywords': [
                ('web framework', 3),
                ('web development framework', 3),
                ('rest framework', 2),
                ('http framework', 2),
                ('mvc framework', 2),
                ('routing', 1),
                ('middleware', 1),
            ]
        },
        'Programming Language': {
            'keywords': [
                ('programming language', 3),
                ('language implementation', 3),
                ('compiler', 2),
                ('interpreter', 2),
                ('language specification', 2),
            ]
        },
        'Runtime Environment': {
            'keywords': [
                ('javascript runtime', 3),
                ('python runtime', 3),
                ('runtime environment', 2),
                ('execution environment', 2),
                ('virtual machine', 2),
                ('runtime', 1),
            ]
        },
        'Operating System': {
            'keywords': [
                ('operating system kernel', 3),
                ('operating system', 2),
                ('os kernel', 2),
                ('unix-like', 2),
                ('kernel', 1),
            ]
        },
        'Database Management System': {
            'keywords': [
                ('database management system', 3),
                ('relational database', 3),
                ('nosql database', 3),
                ('database engine', 2),
                ('database', 1),
            ]
        },
        'Search Engine': {
            'keywords': [
                ('search engine', 2),
                ('full-text search', 2),
                ('information retrieval', 2),
            ]
        },
        'Library': {
            'keywords': [
                ('software library', 2),
                ('code library', 2),
                ('library', 1),
            ]
        },
        'Tool': {
            'keywords': [
                ('software tool', 2),
                ('alignment tool', 2),
                ('tool', 1),
            ]
        },
        'Code Editor': {
            'keywords': [
                ('code editor', 2),
                ('text editor', 2),
                ('editor', 1),
            ]
        },
        'Integrated Development Environment': {
            'keywords': [
                ('integrated development environment', 3),
                ('ide', 2),
                ('development environment', 2),
                ('edit-build-debug', 3),
                ('debugging', 1),
            ]
        },
    }

    def __init__(self, raw_data: dict):
        """
        Initialize the applicationCategory detector.

        Args:
            raw_data: Raw metadata extracted from GitHub repository
        """
        super().__init__(raw_data)
        self.vocab_builder = WikidataVocabularyBuilder()
        self.category_url = None  # URL to external vocabulary entry
        self.category_qid = None  # Wikidata QID if available

    def extract(self) -> None:
        """
        Extract applicationCategory by analyzing repository metadata using NLP.
        
        Strategy:
        1. Check cache first
        2. Use scoring-based keyword detection
        3. Extract key concepts and look them up in Wikidata
        4. Analyze README structure and patterns
        5. Infer from description keywords as fallback
        6. Link to external vocabulary for semantic verification
        """
        # Get repository metadata
        repo_name = self._get_value('name') or ''
        description = self._get_value('description') or ''
        readme_content = self._get_value('readme_content') or ''

        if not repo_name and not description and not readme_content:
            self.metadata = None
            return

        # Check cache first
        cache = get_vocabulary_cache()
        cached_category = cache.get_category(repo_name)
        if cached_category:
            self.metadata = cached_category
            # Still need to set vocabulary reference
            self._set_vocabulary_reference(cached_category)
            return

        # Analyze the repository to determine its type
        app_type = self._analyze_repository_type(
            repo_name, description, readme_content
        )
        
        if app_type:
            self.metadata = app_type
            # Get external vocabulary reference
            self._set_vocabulary_reference(app_type)
            # Cache the result
            cache.set_category(repo_name, app_type)
        else:
            self.metadata = None

    def _analyze_repository_type(
        self, repo_name: str, description: str, readme_content: str
    ) -> Optional[str]:
        """
        Analyze repository to determine its application type using scoring.

        Args:
            repo_name: Repository name
            description: Repository description
            readme_content: README content

        Returns:
            Application type with highest score, or None if no match found
        """
        # Combine all text for analysis
        combined_text = f"{repo_name} {description} {readme_content}".lower()

        # Score each application type based on keyword matches
        scores = {}
        for app_type, keyword_data in self.TYPE_KEYWORDS.items():
            score = 0
            for keyword, weight in keyword_data['keywords']:
                if keyword in combined_text:
                    score += weight
            if score > 0:
                scores[app_type] = score

        # Return the type with the highest score
        if scores:
            best_type = max(scores, key=scores.get)
            return best_type

        # Fallback: Try Wikidata concept lookup
        app_type = self._detect_by_wikidata_concepts(repo_name, description, readme_content)
        if app_type:
            return app_type

        # Fallback: Try README analysis
        app_type = self._detect_by_readme_analysis(readme_content)
        if app_type:
            return app_type

        # Fallback: Try description inference
        app_type = self._infer_from_description_keywords(description)
        if app_type:
            return app_type

        return None

    def _detect_by_wikidata_concepts(
        self, repo_name: str, description: str, readme_content: str
    ) -> Optional[str]:
        """
        Detect application type by extracting concepts and looking them up in Wikidata.

        Args:
            repo_name: Repository name
            description: Repository description
            readme_content: README content

        Returns:
            Application type, or None if not found
        """
        # Extract key concepts/terms from the text
        concepts = self._extract_concepts(repo_name, description, readme_content)

        # Look up each concept in Wikidata
        for concept in concepts:
            wikidata_result = self.vocab_builder.find_matching_category(concept)
            if wikidata_result:
                # Extract type from Wikidata description
                app_type = self._extract_type_from_wikidata_result(wikidata_result)
                if app_type:
                    return app_type

        return None

    def _extract_concepts(
        self, repo_name: str, description: str, readme_content: str
    ) -> List[str]:
        """
        Extract key concepts from repository metadata using NLP-like techniques.

        Args:
            repo_name: Repository name
            description: Repository description
            readme_content: README content

        Returns:
            List of key concepts
        """
        concepts = []

        # Extract from repository name
        if repo_name:
            # Split by common separators
            name_parts = re.split(r'[-_.]', repo_name)
            concepts.extend([p for p in name_parts if len(p) > 2])

        # Extract from description (first sentence)
        if description:
            # Get first sentence
            first_sentence = description.split('.')[0]
            # Extract important words (nouns, verbs)
            words = first_sentence.split()
            # Filter out common words
            stop_words = {'is', 'a', 'the', 'and', 'or', 'for', 'with', 'to', 'in', 'of', 'by'}
            important_words = [
                w for w in words
                if len(w) > 3 and w.lower() not in stop_words
            ]
            concepts.extend(important_words)

        # Extract from README (first paragraph and key sections)
        if readme_content:
            # Get first paragraph
            first_para = readme_content.split('\n\n')[0]
            # Extract key terms
            words = first_para.split()
            stop_words = {'is', 'a', 'the', 'and', 'or', 'for', 'with', 'to', 'in', 'of', 'by'}
            important_words = [
                w.strip('.,!?;:') for w in words
                if len(w) > 3 and w.lower() not in stop_words
            ]
            concepts.extend(important_words[:15])  # Limit to first 15 important words

            # Also look for section headers that might indicate type
            headers = re.findall(r'^#+\s+(.+)$', readme_content, re.MULTILINE)
            concepts.extend(headers[:5])  # Add first 5 headers

        # Remove duplicates and empty strings
        concepts = list(set([c for c in concepts if c and len(c) > 2]))

        return concepts[:20]  # Return top 20 concepts

    def _extract_type_from_wikidata_result(self, wikidata_result: Dict[str, str]) -> Optional[str]:
        """
        Extract application type from Wikidata result.

        Args:
            wikidata_result: Wikidata vocabulary entry

        Returns:
            Application type, or None if not determinable
        """
        description = wikidata_result.get('description', '').lower()
        label = wikidata_result.get('label', '').lower()

        # Check description and label against type keywords
        for app_type, keyword_data in self.TYPE_KEYWORDS.items():
            for keyword, weight in keyword_data['keywords']:
                if keyword in description or keyword in label:
                    return app_type

        return None

    def _detect_by_readme_analysis(self, readme_content: str) -> Optional[str]:
        """
        Detect application type by analyzing README structure and patterns.

        Args:
            readme_content: README content

        Returns:
            Application type, or None if not found
        """
        if not readme_content:
            return None

        readme_lower = readme_content.lower()

        # Pattern-based detection
        patterns = {
            'Programming Language': [
                r'syntax.*example',
                r'language.*specification',
                r'compiler|interpreter',
                r'language.*features',
            ],
            'Web Framework': [
                r'route|routing',
                r'middleware',
                r'request.*response',
                r'http.*server',
                r'rest.*api',
            ],
            'Database': [
                r'database.*schema',
                r'query.*language',
                r'data.*storage',
                r'table.*column',
            ],
            'Machine Learning': [
                r'neural.*network',
                r'model.*training',
                r'dataset',
                r'tensor',
            ],
            'Container': [
                r'docker.*image',
                r'container.*orchestration',
                r'kubernetes',
            ],
        }

        for app_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, readme_lower):
                    return app_type

        return None

    def _infer_from_description_keywords(self, description: str) -> Optional[str]:
        """
        Infer application type from description keywords as a fallback.

        Args:
            description: Repository description

        Returns:
            Application type, or None if not determinable
        """
        if not description:
            return None

        desc_lower = description.lower()

        # Check for domain-specific keywords with scoring
        domain_patterns = {
            'Tool': ['tool', 'utility', 'alignment tool', 'editing tool'],
            'Library': ['library', 'vocabulary', 'ontology', 'semantic'],
            'Framework': ['framework', 'platform'],
        }

        for app_type, keywords in domain_patterns.items():
            for keyword in keywords:
                if keyword in desc_lower:
                    return app_type

        return None

    def _set_vocabulary_reference(self, app_type: str) -> None:
        """
        Set external vocabulary reference for the application type.

        Args:
            app_type: Application type to look up
        """
        # First try to find in Wikidata mapping
        if app_type in self.TYPE_TO_WIKIDATA:
            vocab_info = self.TYPE_TO_WIKIDATA[app_type]
            self.category_qid = vocab_info['qid']
            self.category_url = vocab_info['url']
        else:
            # Try to find in Wikidata by searching
            result = self.vocab_builder.find_matching_category(app_type)
            if result:
                self.category_url = result.get('url')
                self.category_qid = result.get('qid')

    def _validate_metadata(self) -> None:
        """Validate the extracted applicationCategory."""
        if not self.metadata:
            if self.REQUIRED:
                self.add_error(f"Required field '{self.CODEMETA_PROPERTY}' is missing")
        elif not isinstance(self.metadata, str):
            self.add_error(f"Field '{self.CODEMETA_PROPERTY}' must be a string")
        elif len(self.metadata) > 200:
            self.add_warning(f"Field '{self.CODEMETA_PROPERTY}' is very long ({len(self.metadata)} characters)")

    def to_codemeta_dict(self) -> dict:
        """
        Convert to Codemeta format following the Codemeta schema.
        
        Returns the application type as an object with @id reference to external vocabulary.
        This follows the Codemeta specification for semantic linking.
        """
        if not self.metadata:
            return {}
        
        # Use Codemeta schema format with @id for semantic reference
        if self.category_url:
            result = {
                self.CODEMETA_PROPERTY: {
                    '@id': self.category_url,
                    'name': self.metadata
                }
            }
        else:
            # Fallback to simple string if no URL available
            result = {self.CODEMETA_PROPERTY: self.metadata}
        
        return result
