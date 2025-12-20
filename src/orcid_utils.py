"""
ORCID Utilities

Provides functions for ORCID lookup and validation.
"""

import re
import requests
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup


class ORCIDLookup:
    """Handles ORCID lookup and validation."""
    
    ORCID_BASE_URL = "https://orcid.org"
    ORCID_PATTERN = r'^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$'
    
    @staticmethod
    def is_valid_orcid(orcid: str) -> bool:
        """
        Check if ORCID format is valid.
        
        Args:
            orcid: ORCID identifier (with or without URL)
        
        Returns:
            True if valid format, False otherwise
        """
        if not orcid:
            return False
        
        # Extract ORCID from URL if needed
        orcid_id = ORCIDLookup.extract_orcid_id(orcid)
        if not orcid_id:
            return False
        
        # Check format: XXXX-XXXX-XXXX-XXXX
        return bool(re.match(ORCIDLookup.ORCID_PATTERN, orcid_id))
    
    @staticmethod
    def extract_orcid_id(orcid: str) -> Optional[str]:
        """
        Extract ORCID ID from various formats.
        
        Args:
            orcid: ORCID in various formats (URL, ID, etc.)
        
        Returns:
            Clean ORCID ID or None
        """
        if not orcid:
            return None
        
        # Remove whitespace
        orcid = orcid.strip()
        
        # Extract from URL
        if 'orcid.org/' in orcid:
            match = re.search(r'orcid\.org/(\d{4}-\d{4}-\d{4}-\d{3}[0-9X])', orcid)
            if match:
                return match.group(1)
        
        # Check if it's already a clean ORCID ID
        if re.match(ORCIDLookup.ORCID_PATTERN, orcid):
            return orcid
        
        # Try to extract digits and format
        digits = re.findall(r'\d', orcid)
        if len(digits) == 15:
            # Last character might be X
            last_char = orcid[-1] if orcid[-1] in '0123456789X' else digits[-1]
            orcid_id = f"{''.join(digits[:4])}-{''.join(digits[4:8])}-{''.join(digits[8:12])}-{''.join(digits[12:15])}{last_char}"
            return orcid_id
        
        return None
    
    @staticmethod
    def to_orcid_url(orcid: str) -> Optional[str]:
        """
        Convert ORCID to full URL.
        
        Args:
            orcid: ORCID identifier
        
        Returns:
            Full ORCID URL or None
        """
        orcid_id = ORCIDLookup.extract_orcid_id(orcid)
        if not orcid_id:
            return None
        
        return f"{ORCIDLookup.ORCID_BASE_URL}/{orcid_id}"
    
    @staticmethod
    def lookup_orcid(name: str, email: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Look up ORCID information for a person by name.
        
        Args:
            name: Person's name
            email: Person's email (optional, for better matching)
        
        Returns:
            Dictionary with ORCID info or None if not found
        """
        try:
            # Search ORCID public API
            search_url = f"https://pub.orcid.org/v3.0/search/"
            
            # Build query
            query_parts = []
            if name:
                # Split name into parts
                name_parts = name.strip().split()
                if len(name_parts) >= 2:
                    given_name = name_parts[0]
                    family_name = ' '.join(name_parts[1:])
                    query_parts.append(f'given-names:{given_name}')
                    query_parts.append(f'family-name:{family_name}')
                else:
                    query_parts.append(f'text:{name}')
            
            if email:
                query_parts.append(f'email:{email}')
            
            if not query_parts:
                return None
            
            query = ' AND '.join(query_parts)
            
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'Codemeta-Generator/1.0'
            }
            
            params = {
                'q': query
            }
            
            response = requests.get(search_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if we have results
                if data.get('num-found', 0) > 0:
                    results = data.get('result', [])
                    if results:
                        # Get first result
                        first_result = results[0]
                        orcid_id = first_result.get('orcid-identifier', {}).get('path')
                        
                        if orcid_id:
                            # Get detailed info
                            return ORCIDLookup.get_orcid_details(orcid_id)
            
            # If no results found and email was provided, retry without email
            # This handles cases where email is not registered in ORCID profile
            if email and data.get('num-found', 0) == 0:
                return ORCIDLookup.lookup_orcid(name, email=None)
            
            return None
            
        except Exception as e:
            # Silently fail - ORCID lookup is optional
            return None
    
    @staticmethod
    def get_orcid_details(orcid_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed ORCID information including affiliations with URLs.
        
        Args:
            orcid_id: ORCID identifier
        
        Returns:
            Dictionary with ORCID details or None
        """
        try:
            # Get person details from ORCID API
            person_url = f"https://pub.orcid.org/v3.0/{orcid_id}/person"
            
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'Codemeta-Generator/1.0'
            }
            
            response = requests.get(person_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract name
                name_data = data.get('name', {})
                given_names = name_data.get('given-names', {}).get('value', '')
                family_name = name_data.get('family-name', {}).get('value', '')
                
                # Extract affiliations with detailed information
                affiliations = []
                affiliations_detailed = []
                employments = data.get('employments', {}).get('affiliation-group', [])
                for emp_group in employments:
                    summaries = emp_group.get('summaries', [])
                    for summary in summaries:
                        emp_summary = summary.get('employment-summary', {})
                        org_data = emp_summary.get('organization', {})
                        org_name = org_data.get('name')
                        
                        if org_name:
                            affiliations.append(org_name)
                            
                            # Extract detailed affiliation information
                            affiliation_detail = {
                                'name': org_name,
                                'url': None
                            }
                            
                            # Try to get organization URL
                            org_url = org_data.get('url')
                            if org_url:
                                affiliation_detail['url'] = org_url
                            
                            # Try to get organization ROR ID
                            org_ror = org_data.get('disambiguated-organization', {}).get('disambiguated-organization-identifier')
                            if org_ror:
                                affiliation_detail['ror_id'] = org_ror
                            
                            # Get employment dates
                            start_date = emp_summary.get('start-date')
                            end_date = emp_summary.get('end-date')
                            if start_date:
                                affiliation_detail['start_date'] = ORCIDLookup._format_date(start_date)
                            if end_date:
                                affiliation_detail['end_date'] = ORCIDLookup._format_date(end_date)
                            
                            # Get role title
                            role_title = emp_summary.get('role-title')
                            if role_title:
                                affiliation_detail['role'] = role_title
                            
                            affiliations_detailed.append(affiliation_detail)
                
                return {
                    'orcid': orcid_id,
                    'orcid_url': f"https://orcid.org/{orcid_id}",
                    'givenName': given_names,
                    'familyName': family_name,
                    'affiliation': affiliations[0] if affiliations else None,
                    'affiliations': affiliations,
                    'affiliations_detailed': affiliations_detailed
                }
            
            return None
            
        except Exception as e:
            return None
    
    @staticmethod
    def _format_date(date_obj: Dict[str, Any]) -> str:
        """
        Format ORCID date object to string.
        
        Args:
            date_obj: Date object from ORCID API
        
        Returns:
            Formatted date string
        """
        try:
            year = date_obj.get('year', {}).get('value', '')
            month = date_obj.get('month', {}).get('value', '')
            day = date_obj.get('day', {}).get('value', '')
            
            if year and month and day:
                return f"{year}-{month:0>2}-{day:0>2}"
            elif year and month:
                return f"{year}-{month:0>2}"
            elif year:
                return year
            return ''
        except:
            return ''
    
    @staticmethod
    def get_orcid_affiliations(orcid_id: str) -> Optional[Dict[str, Any]]:
        """
        Get ORCID affiliations with detailed information including URLs.
        
        Args:
            orcid_id: ORCID identifier
        
        Returns:
            Dictionary with affiliations or None
        """
        try:
            orcid_details = ORCIDLookup.get_orcid_details(orcid_id)
            if orcid_details:
                return {
                    'orcid': orcid_id,
                    'orcid_url': orcid_details.get('orcid_url'),
                    'affiliations': orcid_details.get('affiliations_detailed', [])
                }
            return None
        except Exception as e:
            return None
    
    @staticmethod
    def verify_orcid_exists(orcid: str) -> bool:
        """
        Verify that an ORCID exists by checking orcid.org.
        
        Args:
            orcid: ORCID identifier or URL
        
        Returns:
            True if ORCID exists, False otherwise
        """
        orcid_id = ORCIDLookup.extract_orcid_id(orcid)
        if not orcid_id:
            return False
        
        try:
            url = f"https://orcid.org/{orcid_id}"
            response = requests.head(url, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except:
            return False
