"""
Wikidata Keyword Resolver

Resolves keywords to Wikidata entities with context-aware disambiguation for homonyms.
Uses SPARQL queries to find matching entities and their descriptions.
Implements domain-aware semantic context analysis for better accuracy.
"""

import requests
import json
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote
from src.domain_keyword_mapping import DomainKeywordMapper


class WikidataKeywordResolver:
    """Resolves keywords to Wikidata entities with disambiguation."""

    WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
    WIKIDATA_ENTITY_URL = "https://www.wikidata.org/wiki"
    
    # Cache for resolved keywords
    _cache = {}

    def __init__(self):
        """Initialize the resolver."""
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'CodemetaGenerator/1.0'})

    def resolve_keyword(self, keyword: str, context: str = "") -> Optional[Dict[str, str]]:
        """
        Resolve a keyword to a Wikidata entity.

        Uses domain-aware mapping first, then falls back to Wikidata search.

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

        # Try domain-specific mapping first
        domain = DomainKeywordMapper.detect_domain(context)
        domain_mapping = DomainKeywordMapper.get_domain_mapping(keyword, domain)
        
        if domain_mapping:
            result = {
                'qid': domain_mapping['qid'],
                'url': domain_mapping['url'],
                'label': domain_mapping['label'],
                'description': domain_mapping['description']
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
        Search Wikidata for the keyword.

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
                'limit': 20  # Get more results for better disambiguation
            }
            
            response = self.session.get(search_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('search'):
                return None
            
            # Get top results
            results = data['search']
            
            # If only one result, use it
            if len(results) == 1:
                return self._format_entity(results[0])
            
            # If multiple results, use context to disambiguate
            if len(results) > 1 and context:
                best_match = self._disambiguate_results(results, keyword, context)
                if best_match:
                    return self._format_entity(best_match)
            
            # Default to first result
            return self._format_entity(results[0])
            
        except Exception as e:
            print(f"Error searching Wikidata for '{keyword}': {e}")
            return None

    def _extract_domain_keywords(self, context: str) -> List[str]:
        """
        Extract domain-specific keywords from context.
        
        Identifies specialized domains like:
        - Semantic web: SKOS, RDF, ontology, semantic web
        - Knowledge representation: knowledge graph, alignment, mapping
        - Data science: machine learning, neural network
        - Web development: framework, API, REST

        Args:
            context: Repository context string

        Returns:
            List of domain keywords found in context
        """
        domain_keywords = []
        context_lower = context.lower()
        
        # Domain-specific keyword sets
        semantic_web_keywords = ['skos', 'rdf', 'ontology', 'semantic', 'linked data', 
                                'knowledge graph', 'knowledge representation', 'owl']
        alignment_keywords = ['alignment', 'mapping', 'match', 'reconciliation']
        ml_keywords = ['machine learning', 'neural', 'deep learning', 'tensorflow', 'pytorch']
        web_keywords = ['api', 'rest', 'http', 'web service', 'framework']
        
        all_domain_sets = [
            semantic_web_keywords,
            alignment_keywords,
            ml_keywords,
            web_keywords
        ]
        
        for keyword_set in all_domain_sets:
            for kw in keyword_set:
                if kw in context_lower:
                    domain_keywords.append(kw)
        
        return domain_keywords

    def _disambiguate_results(self, results: List[Dict], keyword: str, context: str) -> Optional[Dict]:
        """
        Disambiguate multiple Wikidata results using deep semantic context.

        Uses multiple strategies:
        1. Exact label match
        2. Domain-specific context analysis (SKOS, semantic web, ontology, etc.)
        3. Description relevance to repository context
        4. Software/technology domain preference
        5. Filtering out non-software entities

        Args:
            results: List of Wikidata search results
            keyword: The original keyword
            context: Repository context

        Returns:
            Best matching result or None
        """
        context_lower = context.lower()
        
        # Extract domain-specific keywords from context
        domain_keywords = self._extract_domain_keywords(context_lower)
        
        # Filter out clearly non-software results
        filtered_results = self._filter_non_software_results(results)
        if not filtered_results:
            filtered_results = results  # Fallback if all filtered
        
        # Score each result based on description relevance to context
        scored_results = []
        
        for result in filtered_results:
            score = 0
            description = result.get('description', '').lower()
            label = result.get('label', '').lower()
            
            # Exact label match
            if label == keyword.lower():
                score += 20
            
            # Penalize non-software entities
            non_software_keywords = ['family name', 'given name', 'television', 'tv series', 
                                    'film', 'movie', 'person', 'people', 'place', 'city', 
                                    'country', 'band', 'music', 'song', 'album', 'bioinformatics',
                                    'patent', 'data import']
            for non_sw in non_software_keywords:
                if non_sw in description:
                    score -= 15
            
            # Domain-specific scoring (SKOS, semantic web, ontology, etc.)
            if domain_keywords:
                for domain_kw in domain_keywords:
                    if domain_kw in description:
                        score += 5  # High boost for domain-specific matches
                    if domain_kw in label:
                        score += 6
            
            # Check if description contains context keywords
            context_keywords = [w for w in context_lower.split() if len(w) > 3]
            for ctx_word in context_keywords[:15]:  # Check first 15 context words
                if ctx_word in description:
                    score += 3
                if ctx_word in label:
                    score += 4
            
            # Prefer software/technology related descriptions
            software_keywords = ['software', 'programming', 'computer', 'algorithm', 'framework', 
                               'library', 'tool', 'application', 'system', 'protocol', 'language',
                               'interface', 'feature', 'function', 'module', 'component',
                               'user interface', 'ui', 'graphical', 'display', 'color scheme',
                               'knowledge', 'semantic', 'ontology', 'vocabulary', 'mapping',
                               'alignment', 'representation']
            for sw_keyword in software_keywords:
                if sw_keyword in description:
                    score += 2
            
            scored_results.append((score, result))
        
        # Return result with highest score
        if scored_results:
            scored_results.sort(key=lambda x: x[0], reverse=True)
            return scored_results[0][1]
        
        return None

    def _filter_non_software_results(self, results: List[Dict]) -> List[Dict]:
        """
        Filter out clearly non-software results.

        Args:
            results: List of Wikidata search results

        Returns:
            Filtered list of potentially software-related results
        """
        filtered = []
        
        for result in results:
            description = result.get('description', '').lower()
            
            # Skip obvious non-software entities
            non_software_keywords = ['family name', 'given name', 'television', 'tv series', 
                                    'film', 'movie', 'person', 'people', 'place', 'city', 
                                    'country', 'band', 'music', 'song', 'album', 'bioinformatics',
                                    'patent']
            
            is_non_software = any(keyword in description for keyword in non_software_keywords)
            
            if not is_non_software:
                filtered.append(result)
        
        return filtered

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

    @staticmethod
    def get_domain_mapper() -> DomainKeywordMapper:
        """Get the domain keyword mapper."""
        return DomainKeywordMapper()
