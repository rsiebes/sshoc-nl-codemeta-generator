"""
Organization URL Resolver

Resolves organization names to their official URLs using multiple strategies:
1. Wikidata lookup for known organizations
2. Google search with domain extraction
3. Caching for performance

This module helps enrich author affiliations with organization URLs.
"""

import requests
import json
import re
from typing import Dict, Optional, Tuple
from urllib.parse import quote, urlparse
from functools import lru_cache


class OrganizationURLResolver:
    """Resolves organization names to their official URLs."""

    # Wikidata SPARQL endpoint for organization lookups
    WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
    
    # Google Custom Search (using public search via DuckDuckGo as fallback)
    DUCKDUCKGO_API = "https://duckduckgo.com/api/v1/search"
    
    # Cache for resolved organizations
    _cache = {}
    
    # Common organization patterns and their URLs
    KNOWN_ORGANIZATIONS = {
        'vu': 'https://www.vu.nl',
        'vu amsterdam': 'https://www.vu.nl',
        'vrije universiteit': 'https://www.vu.nl',
        'vrije universiteit amsterdam': 'https://www.vu.nl',
        'uva': 'https://www.uva.nl',
        'university of amsterdam': 'https://www.uva.nl',
        'mit': 'https://www.mit.edu',
        'stanford': 'https://www.stanford.edu',
        'harvard': 'https://www.harvard.edu',
        'berkeley': 'https://www.berkeley.edu',
        'oxford': 'https://www.ox.ac.uk',
        'cambridge': 'https://www.cam.ac.uk',
        'eth zurich': 'https://www.ethz.ch',
        'eth': 'https://www.ethz.ch',
        'max planck': 'https://www.mpg.de',
        'cern': 'https://www.cern.ch',
        'nasa': 'https://www.nasa.gov',
        'ibm': 'https://www.ibm.com',
        'microsoft': 'https://www.microsoft.com',
        'google': 'https://www.google.com',
        'apple': 'https://www.apple.com',
        'amazon': 'https://www.amazon.com',
        'facebook': 'https://www.facebook.com',
        'meta': 'https://www.meta.com',
        'twitter': 'https://www.twitter.com',
        'github': 'https://www.github.com',
        'linux foundation': 'https://www.linuxfoundation.org',
        'apache software foundation': 'https://www.apache.org',
        'mozilla': 'https://www.mozilla.org',
        'python software foundation': 'https://www.python.org',
        'w3c': 'https://www.w3.org',
        'ietf': 'https://www.ietf.org',
    }
    
    def __init__(self, timeout: int = 5):
        """
        Initialize the resolver.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
    
    def resolve_organization_url(self, organization_name: Optional[str]) -> Optional[str]:
        """
        Resolve an organization name to its URL.
        
        Args:
            organization_name: Name of the organization
            
        Returns:
            URL of the organization or None if not found
        """
        if not organization_name or not isinstance(organization_name, str):
            return None
        
        org_name = organization_name.strip().lower()
        
        if not org_name:
            return None
        
        # Check cache first
        if org_name in self._cache:
            return self._cache[org_name]
        
        # Try known organizations first
        if org_name in self.KNOWN_ORGANIZATIONS:
            url = self.KNOWN_ORGANIZATIONS[org_name]
            self._cache[org_name] = url
            return url
        
        # Try partial matches in known organizations
        for known_org, url in self.KNOWN_ORGANIZATIONS.items():
            if org_name in known_org or known_org in org_name:
                self._cache[org_name] = url
                return url
        
        # Try Wikidata lookup
        wikidata_url = self._lookup_wikidata_organization(org_name)
        if wikidata_url:
            self._cache[org_name] = wikidata_url
            return wikidata_url
        
        # Try search-based lookup
        search_url = self._search_organization_url(org_name)
        if search_url:
            self._cache[org_name] = search_url
            return search_url
        
        # Cache the failure
        self._cache[org_name] = None
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
            # SPARQL query to find organization and its official website
            sparql_query = f"""
            SELECT ?org ?orgLabel ?website WHERE {{
              ?org rdfs:label "{org_name}"@en ;
                   wdt:P31 wd:Q43229 .  # instance of organization
              OPTIONAL {{ ?org wdt:P856 ?website . }}
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
            }}
            LIMIT 5
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
                            return website
            
        except Exception as e:
            # Silently fail and try next method
            pass
        
        return None
    
    def _search_organization_url(self, org_name: str) -> Optional[str]:
        """
        Search for organization URL using DuckDuckGo.
        
        Args:
            org_name: Organization name
            
        Returns:
            Organization URL or None
        """
        try:
            # Search for the organization with common TLDs
            search_query = f"{org_name} official website"
            
            response = requests.get(
                self.DUCKDUCKGO_API,
                params={
                    'q': search_query,
                    'format': 'json'
                },
                timeout=self.timeout,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Try to extract URL from results
                results = data.get('Results', [])
                for result in results:
                    url = result.get('FirstURL', '').strip()
                    if url and self._is_valid_url(url):
                        # Extract domain and verify it's likely the official site
                        domain = self._extract_domain(url)
                        if domain and self._is_likely_official_domain(domain, org_name):
                            return self._normalize_url(url)
                
                # Try abstract/related links
                related_topics = data.get('RelatedTopics', [])
                for topic in related_topics:
                    url = topic.get('FirstURL', '').strip()
                    if url and self._is_valid_url(url):
                        domain = self._extract_domain(url)
                        if domain and self._is_likely_official_domain(domain, org_name):
                            return self._normalize_url(url)
            
        except Exception as e:
            # Silently fail
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
    
    def _is_likely_official_domain(self, domain: str, org_name: str) -> bool:
        """
        Check if a domain is likely the official domain for an organization.
        
        Args:
            domain: Domain name
            org_name: Organization name
            
        Returns:
            True if likely official, False otherwise
        """
        org_name_lower = org_name.lower()
        domain_lower = domain.lower()
        
        # Remove common TLDs and extensions
        domain_clean = re.sub(r'\.(com|org|net|edu|gov|co|uk|de|nl|fr|ch|at|se|no|dk|be|ie|es|it|pt|gr|cz|pl|ru|cn|jp|au|nz|in|br|mx|za)$', '', domain_lower)
        
        # Check if organization name appears in domain
        org_parts = org_name_lower.split()
        
        # Full name match
        if org_name_lower in domain_lower or domain_lower in org_name_lower:
            return True
        
        # Check if main parts of organization name are in domain
        if len(org_parts) > 0:
            main_part = org_parts[0]
            if main_part in domain_clean or domain_clean in main_part:
                return True
        
        # Check for common abbreviations
        if len(org_parts) > 1:
            abbrev = ''.join([part[0] for part in org_parts])
            if abbrev.lower() in domain_clean:
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
        
        return url
    
    def clear_cache(self):
        """Clear the resolution cache."""
        self._cache.clear()
