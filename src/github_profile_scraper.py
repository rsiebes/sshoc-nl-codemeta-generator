"""
GitHub User Profile Scraper

Extracts detailed information from GitHub user profiles including:
- ORCID identifier
- Affiliation/Company
- Email address
- Bio/Description
- Location
- Website/Blog
"""

import re
from typing import Dict, Optional, Any
import requests
from bs4 import BeautifulSoup
from src.execution_profiler import profile


class GitHubProfileScraper:
    """Scrapes detailed information from GitHub user profiles."""
    
    def __init__(self, timeout: int = 10):
        """
        Initialize the profile scraper.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    @profile("Scrape GitHub Profile", "profile")
    def scrape_profile(self, username: str) -> Dict[str, Any]:
        """
        Scrape detailed information from a GitHub user profile.
        
        Args:
            username: GitHub username
        
        Returns:
            Dictionary with profile information
        """
        profile_data = {
            'username': username,
            'name': None,
            'email': None,
            'company': None,
            'location': None,
            'bio': None,
            'website': None,
            'orcid': None,
            'twitter': None,
            'linkedin': None,
            'mastodon': None
        }
        
        try:
            url = f"https://github.com/{username}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract name
            name_elem = soup.find('span', {'class': 'p-name'})
            if name_elem:
                profile_data['name'] = name_elem.get_text(strip=True)
            
            # Extract email from public profile
            email_elem = soup.find('a', {'href': re.compile(r'^mailto:')})
            if email_elem:
                profile_data['email'] = email_elem.get_text(strip=True)
            
            # Extract company
            company_elem = soup.find('span', {'class': 'p-org'})
            if company_elem:
                profile_data['company'] = company_elem.get_text(strip=True)
            
            # Extract location
            location_elem = soup.find('span', {'class': 'p-label'})
            if location_elem:
                profile_data['location'] = location_elem.get_text(strip=True)
            
            # Extract bio
            bio_elem = soup.find('div', {'data-bio-text': True})
            if bio_elem:
                profile_data['bio'] = bio_elem.get_text(strip=True)
            
            # Extract website/blog
            website_elem = soup.find('a', {'class': 'Link--primary'})
            if website_elem and 'href' in website_elem.attrs:
                href = website_elem.get('href', '')
                if href and not href.startswith('http://github.com') and not href.startswith('https://github.com'):
                    profile_data['website'] = href
            
            # Extract social links and ORCID
            social_links = soup.find_all('a', {'class': 'Link--secondary'})
            for link in social_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Check for ORCID
                if 'orcid.org' in href:
                    # Extract ORCID ID from URL
                    orcid_match = re.search(r'(\d{4}-\d{4}-\d{4}-\d{3}[0-9X])', href)
                    if orcid_match:
                        profile_data['orcid'] = orcid_match.group(1)
                
                # Check for Twitter
                elif 'twitter.com' in href or 'x.com' in href:
                    profile_data['twitter'] = text
                
                # Check for LinkedIn
                elif 'linkedin.com' in href:
                    profile_data['linkedin'] = text
                
                # Check for Mastodon
                elif 'mastodon' in href:
                    profile_data['mastodon'] = text
            
            # Try to extract ORCID from bio if not found in links
            if not profile_data['orcid'] and profile_data['bio']:
                orcid_match = re.search(r'(\d{4}-\d{4}-\d{4}-\d{3}[0-9X])', profile_data['bio'])
                if orcid_match:
                    profile_data['orcid'] = orcid_match.group(1)
            
            return profile_data
        
        except Exception as e:
            return profile_data
    
    def extract_orcid(self, username: str) -> Optional[str]:
        """
        Extract ORCID from a GitHub user profile.
        
        Args:
            username: GitHub username
        
        Returns:
            ORCID identifier or None
        """
        profile = self.scrape_profile(username)
        return profile.get('orcid')
    
    def extract_affiliation(self, username: str) -> Optional[str]:
        """
        Extract affiliation/company from a GitHub user profile.
        
        Args:
            username: GitHub username
        
        Returns:
            Affiliation/company name or None
        """
        profile = self.scrape_profile(username)
        return profile.get('company')
    
    def extract_email(self, username: str) -> Optional[str]:
        """
        Extract email from a GitHub user profile.
        
        Args:
            username: GitHub username
        
        Returns:
            Email address or None
        """
        profile = self.scrape_profile(username)
        return profile.get('email')
    
    def extract_name(self, username: str) -> Optional[str]:
        """
        Extract full name from a GitHub user profile.
        
        Args:
            username: GitHub username
        
        Returns:
            Full name or None
        """
        profile = self.scrape_profile(username)
        return profile.get('name')
