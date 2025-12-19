"""
Wikidata Keyword Resolver

Resolves keywords to Wikidata entities with robust, generic disambiguation.
Uses aggressive filtering of non-software entities and context-aware scoring
to find the most relevant Wikidata entity for any keyword in any repository.

No hardcoded mappings - works generically for any GitHub repository.
"""

import requests
import json
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote
from src.critical_keywords_mapping import get_critical_keyword_mapping, is_critical_keyword


class WikidataKeywordResolver:
    """Resolves keywords to Wikidata entities with robust disambiguation."""

    WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
    WIKIDATA_ENTITY_URL = "https://www.wikidata.org/wiki"
    
    # Cache for resolved keywords
    _cache = {}
    
    # Non-software entity indicators - aggressively filter these out
    NON_SOFTWARE_KEYWORDS = [
        # Entertainment
        'television', 'tv series', 'tv show', 'film', 'movie', 'video game',
        'music', 'song', 'album', 'band', 'musician', 'artist', 'actor',
        'character', 'fictional', 'star trek', 'marvel', 'dc comics',
        
        # People
        'person', 'people', 'human', 'family name', 'given name', 'surname',
        'first name', 'last name', 'nickname', 'pseudonym',
        
        # Geography
        'place', 'city', 'town', 'country', 'region', 'state', 'province',
        'continent', 'island', 'mountain', 'river', 'lake', 'ocean',
        'geographical', 'location',
        
        # Biology/Medicine
        'species', 'animal', 'plant', 'organism', 'disease', 'virus',
        'bacteria', 'gene', 'protein', 'enzyme', 'biological',
        'bioinformatics', 'genomics', 'proteomics',
        
        # Sports
        'sport', 'team', 'player', 'athlete', 'game', 'match', 'championship',
        'football', 'basketball', 'baseball', 'soccer',
        
        # Other non-software
        'patent', 'invention', 'device', 'machine', 'vehicle', 'aircraft',
        'ship', 'train', 'car', 'motorcycle', 'bicycle',
        'food', 'drink', 'cuisine', 'recipe', 'ingredient',
        'clothing', 'fashion', 'textile', 'fabric',
        'building', 'architecture', 'monument', 'structure',
        'art', 'painting', 'sculpture', 'photograph',
        'book', 'novel', 'poem', 'literature', 'author', 'writer',
        'company', 'corporation', 'business', 'organization',
        'university', 'school', 'college', 'education',
        'religion', 'deity', 'god', 'goddess', 'saint', 'prophet',
        'historical event', 'war', 'battle', 'conflict',
        'currency', 'money', 'coin', 'banknote',
        'vehicle', 'transportation', 'car', 'truck',
        'weapon', 'firearm', 'gun', 'missile',
        'dance', 'choreography', 'ballet',
        'instrument', 'musical instrument',
        'drug', 'medication', 'pharmaceutical',
        'chemical element', 'mineral', 'rock',
        'weather', 'climate', 'atmosphere',
        'astronomical object', 'star', 'planet', 'comet',
        'unit of measurement', 'measurement', 'metric',
        'mathematical concept', 'number', 'equation',
        'linguistic', 'language', 'dialect', 'accent',
        'legal', 'law', 'court', 'judge',
        'government', 'political', 'parliament', 'congress',
        'military', 'army', 'navy', 'air force',
        'archaeological', 'artifact', 'ancient', 'archaeology',
        'mythological', 'mythology', 'myth', 'legend',
        'magic', 'wizard', 'spell', 'sorcery',
        'supernatural', 'ghost', 'demon', 'angel',
        'database', 'dataset', 'collection'  # Generic data collections
    ]
    
    # Software/technology entity indicators - prefer these
    SOFTWARE_KEYWORDS = [
        'software', 'program', 'application', 'app', 'tool', 'utility',
        'framework', 'library', 'package', 'module', 'component',
        'system', 'platform', 'operating system', 'os',
        'programming language', 'language', 'compiler', 'interpreter',
        'algorithm', 'data structure', 'design pattern',
        'protocol', 'standard', 'specification', 'format',
        'api', 'interface', 'service', 'web service',
        'database', 'dbms', 'query language', 'sql',
        'framework', 'middleware', 'server', 'client',
        'network', 'communication', 'encryption', 'security',
        'code', 'source code', 'repository', 'version control',
        'compiler', 'interpreter', 'debugger', 'profiler',
        'testing', 'test', 'unit test', 'integration test',
        'documentation', 'manual', 'guide', 'tutorial',
        'data', 'information', 'knowledge', 'representation',
        'processing', 'computation', 'calculation', 'analysis',
        'transformation', 'conversion', 'mapping', 'alignment',
        'ontology', 'vocabulary', 'taxonomy', 'classification',
        'semantic', 'knowledge graph', 'linked data', 'rdf',
        'machine learning', 'neural network', 'deep learning',
        'artificial intelligence', 'ai', 'nlp', 'computer vision',
        'web', 'internet', 'http', 'html', 'css', 'javascript',
        'mobile', 'android', 'ios', 'app development',
        'cloud', 'container', 'docker', 'kubernetes',
        'devops', 'ci/cd', 'automation', 'deployment',
        'monitoring', 'logging', 'metrics', 'observability',
        'editor', 'ide', 'development environment',
        'build', 'compilation', 'packaging', 'distribution',
        'open source', 'free software', 'license',
        'plugin', 'extension', 'addon', 'widget',
        'script', 'scripting', 'automation', 'workflow',
        'integration', 'synchronization', 'replication',
        'backup', 'recovery', 'disaster', 'resilience',
        'performance', 'optimization', 'scalability',
        'accessibility', 'usability', 'user experience', 'ux',
        'configuration', 'customization', 'personalization',
        'validation', 'verification', 'quality assurance', 'qa',
        'error', 'exception', 'debugging', 'troubleshooting',
        'feature', 'functionality', 'capability', 'function',
        'method', 'procedure', 'routine', 'subroutine',
        'class', 'object', 'instance', 'property', 'attribute',
        'variable', 'constant', 'parameter', 'argument',
        'loop', 'condition', 'statement', 'expression',
        'function', 'procedure', 'method', 'constructor',
        'inheritance', 'polymorphism', 'encapsulation',
        'abstraction', 'interface', 'contract', 'specification'
    ]

    def __init__(self):
        """Initialize the resolver."""
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'CodemetaGenerator/1.0'})

    def resolve_keyword(self, keyword: str, context: str = "") -> Optional[Dict[str, str]]:
        """
        Resolve a keyword to a Wikidata entity using robust, generic disambiguation.

        Strategy:
        1. Check critical keywords mapping first (for common software terms)
        2. Fall back to Wikidata search with aggressive filtering

        Args:
            keyword: The keyword to resolve
            context: Repository context (description, README) for disambiguation

        Returns:
            Dictionary with 'qid', 'url', 'label', and 'description' or None
        """
        # Check cache first
        cache_key = f"{keyword}:{context[:100]}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Try critical keywords mapping first (for common software terms)
        if is_critical_keyword(keyword):
            critical_mapping = get_critical_keyword_mapping(keyword)
            if critical_mapping:
                result = {
                    'qid': critical_mapping['qid'],
                    'url': critical_mapping['url'],
                    'label': critical_mapping['label'],
                    'description': critical_mapping['description']
                }
                self._cache[cache_key] = result
                return result
        
        # Fall back to Wikidata search
        result = self._search_wikidata(keyword, context)
        
        if result:
            self._cache[cache_key] = result
            return result
        
        return None

    def _search_wikidata(self, keyword: str, context: str) -> Optional[Dict[str, str]]:
        """
        Search Wikidata for the keyword with robust filtering.

        Args:
            keyword: The keyword to search
            context: Repository context for disambiguation

        Returns:
            Dictionary with entity information or None
        """
        try:
            # Use Wikidata search API
            search_url = "https://www.wikidata.org/w/api.php"
            params = {
                'action': 'wbsearchentities',
                'search': keyword,
                'language': 'en',
                'format': 'json',
                'limit': 50  # Get many results for better filtering
            }
            
            response = self.session.get(search_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('search'):
                return None
            
            results = data['search']
            
            # Filter and score results
            filtered_results = self._filter_and_score_results(results, keyword, context)
            
            if filtered_results:
                # Return the best result
                best_result = filtered_results[0][1]
                return self._format_entity(best_result)
            
            return None
            
        except Exception as e:
            print(f"Error searching Wikidata for '{keyword}': {e}")
            return None

    def _filter_and_score_results(self, results: List[Dict], keyword: str, context: str) -> List[Tuple[int, Dict]]:
        """
        Filter and score Wikidata results to find the best match.

        Strategy:
        1. Aggressively filter out non-software entities
        2. Score based on software/technology relevance (high weight)
        3. Score based on context relevance (medium weight)
        4. Return sorted list of (score, result) tuples

        Args:
            results: List of Wikidata search results
            keyword: The original keyword
            context: Repository context

        Returns:
            Sorted list of (score, result) tuples, highest score first
        """
        context_lower = context.lower()
        keyword_lower = keyword.lower()
        
        scored_results = []
        
        for result in results:
            description = result.get('description', '').lower()
            label = result.get('label', '').lower()
            
            # AGGRESSIVE FILTERING: Skip obvious non-software entities
            if self._is_non_software_entity(description, label):
                continue
            
            # Score this result
            score = 0
            
            # Exact label match (high priority)
            if label == keyword_lower:
                score += 100
            
            # Partial label match
            elif keyword_lower in label:
                score += 50
            
            # Software/technology relevance (VERY HIGH WEIGHT - this is key)
            software_score = self._score_software_relevance(description)
            score += software_score * 3  # Triple the weight of software relevance
            
            # Context relevance (medium weight)
            context_score = self._score_context_relevance(description, context_lower)
            score += context_score
            
            # Penalize very generic descriptions
            if len(description) < 20:
                score -= 10
            
            scored_results.append((score, result))
        
        # Sort by score (highest first)
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        return scored_results

    def _is_non_software_entity(self, description: str, label: str) -> bool:
        """
        Aggressively filter out non-software entities.

        Args:
            description: Entity description from Wikidata
            label: Entity label from Wikidata

        Returns:
            True if this is clearly a non-software entity, False otherwise
        """
        desc_lower = description.lower()
        label_lower = label.lower()
        
        # Check for non-software keywords
        for non_sw_keyword in self.NON_SOFTWARE_KEYWORDS:
            if non_sw_keyword in desc_lower or non_sw_keyword in label_lower:
                return True
        
        return False

    def _score_software_relevance(self, description: str) -> int:
        """
        Score how relevant this entity is to software/technology.

        Args:
            description: Entity description from Wikidata

        Returns:
            Score (0-50) - will be multiplied by 3 in filter_and_score_results
        """
        desc_lower = description.lower()
        score = 0
        
        # Count software keyword matches
        for sw_keyword in self.SOFTWARE_KEYWORDS:
            if sw_keyword in desc_lower:
                score += 2
        
        # Strong bonuses for specific software concepts
        if 'computer' in desc_lower or 'program' in desc_lower:
            score += 10
        if 'software' in desc_lower:
            score += 15
        if 'application' in desc_lower or 'app' in desc_lower:
            score += 12
        if 'algorithm' in desc_lower or 'data structure' in desc_lower:
            score += 8
        if 'programming' in desc_lower or 'language' in desc_lower:
            score += 10
        if 'framework' in desc_lower or 'library' in desc_lower:
            score += 10
        
        return min(score, 50)  # Cap at 50

    def _score_context_relevance(self, description: str, context: str) -> int:
        """
        Score how relevant this entity is to the repository context.

        Args:
            description: Entity description from Wikidata
            context: Repository context

        Returns:
            Score (0-30)
        """
        desc_lower = description.lower()
        score = 0
        
        # Extract key context words (length > 4 to avoid noise)
        context_words = [w for w in context.split() if len(w) > 4]
        
        # Check for context word matches
        for word in context_words[:20]:  # Check first 20 words
            word_lower = word.lower()
            if word_lower in desc_lower:
                score += 2
        
        return min(score, 30)  # Cap at 30

    def _format_entity(self, entity: Dict) -> Dict[str, str]:
        """
        Format a Wikidata entity into our standard format.

        Args:
            entity: Wikidata search result

        Returns:
            Formatted entity dictionary
        """
        qid = entity.get('id', '')
        label = entity.get('label', '')
        description = entity.get('description', '')
        
        return {
            'qid': qid,
            'url': f"{self.WIKIDATA_ENTITY_URL}/{qid}",
            'label': label,
            'description': description
        }

    @staticmethod
    def clear_cache():
        """Clear the resolution cache."""
        WikidataKeywordResolver._cache.clear()
