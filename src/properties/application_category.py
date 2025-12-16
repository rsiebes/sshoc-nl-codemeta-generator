"""
Application Category Property Module

This module detects the applicationCategory property for ANY software by using:
1. NLP to extract key concepts from README and description
2. External vocabularies (Wikidata) to understand what those concepts are
3. Classification logic to determine the application type

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

    # Keywords that indicate specific application types
    TYPE_KEYWORDS = {
        'Tool': [
            'tool', 'utility', 'utility tool', 'software tool',
            'alignment tool', 'editing tool', 'management tool'
        ],
        'Programming Language': [
            'programming language', 'language implementation', 'compiler', 'interpreter',
            'language', 'scripting language', 'language runtime', 'language specification'
        ],
        'Web Framework': [
            'web framework', 'web application', 'http framework', 'rest framework',
            'web development', 'web server', 'web application framework', 'mvc framework',
            'web api', 'web service'
        ],
        'Runtime Environment': [
            'runtime', 'execution environment', 'virtual machine', 'runtime system',
            'runtime environment', 'javascript runtime', 'python runtime'
        ],
        'Operating System': [
            'operating system', 'kernel', 'os implementation', 'unix-like',
            'operating system kernel', 'system kernel', 'os kernel'
        ],
        'Database Management System': [
            'database', 'relational database', 'nosql', 'data storage',
            'database system', 'database management', 'database engine'
        ],
        'Search Engine': [
            'search engine', 'full-text search', 'information retrieval',
            'search platform', 'search technology'
        ],
        'Container Platform': [
            'container', 'containerization', 'docker', 'container technology',
            'container platform'
        ],
        'Container Orchestration Platform': [
            'orchestration', 'kubernetes', 'container orchestration',
            'orchestration platform', 'container orchestration system'
        ],
        'Version Control System': [
            'version control', 'source control', 'scm', 'version control system',
            'distributed version control'
        ],
        'Code Repository Platform': [
            'code repository', 'repository platform', 'git hosting',
            'repository hosting', 'code hosting'
        ],
        'Continuous Integration Platform': [
            'continuous integration', 'ci/cd', 'ci pipeline', 'build automation',
            'continuous deployment', 'automation platform'
        ],
        'Machine Learning Framework': [
            'machine learning', 'deep learning', 'neural network', 'ml framework',
            'machine learning framework', 'deep learning framework',
            'tensorflow', 'pytorch', 'keras'
        ],
        'Library': [
            'library', 'code library', 'software library', 'utility library',
            'helper library', 'support library', 'vocabulary library',
            'semantic library', 'ontology library'
        ],
        'Framework': [
            'framework', 'application framework', 'software framework',
            'development framework'
        ],
    }

    def __init__(self, raw_data: dict):
        """
        Initialize the applicationCategory detector.

        Args:
            raw_data: Raw metadata extracted from GitHub repository
        """
        super().__init__(raw_data)
        self.vocab_builder = WikidataVocabularyBuilder()

    def extract(self) -> None:
        """
        Extract applicationCategory by analyzing repository metadata using NLP.
        
        Strategy:
        1. Extract key concepts from README, description, and repository name
        2. Use Wikidata to understand what these concepts are
        3. Classify the application type based on found concepts
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
            return

        # Analyze the repository to determine its type
        app_type = self._analyze_repository_type(
            repo_name, description, readme_content
        )
        
        if app_type:
            self.metadata = app_type
            # Cache the result
            cache.set_category(repo_name, app_type)
        else:
            self.metadata = None

    def _analyze_repository_type(
        self, repo_name: str, description: str, readme_content: str
    ) -> Optional[str]:
        """
        Analyze repository to determine its application type.

        Args:
            repo_name: Repository name
            description: Repository description
            readme_content: README content

        Returns:
            Application type (e.g., "Web Framework", "Programming Language"), or None
        """
        # Combine all text for analysis
        combined_text = f"{repo_name} {description} {readme_content}".lower()

        # Strategy 1: Check for direct type keywords
        app_type = self._detect_by_keywords(combined_text)
        if app_type:
            return app_type

        # Strategy 2: Extract key concepts and look them up in Wikidata
        app_type = self._detect_by_wikidata_concepts(repo_name, description, readme_content)
        if app_type:
            return app_type

        # Strategy 3: Analyze README structure and content patterns
        app_type = self._detect_by_readme_analysis(readme_content)
        if app_type:
            return app_type

        # Strategy 4: Infer from description keywords as fallback
        app_type = self._infer_from_description_keywords(description)
        if app_type:
            return app_type

        return None

    def _detect_by_keywords(self, combined_text: str) -> Optional[str]:
        """
        Detect application type by checking for type-specific keywords.

        Args:
            combined_text: Combined text from all sources

        Returns:
            Application type, or None if not found
        """
        # Check each type's keywords
        for app_type, keywords in self.TYPE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in combined_text:
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
        for app_type, keywords in self.TYPE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in description or keyword in label:
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

        # Check for domain-specific keywords
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
        Convert to Codemeta format.
        
        Returns the application type as the main property.
        """
        if not self.metadata:
            return {}
        
        return {self.CODEMETA_PROPERTY: self.metadata}
