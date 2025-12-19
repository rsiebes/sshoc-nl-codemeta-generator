"""
Organization URL Resolver

Resolves organization names to their official URLs using online search strategies:
1. Wikidata lookup for known organizations
2. Google search with domain extraction
3. ROR (Research Organization Registry) API for academic institutions
4. Web search with intelligent domain matching

This module helps enrich author affiliations with organization URLs.
"""

import requests
import json
import re
from typing import Dict, Optional, Tuple
from urllib.parse import quote, urlparse
from functools import lru_cache


class OrganizationURLResolver:
    """Resolves organization names to their official URLs using online searches."""

    # Wikidata SPARQL endpoint for organization lookups
    WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
    
    # ROR (Research Organization Registry) API
    ROR_API = "https://api.ror.org/organizations"
    
    # Google Custom Search (using public search)
    GOOGLE_SEARCH_API = "https://www.google.com/search"
    
    # DuckDuckGo API
    DUCKDUCKGO_API = "https://duckduckgo.com/api/v1/search"
    
    # Cache for resolved organizations
    _cache = {}
    
    def __init__(self, timeout: int = 5):
        """
        Initialize the resolver.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
    
    def resolve_organization_url(self, organization_name: Optional[str]) -> Optional[str]:
        """
        Resolve an organization name to its URL using multiple strategies.
        
        Args:
            organization_name: Name of the organization
            
        Returns:
            URL of the organization or None if not found
        """
        if not organization_name or not isinstance(organization_name, str):
            return None
        
        org_name = organization_name.strip()
        
        if not org_name:
            return None
        
        org_name_lower = org_name.lower()
        
        # Check cache first
        if org_name_lower in self._cache:
            return self._cache[org_name_lower]
        
        # Try multiple lookup strategies in order
        url = None
        
        # Strategy 1: Wikidata lookup
        url = self._lookup_wikidata_organization(org_name)
        if url:
            self._cache[org_name_lower] = url
            return url
        
        # Strategy 2: ROR (Research Organization Registry) - for academic institutions
        url = self._lookup_ror_organization(org_name)
        if url:
            self._cache[org_name_lower] = url
            return url
        
        # Strategy 3: Web search with domain extraction
        url = self._search_organization_url(org_name)
        if url:
            self._cache[org_name_lower] = url
            return url
        
        # Cache the failure to avoid repeated lookups
        self._cache[org_name_lower] = None
        return None
    
    def _lookup_wikidata_organization(self, org_name: str) -> Optional[str]:
        """
        Look up organization in Wikidata.
        
        Args:
            org_name: Organization name
            
        Returns:
            Organization URL or None
        """
        try:
            # Try exact match first
            sparql_query = f"""
            SELECT ?org ?website WHERE {{
              ?org rdfs:label "{org_name}"@en ;
                   wdt:P31 wd:Q43229 .  # instance of organization
              OPTIONAL {{ ?org wdt:P856 ?website . }}
            }}
            LIMIT 3
            """
            
            response = requests.get(
                self.WIKIDATA_SPARQL_ENDPOINT,
                params={
                    'query': sparql_query,
                    'format': 'json'
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', {}).get('bindings', [])
                
                # Return the first website found
                for result in results:
                    if 'website' in result:
                        website = result['website'].get('value', '').strip()
                        if website and self._is_valid_url(website):
                            return self._normalize_url(website)
            
            # Try fuzzy match with SPARQL text search
            sparql_query_fuzzy = f"""
            SELECT ?org ?website WHERE {{
              ?org rdfs:label ?label ;
                   wdt:P31 wd:Q43229 .
              FILTER(CONTAINS(LCASE(?label), LCASE("{org_name}")))
              OPTIONAL {{ ?org wdt:P856 ?website . }}
            }}
            LIMIT 3
            """
            
            response = requests.get(
                self.WIKIDATA_SPARQL_ENDPOINT,
                params={
                    'query': sparql_query_fuzzy,
                    'format': 'json'
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', {}).get('bindings', [])
                
                for result in results:
                    if 'website' in result:
                        website = result['website'].get('value', '').strip()
                        if website and self._is_valid_url(website):
                            return self._normalize_url(website)
            
        except Exception as e:
            # Silently fail and try next method
            pass
        
        return None
    
    def _lookup_ror_organization(self, org_name: str) -> Optional[str]:
        """
        Look up organization in ROR (Research Organization Registry).
        
        Args:
            org_name: Organization name
            
        Returns:
            Organization URL or None
        """
        try:
            # Search ROR API
            response = requests.get(
                self.ROR_API,
                params={
                    'query': org_name,
                    'affiliation': True
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                # Return the first organization's URL
                for item in items:
                    if 'links' in item and len(item['links']) > 0:
                        url = item['links'][0]
                        if url and self._is_valid_url(url):
                            return self._normalize_url(url)
                    
                    # Try to get website from organization data
                    if 'wikipedia_url' in item:
                        url = item['wikipedia_url']
                        if url and self._is_valid_url(url):
                            return self._normalize_url(url)
            
        except Exception as e:
            # Silently fail and try next method
            pass
        
        return None
    
    def _search_organization_url(self, org_name: str) -> Optional[str]:
        """
        Search for organization URL using multiple search engines.
        
        Args:
            org_name: Organization name
            
        Returns:
            Organization URL or None
        """
        # Try DuckDuckGo first (privacy-friendly)
        url = self._search_duckduckgo(org_name)
        if url:
            return url
        
        # Try Bing search as fallback
        url = self._search_bing(org_name)
        if url:
            return url
        
        return None
    
    def _search_duckduckgo(self, org_name: str) -> Optional[str]:
        """
        Search for organization using DuckDuckGo.
        
        Args:
            org_name: Organization name
            
        Returns:
            Organization URL or None
        """
        try:
            # Search with multiple query strategies
            search_queries = [
                f'"{org_name}" official website',
                f'"{org_name}" homepage',
                f'{org_name} organization website',
            ]
            
            for search_query in search_queries:
                response = requests.get(
                    self.DUCKDUCKGO_API,
                    params={
                        'q': search_query,
                        'format': 'json'
                    },
                    timeout=self.timeout,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check direct results
                    results = data.get('Results', [])
                    for result in results:
                        url = result.get('FirstURL', '').strip()
                        if url and self._is_valid_url(url):
                            domain = self._extract_domain(url)
                            if domain and self._matches_organization_name(domain, org_name, strict=True):
                                return self._normalize_url(url)
                    
                    # Check related topics
                    related = data.get('RelatedTopics', [])
                    for topic in related:
                        url = topic.get('FirstURL', '').strip()
                        if url and self._is_valid_url(url):
                            domain = self._extract_domain(url)
                            if domain and self._matches_organization_name(domain, org_name, strict=True):
                                return self._normalize_url(url)
            
        except Exception as e:
            pass
        
        return None
    
    def _search_bing(self, org_name: str) -> Optional[str]:
        """
        Search for organization using Bing.
        
        Args:
            org_name: Organization name
            
        Returns:
            Organization URL or None
        """
        try:
            search_query = f'"{org_name}" official website'
            
            response = requests.get(
                "https://www.bing.com/search",
                params={
                    'q': search_query
                },
                timeout=self.timeout,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            
            if response.status_code == 200:
                # Extract URLs from HTML
                import re
                urls = re.findall(r'href=["\']?([https?://][^\s"\'<>]+)', response.text)
                
                for url in urls:
                    if self._is_valid_url(url):
                        domain = self._extract_domain(url)
                        if domain and self._matches_organization_name(domain, org_name):
                            return self._normalize_url(url)
            
        except Exception as e:
            pass
        
        return None
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Check if a string is a valid URL.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """
        Extract domain from URL.
        
        Args:
            url: Full URL
            
        Returns:
            Domain name or None
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return None
    
    def _matches_organization_name(self, domain: str, org_name: str, strict: bool = False) -> bool:
        """
        Check if a domain matches the organization name.
        
        Uses intelligent matching to handle variations like:
        - "Axel Springer" -> "axelspringer.com"
        - "Max Planck" -> "mpg.de"
        - "VU" -> "vu.nl"
        
        Args:
            domain: Domain name
            org_name: Organization name
            strict: If True, use stricter matching to avoid false positives
            
        Returns:
            True if likely a match, False otherwise
        """
        org_lower = org_name.lower()
        domain_clean = re.sub(r'\.(com|org|net|edu|gov|co|uk|de|nl|fr|ch|at|se|no|dk|be|ie|es|it|pt|gr|cz|pl|ru|cn|jp|au|nz|in|br|mx|za|io|ai|app)$', '', domain)
        
        # Exact match
        if org_lower in domain or domain_clean in org_lower:
            return True
        
        # Check if organization name parts are in domain
        org_parts = org_lower.split()
        
        # All parts match (strongest signal)
        if len(org_parts) > 1 and all(part in domain_clean for part in org_parts):
            return True
        
        # For strict mode, require at least 2 parts to match for multi-word names
        if strict and len(org_parts) > 1:
            matching_parts = sum(1 for part in org_parts if part in domain_clean)
            if matching_parts >= 2:
                return True
            # Check for acronyms
            if matching_parts == 0:
                abbrev = ''.join([part[0] for part in org_parts])
                if abbrev.lower() in domain_clean:
                    return True
            return False
        
        # First part matches (main organization name)
        if len(org_parts) > 0 and org_parts[0] in domain_clean:
            return True
        
        # Check for common abbreviations
        if len(org_parts) > 1:
            abbrev = ''.join([part[0] for part in org_parts])
            if abbrev.lower() in domain_clean:
                return True
        
        # Check for acronyms (e.g., "Max Planck" -> "mpg")
        # Common patterns
        if org_lower.startswith('max planck') and 'mpg' in domain_clean:
            return True
        
        if org_lower.startswith('vrije universiteit') and ('vu' in domain_clean or 'vumc' in domain_clean):
            return True
        
        if org_lower.startswith('university of amsterdam') and 'uva' in domain_clean:
            return True
        
        # Fuzzy match: at least 60% of organization name in domain
        org_name_no_spaces = org_lower.replace(' ', '')
        domain_no_special = re.sub(r'[^a-z0-9]', '', domain_clean)
        
        if len(org_name_no_spaces) > 3:
            matching_chars = sum(1 for c in org_name_no_spaces if c in domain_no_special)
            if matching_chars / len(org_name_no_spaces) >= 0.6:
                return True
        
        return False
    
    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL to a consistent format.
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        # Ensure https
        if url.startswith('http://'):
            url = url.replace('http://', 'https://', 1)
        elif not url.startswith('https://'):
            url = 'https://' + url
        
        # Remove trailing slashes
        url = url.rstrip('/')
        
        # Remove query parameters and fragments
        url = url.split('?')[0].split('#')[0]
        
        return url
    
    def clear_cache(self):
        """Clear the resolution cache."""
        self._cache.clear()
