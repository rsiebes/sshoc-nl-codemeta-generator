"""
Organization URL Resolver

Resolves organization names to their official URLs using multiple strategies:
1. Direct URL construction from organization name
2. Wikidata lookup for known organizations
3. ROR (Research Organization Registry) API for academic institutions
4. Web search with intelligent domain matching

This module helps enrich author affiliations with organization URLs.
"""

import requests
import json
import re
from typing import Dict, Optional, Tuple, List
from urllib.parse import quote, urlparse
from functools import lru_cache


class OrganizationURLResolver:
    """Resolves organization names to their official URLs using online searches."""

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
        
        # Strategy 1: Try direct URL construction (for common patterns)
        url = self._try_direct_url(org_name)
        if url:
            self._cache[org_name_lower] = url
            return url
        
        # Strategy 2: Wikidata lookup
        url = self._lookup_wikidata_organization(org_name)
        if url:
            self._cache[org_name_lower] = url
            return url
        
        # Strategy 3: ROR (Research Organization Registry) - for academic institutions
        url = self._lookup_ror_organization(org_name)
        if url:
            self._cache[org_name_lower] = url
            return url
        
        # Strategy 4: Web search with domain extraction
        url = self._search_organization_url(org_name)
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
        
        # Known mappings for common abbreviations
        known_mappings = {
            # Dutch Universities
            'vu': 'https://www.vu.nl',
            'uva': 'https://www.uva.nl',
            'uu': 'https://www.uu.nl',
            'utrecht university': 'https://www.uu.nl',
            'leiden': 'https://www.universiteitleiden.nl',
            'groningen': 'https://www.rug.nl',
            'erasmus': 'https://www.eur.nl',
            'tilburg': 'https://www.tilburguniversity.edu',
            'wageningen': 'https://www.wur.nl',
            'twente': 'https://www.utwente.nl',
            'maastricht': 'https://www.maastrichtuniversity.nl',
            
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
    
    def _lookup_wikidata_organization(self, org_name: str) -> Optional[str]:
        """
        Look up organization in Wikidata.
        
        Args:
            org_name: Organization name
            
        Returns:
            Organization URL or None
        """
        try:
            # Query for organization by name
            sparql_query = f'''
            SELECT ?item ?website WHERE {{
              ?item rdfs:label "{org_name}"@en .
              ?item wikibase:sitelinks ?sitelinks .
              OPTIONAL {{ ?item foaf:homepage ?website . }}
            }}
            LIMIT 5
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
            
            # Try fuzzy match if exact match fails
            sparql_query_fuzzy = f'''
            SELECT ?item ?website WHERE {{
              ?item rdfs:label ?label .
              FILTER(CONTAINS(LCASE(?label), LCASE("{org_name}")))
              ?item wikibase:sitelinks ?sitelinks .
              OPTIONAL {{ ?item foaf:homepage ?website . }}
            }}
            LIMIT 5
            '''
            
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
        Search for organization URL using web search.
        
        Args:
            org_name: Organization name
            
        Returns:
            Organization URL or None
        """
        # Try different search strategies
        strategies = [
            (f'{org_name} official website', True),  # strict matching
            (f'{org_name} homepage', True),
            (f'{org_name} university', False),  # loose matching
            (f'{org_name} company', False),
            (f'{org_name} organization', False),
        ]
        
        for query, strict in strategies:
            url = self._search_with_bing(query, strict)
            if url:
                return url
        
        return None
    
    def _search_with_bing(self, search_query: str, strict: bool = False) -> Optional[str]:
        """
        Search for organization using Bing.
        
        Args:
            search_query: Search query
            strict: If True, use stricter domain matching
            
        Returns:
            Organization URL or None
        """
        try:
            response = requests.get(
                "https://www.bing.com/search",
                params={'q': search_query},
                timeout=self.timeout,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            
            if response.status_code == 200:
                # Extract URLs from HTML
                urls = re.findall(r'href=["\']?([https?://][^\s"\'<>]+)', response.text)
                
                # Filter out Bing-specific URLs and tracking URLs
                urls = [u for u in urls if 'bing.com' not in u and 'microsoft.com' not in u and 'go.microsoft.com' not in u]
                
                for url in urls:
                    if self._is_valid_url(url):
                        domain = self._extract_domain(url)
                        if domain and self._matches_organization_name(domain, search_query, strict=strict):
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
    
    def _matches_organization_name(self, domain: str, search_query: str, strict: bool = False) -> bool:
        """
        Check if a domain matches the search query.
        
        Args:
            domain: Domain name
            search_query: Search query or organization name
            strict: If True, use stricter matching
            
        Returns:
            True if likely a match, False otherwise
        """
        query_lower = search_query.lower().strip()
        domain_clean = re.sub(r'\.(com|org|net|edu|gov|co|uk|de|nl|fr|ch|at|se|no|dk|be|ie|es|it|pt|gr|cz|pl|ru|cn|jp|au|nz|in|br|mx|za|io|ai|app)$', '', domain)
        
        # Extract the core organization name from search query (remove keywords)
        org_name = query_lower
        for keyword in [' official website', ' homepage', ' university', ' company', ' organization']:
            org_name = org_name.replace(keyword, '').strip()
        
        # For very short names, require exact match
        if len(org_name) <= 3:
            if org_name == domain_clean or org_name == domain:
                return True
            if domain_clean.startswith(org_name) and len(domain_clean) <= len(org_name) + 2:
                return True
            return False
        
        # For longer names
        org_parts = org_name.split()
        
        # Exact match
        if org_name == domain_clean or org_name in domain:
            return True
        
        # Check if all parts are in domain (concatenated)
        if len(org_parts) > 1:
            org_no_space = org_name.replace(' ', '')
            if org_no_space in domain_clean.replace('-', ''):
                return True
            
            # All parts match
            if all(part in domain_clean for part in org_parts):
                return True
        
        # Check for acronyms
        if len(org_parts) > 1:
            abbrev = ''.join([part[0] for part in org_parts])
            if abbrev.lower() in domain_clean:
                return True
        
        # First part matches (for multi-word names)
        if len(org_parts) > 0 and org_parts[0] in domain_clean:
            if strict and len(org_parts) > 1:
                matching_parts = sum(1 for part in org_parts if part in domain_clean)
                return matching_parts >= 2
            return not strict
        
        return False
    
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
