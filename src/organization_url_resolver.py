"""
Organization URL Resolver

Resolves ANY organization name to its official URL using intelligent search strategies:
1. Known mappings database (for common organizations)
2. Context-aware search using author/contributor information
3. Wikidata lookup with fuzzy matching
4. ROR (Research Organization Registry) API for academic institutions
5. Intelligent web search with result ranking and validation

This module helps enrich author affiliations with organization URLs.
"""

import requests
import json
import re
from typing import Dict, Optional, Tuple, List
from urllib.parse import quote, urlparse
from functools import lru_cache


class OrganizationURLResolver:
    """Resolves ANY organization name to its official URL using intelligent strategies."""

    # Wikidata SPARQL endpoint for organization lookups
    WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
    
    # ROR (Research Organization Registry) API
    ROR_API = "https://api.ror.org/organizations"
    
    # Cache for resolved organizations
    _cache = {}
    
    def __init__(self, timeout: int = 5):
        """
        Initialize the resolver.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
    
    def resolve_organization_url(self, organization_name: Optional[str], 
                                author_name: Optional[str] = None,
                                author_email: Optional[str] = None) -> Optional[str]:
        """
        Resolve ANY organization name to its URL using multiple strategies.
        Can use author context to improve accuracy.
        
        Args:
            organization_name: Name of the organization
            author_name: Optional name of the author/contributor for context
            author_email: Optional email of the author/contributor for context
            
        Returns:
            URL of the organization or None if not found
        """
        if not organization_name or not isinstance(organization_name, str):
            return None
        
        org_name = organization_name.strip()
        
        if not org_name:
            return None
        
        org_name_lower = org_name.lower()
        
        # Check cache first (using org name only as key for now)
        if org_name_lower in self._cache:
            return self._cache[org_name_lower]
        
        # Try multiple lookup strategies in order
        url = None
        
        # Strategy 1: Try direct URL construction (for common patterns)
        url = self._try_direct_url(org_name)
        if url:
            self._cache[org_name_lower] = url
            return url
        
        # Strategy 2: ROR (Research Organization Registry) - for academic institutions
        url = self._lookup_ror_organization(org_name)
        if url:
            self._cache[org_name_lower] = url
            return url
        
        # Strategy 3: Wikidata lookup
        url = self._lookup_wikidata_organization(org_name)
        if url:
            self._cache[org_name_lower] = url
            return url
        
        # Strategy 4: Context-aware intelligent web search
        url = self._intelligent_web_search(org_name, author_name, author_email)
        if url:
            self._cache[org_name_lower] = url
            return url
        
        # Cache the failure to avoid repeated lookups
        self._cache[org_name_lower] = None
        return None
    
    def _try_direct_url(self, org_name: str) -> Optional[str]:
        """
        Try to construct URL directly from organization name.
        Useful for common patterns like "VU" -> "vu.nl"
        
        Args:
            org_name: Organization name
            
        Returns:
            Organization URL or None
        """
        org_lower = org_name.lower().strip()
        
        # Known mappings for common organizations
        known_mappings = {
            # Dutch Universities
            'vu': 'https://www.vu.nl',
            'uva': 'https://www.uva.nl',
            'uu': 'https://www.uu.nl',
            'leiden': 'https://www.universiteitleiden.nl',
            'groningen': 'https://www.rug.nl',
            'erasmus': 'https://www.eur.nl',
            'tilburg': 'https://www.tilburguniversity.edu',
            'wageningen': 'https://www.wur.nl',
            'twente': 'https://www.utwente.nl',
            'maastricht': 'https://www.maastrichtuniversity.nl',
            'utrecht university': 'https://www.uu.nl',
            
            # US Universities
            'mit': 'https://www.mit.edu',
            'stanford': 'https://www.stanford.edu',
            'harvard': 'https://www.harvard.edu',
            'yale': 'https://www.yale.edu',
            'princeton': 'https://www.princeton.edu',
            'columbia': 'https://www.columbia.edu',
            'penn': 'https://www.penn.edu',
            'cornell': 'https://www.cornell.edu',
            'caltech': 'https://www.caltech.edu',
            'berkeley': 'https://www.berkeley.edu',
            
            # European Universities
            'oxford': 'https://www.ox.ac.uk',
            'cambridge': 'https://www.cam.ac.uk',
            'eth': 'https://www.ethz.ch',
            'eth zurich': 'https://www.ethz.ch',
            'sorbonne': 'https://www.sorbonne-universite.fr',
            'paris': 'https://www.universite-paris-cité.fr',
            'munich': 'https://www.lmu.de',
            'heidelberg': 'https://www.uni-heidelberg.de',
            'berlin': 'https://www.hu-berlin.de',
            
            # Research Institutions
            'cern': 'https://www.cern.ch',
            'nasa': 'https://www.nasa.gov',
            'max planck': 'https://www.mpg.de',
            'max-planck': 'https://www.mpg.de',
            'mpg': 'https://www.mpg.de',
            'fraunhofer': 'https://www.fraunhofer.de',
            'helmholtz': 'https://www.helmholtz.de',
            
            # Tech Companies
            'ibm': 'https://www.ibm.com',
            'microsoft': 'https://www.microsoft.com',
            'google': 'https://www.google.com',
            'apple': 'https://www.apple.com',
            'amazon': 'https://www.amazon.com',
            'meta': 'https://www.meta.com',
            'facebook': 'https://www.facebook.com',
            'intel': 'https://www.intel.com',
            'nvidia': 'https://www.nvidia.com',
            'qualcomm': 'https://www.qualcomm.com',
            
            # Media & Publishing
            'axel springer': 'https://www.axelspringer.com',
            'springer': 'https://www.springer.com',
            'elsevier': 'https://www.elsevier.com',
            'wiley': 'https://www.wiley.com',
            'taylor & francis': 'https://www.taylorandfrancis.com',
            'sage': 'https://www.sagepub.com',
            
            # Open Source & Standards
            'mozilla': 'https://www.mozilla.org',
            'apache': 'https://www.apache.org',
            'linux foundation': 'https://www.linuxfoundation.org',
            'python software foundation': 'https://www.python.org',
            'w3c': 'https://www.w3.org',
            'ietf': 'https://www.ietf.org',
            'eclipse': 'https://www.eclipse.org',
            'gnome': 'https://www.gnome.org',
            'kde': 'https://www.kde.org',
        }
        
        if org_lower in known_mappings:
            return known_mappings[org_lower]
        
        return None
    
    def _lookup_ror_organization(self, org_name: str) -> Optional[str]:
        """
        Look up organization in ROR (Research Organization Registry).
        Works well for academic institutions.
        
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
                
                # Return the first organization's URL if it matches well
                for item in items:
                    # Check if the name matches
                    item_name = item.get('name', '').lower()
                    org_lower = org_name.lower()
                    
                    # Good match if the organization name is similar
                    if self._string_similarity(item_name, org_lower) > 0.7:
                        if 'links' in item and len(item['links']) > 0:
                            url = item['links'][0]
                            if url and self._is_valid_url(url):
                                return self._normalize_url(url)
            
        except Exception as e:
            # Silently fail and try next method
            pass
        
        return None
    
    def _lookup_wikidata_organization(self, org_name: str) -> Optional[str]:
        """
        Look up organization in Wikidata with fuzzy matching.
        
        Args:
            org_name: Organization name
            
        Returns:
            Organization URL or None
        """
        try:
            # Try fuzzy match in Wikidata
            sparql_query = f'''
            SELECT ?item ?website WHERE {{
              ?item rdfs:label ?label .
              FILTER(CONTAINS(LCASE(?label), LCASE("{org_name}")))
              ?item wikibase:sitelinks ?sitelinks .
              OPTIONAL {{ ?item foaf:homepage ?website . }}
            }}
            LIMIT 10
            '''
            
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
                
                for result in results:
                    if 'website' in result:
                        website = result['website'].get('value', '').strip()
                        if website and self._is_valid_url(website):
                            return self._normalize_url(website)
            
        except Exception as e:
            # Silently fail and try next method
            pass
        
        return None
    
    def _intelligent_web_search(self, org_name: str, 
                               author_name: Optional[str] = None,
                               author_email: Optional[str] = None) -> Optional[str]:
        """
        Perform intelligent web search with context-aware queries.
        Uses author information to improve search accuracy.
        
        Args:
            org_name: Organization name
            author_name: Optional author name for context
            author_email: Optional author email for context
            
        Returns:
            Organization URL or None
        """
        # Build context-aware search queries
        search_strategies = []
        
        # Strategy 1: Exact organization name (highest confidence)
        search_strategies.append((f'"{org_name}" official website', 0.95))
        search_strategies.append((f'"{org_name}" homepage', 0.90))
        
        # Strategy 2: Organization + author context (if available)
        if author_name:
            author_last_name = author_name.split()[-1] if author_name else None
            if author_last_name:
                search_strategies.append((f'"{org_name}" "{author_last_name}" official website', 0.88))
                search_strategies.append((f'{org_name} {author_last_name} university', 0.85))
                search_strategies.append((f'{org_name} {author_last_name} company', 0.85))
        
        # Strategy 3: Organization + email domain context (if available)
        if author_email and '@' in author_email:
            email_domain = author_email.split('@')[1].lower()
            search_strategies.append((f'"{org_name}" "{email_domain}"', 0.87))
            search_strategies.append((f'{org_name} email domain {email_domain}', 0.80))
        
        # Strategy 4: Generic organization searches
        search_strategies.append((f'{org_name} official website', 0.80))
        search_strategies.append((f'{org_name} homepage', 0.75))
        search_strategies.append((f'{org_name} university', 0.70))
        search_strategies.append((f'{org_name} company', 0.70))
        search_strategies.append((f'{org_name} organization', 0.65))
        search_strategies.append((f'{org_name}', 0.60))
        
        best_url = None
        best_score = 0
        
        for query, base_confidence in search_strategies:
            url = self._search_and_rank(query, org_name, base_confidence)
            if url and url[1] > best_score:
                best_url = url[0]
                best_score = url[1]
        
        return best_url if best_score > 0.5 else None
    
    def _search_and_rank(self, query: str, org_name: str, base_confidence: float) -> Optional[Tuple[str, float]]:
        """
        Search and rank results by relevance.
        
        Args:
            query: Search query
            org_name: Original organization name
            base_confidence: Base confidence score for this query
            
        Returns:
            Tuple of (URL, confidence_score) or None
        """
        try:
            # Try Bing search
            response = requests.get(
                "https://www.bing.com/search",
                params={'q': query},
                timeout=self.timeout,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            
            if response.status_code == 200:
                # Extract URLs from HTML
                urls = re.findall(r'href=["\']?([https?://][^\s"\'<>]+)', response.text)
                
                # Filter and rank URLs
                candidates = []
                for url in urls:
                    if self._is_valid_url(url) and not self._is_search_engine_url(url):
                        domain = self._extract_domain(url)
                        if domain:
                            # Calculate relevance score
                            relevance = self._calculate_relevance(domain, org_name)
                            if relevance > 0:
                                confidence = base_confidence * relevance
                                candidates.append((url, confidence))
                
                # Return the best candidate
                if candidates:
                    candidates.sort(key=lambda x: x[1], reverse=True)
                    best_url, best_confidence = candidates[0]
                    if best_confidence > 0.5:
                        return (self._normalize_url(best_url), best_confidence)
        
        except Exception as e:
            pass
        
        return None
    
    def _calculate_relevance(self, domain: str, org_name: str) -> float:
        """
        Calculate relevance score between domain and organization name.
        Returns a score between 0 and 1.
        
        Args:
            domain: Domain name
            org_name: Organization name
            
        Returns:
            Relevance score (0-1)
        """
        org_lower = org_name.lower().strip()
        domain_clean = re.sub(r'\.(com|org|net|edu|gov|co|uk|de|nl|fr|ch|at|se|no|dk|be|ie|es|it|pt|gr|cz|pl|ru|cn|jp|au|nz|in|br|mx|za|io|ai|app)$', '', domain.lower())
        
        # Exact match is best
        if org_lower == domain_clean or org_lower == domain:
            return 1.0
        
        # Check if organization name is in domain
        if org_lower in domain_clean:
            return 0.95
        
        # Check if domain is in organization name
        if domain_clean in org_lower:
            return 0.9
        
        # Check for word matches
        org_parts = org_lower.split()
        domain_parts = domain_clean.replace('-', ' ').split()
        
        if len(org_parts) > 0 and len(domain_parts) > 0:
            # Count matching parts
            matching_parts = sum(1 for part in org_parts if part in domain_clean)
            
            if matching_parts == len(org_parts) and len(org_parts) > 0:
                # All parts match
                return 0.85
            elif matching_parts > 0:
                # Some parts match
                match_ratio = matching_parts / len(org_parts)
                return 0.5 + (0.3 * match_ratio)
        
        # Check for acronyms
        if len(org_parts) > 1:
            abbrev = ''.join([part[0] for part in org_parts])
            if abbrev.lower() in domain_clean:
                return 0.8
        
        # String similarity as fallback
        similarity = self._string_similarity(org_lower, domain_clean)
        return similarity * 0.7  # Scale down similarity-based matches
    
    def _string_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate string similarity using character overlap.
        Returns a score between 0 and 1.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score (0-1)
        """
        # Simple implementation using character overlap
        s1 = set(str1.replace(' ', ''))
        s2 = set(str2.replace(' ', ''))
        
        if len(s1) == 0 and len(s2) == 0:
            return 1.0
        
        intersection = len(s1 & s2)
        union = len(s1 | s2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
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
    
    def _is_search_engine_url(self, url: str) -> bool:
        """
        Check if URL is from a search engine or tracking service.
        
        Args:
            url: URL to check
            
        Returns:
            True if it's a search engine URL, False otherwise
        """
        search_engines = [
            'bing.com', 'microsoft.com', 'go.microsoft.com',
            'google.com', 'google.', 'googleusercontent.com',
            'duckduckgo.com', 'yahoo.com',
            'facebook.com', 'twitter.com', 'instagram.com',
            'reddit.com', 'linkedin.com',
            'amazon.com', 'ebay.com',
            'pinterest.com', 'youtube.com',
        ]
        
        url_lower = url.lower()
        for engine in search_engines:
            if engine in url_lower:
                return True
        
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
    
    def _normalize_url(self, url: str) -> str:
        """
        Normalize a URL to standard format.
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        url = url.strip()
        # Ensure it starts with https://
        if not url.startswith('http'):
            url = 'https://' + url
        # Remove trailing slashes
        url = url.rstrip('/')
        return url
