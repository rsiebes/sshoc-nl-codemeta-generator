"""
Author Property Module

Handles extraction and validation of the 'author' Codemeta property.
Extracts author information including ORCID lookup and organization affiliation.
"""

from typing import Dict, Any, Optional, List, Union
from src.base_metadata import BaseMetadata
from src.orcid_utils import ORCIDLookup


class AuthorMetadata(BaseMetadata):
    """Handles author metadata extraction and validation."""

    CODEMETA_PROPERTY = 'author'
    CODEMETA_TYPE = 'schema:Person'
    REQUIRED = False

    def __init__(self, raw_data: Dict[str, Any]):
        """
        Initialize AuthorMetadata.
        
        Args:
            raw_data: Raw scraped data
        """
        super().__init__(raw_data)
        self.orcid_lookup = ORCIDLookup()

    def extract(self) -> Dict[str, Any]:
        """
        Extract authors from raw data.

        Authors can come from:
        1. Direct 'author' field
        2. 'authors' field
        3. 'creator' field
        4. Repository owner information
        5. Contributors list (filtered for authors)

        Returns:
            Dictionary with 'author' key containing array of Person objects
        """
        authors = []
        
        # Try to extract from different sources
        raw_authors = self._get_value('author')
        if raw_authors:
            authors.extend(self._process_authors(raw_authors))
        
        # Try authors field
        if not authors:
            raw_authors = self._get_value('authors')
            if raw_authors:
                authors.extend(self._process_authors(raw_authors))
        
        # Try creator field
        if not authors:
            creator = self._get_value('creator')
            if creator:
                authors.extend(self._process_authors(creator))
        
        # Try owner field (GitHub repository owner with profile data)
        if not authors:
            owner = self._get_value('owner')
            if owner:
                # If owner is a dict (from enhanced scraper), it has profile data
                if isinstance(owner, dict):
                    author_obj = self._process_single_author(owner)
                    if author_obj:
                        authors.append(author_obj)
                else:
                    # Fallback to simple string
                    author_obj = self._process_single_author(owner)
                    if author_obj:
                        authors.append(author_obj)
        
        # Try commit_authors (from commit history with profile data)
        if not authors:
            commit_authors = self._get_value('commit_authors')
            if commit_authors and isinstance(commit_authors, list):
                # Take first 5 commit authors
                for commit_author in commit_authors[:5]:
                    # Enrich with profile data if available
                    if isinstance(commit_author, dict) and commit_author.get('username'):
                        # Try to get full profile
                        username = commit_author['username']
                        # Use the name from commit if available
                        author_obj = self._process_single_author(commit_author)
                        if author_obj:
                            authors.append(author_obj)
        
        # Try contributors (limit to first few)
        if not authors:
            contributors = self._get_value('contributors')
            if contributors and isinstance(contributors, list):
                # Take first 3 contributors as potential authors
                for contrib in contributors[:3]:
                    author_obj = self._process_single_author(contrib)
                    if author_obj:
                        authors.append(author_obj)
        
        if not authors:
            self.add_warning(f"Optional field '{self.CODEMETA_PROPERTY}' could not be extracted")
            return {}
        
        # Remove duplicates based on name or email
        unique_authors = self._remove_duplicate_authors(authors)
        
        if unique_authors:
            self.metadata[self.CODEMETA_PROPERTY] = unique_authors
            return self.metadata
        else:
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' could not be processed")
            return {}

    def _process_authors(self, value: Any) -> List[Dict[str, Any]]:
        """
        Process and normalize authors from various formats.

        Args:
            value: Raw authors value (string, list, dict, or other)

        Returns:
            List of author Person objects
        """
        authors = []
        
        if isinstance(value, str):
            # Single author as string
            author_obj = self._process_single_author(value)
            if author_obj:
                authors.append(author_obj)
        
        elif isinstance(value, list):
            # List of authors
            for item in value:
                author_obj = self._process_single_author(item)
                if author_obj:
                    authors.append(author_obj)
        
        elif isinstance(value, dict):
            # Single author as dict
            author_obj = self._process_single_author(value)
            if author_obj:
                authors.append(author_obj)
        
        return authors

    def _process_single_author(self, author_data: Any) -> Optional[Dict[str, Any]]:
        """
        Process a single author from various formats.

        Args:
            author_data: Author data (string, dict, or other)

        Returns:
            Person object dict or None
        """
        if isinstance(author_data, str):
            # Author as string (name only)
            return self._create_person_object(name=author_data)
        
        elif isinstance(author_data, dict):
            # Author as dictionary (may include enhanced profile data)
            name = author_data.get('name') or author_data.get('login') or author_data.get('username')
            email = author_data.get('email')
            orcid = author_data.get('orcid') or author_data.get('orcid_id')
            affiliation = author_data.get('affiliation') or author_data.get('organization')
            given_name = author_data.get('givenName') or author_data.get('given_name')
            family_name = author_data.get('familyName') or author_data.get('family_name')
            
            # Extract additional profile data if available
            location = author_data.get('location')
            bio = author_data.get('bio')
            website = author_data.get('website')
            
            return self._create_person_object(
                name=name,
                email=email,
                orcid=orcid,
                affiliation=affiliation,
                given_name=given_name,
                family_name=family_name
            )
        
        return None

    def _create_person_object(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        orcid: Optional[str] = None,
        affiliation: Optional[str] = None,
        given_name: Optional[str] = None,
        family_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Person object according to Codemeta 3.1 specification.

        Args:
            name: Full name
            email: Email address
            orcid: ORCID identifier
            affiliation: Organization affiliation
            given_name: Given name (first name)
            family_name: Family name (last name)

        Returns:
            Person object dict or None
        """
        if not name and not given_name and not family_name:
            return None
        
        person = {
            "@type": "Person"
        }
        
        # Add name
        if name:
            person["name"] = name.strip()
        elif given_name or family_name:
            name_parts = []
            if given_name:
                name_parts.append(given_name.strip())
            if family_name:
                name_parts.append(family_name.strip())
            person["name"] = " ".join(name_parts)
        
        # Split name into given and family if not provided
        if not given_name and not family_name and name:
            name_parts = name.strip().split()
            if len(name_parts) >= 2:
                given_name = name_parts[0]
                family_name = " ".join(name_parts[1:])
        
        # Add given name
        if given_name:
            person["givenName"] = given_name.strip()
        
        # Add family name
        if family_name:
            person["familyName"] = family_name.strip()
        
        # Add email
        if email and self._is_valid_email(email):
            person["email"] = email.strip()
        
        # Validate and add ORCID
        if orcid:
            orcid_url = self.orcid_lookup.to_orcid_url(orcid)
            if orcid_url:
                person["@id"] = orcid_url
                # Verify ORCID exists
                if self.orcid_lookup.verify_orcid_exists(orcid):
                    # Try to get additional info from ORCID
                    orcid_details = self.orcid_lookup.get_orcid_details(
                        self.orcid_lookup.extract_orcid_id(orcid)
                    )
                    if orcid_details:
                        # Update with ORCID data if not already set
                        if not given_name and orcid_details.get('givenName'):
                            person["givenName"] = orcid_details['givenName']
                        if not family_name and orcid_details.get('familyName'):
                            person["familyName"] = orcid_details['familyName']
                        if not affiliation and orcid_details.get('affiliation'):
                            affiliation = orcid_details['affiliation']
        else:
            # Try to lookup ORCID if we have name and/or email
            if name or (given_name and family_name):
                lookup_name = name or f"{given_name} {family_name}"
                orcid_info = self.orcid_lookup.lookup_orcid(lookup_name, email)
                if orcid_info:
                    person["@id"] = orcid_info['orcid_url']
                    # Update with ORCID data if not already set
                    if not given_name and orcid_info.get('givenName'):
                        person["givenName"] = orcid_info['givenName']
                    if not family_name and orcid_info.get('familyName'):
                        person["familyName"] = orcid_info['familyName']
                    if not affiliation and orcid_info.get('affiliation'):
                        affiliation = orcid_info['affiliation']
        
        # Add affiliation as Organization object
        if affiliation:
            person["affiliation"] = {
                "@type": "Organization",
                "name": affiliation.strip()
            }
        
        return person

    def _is_valid_email(self, email: str) -> bool:
        """
        Check if email format is valid.

        Args:
            email: Email address to check

        Returns:
            True if valid, False otherwise
        """
        if not email or not isinstance(email, str):
            return False
        
        # Basic email validation
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _remove_duplicate_authors(self, authors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate authors based on name or email.

        Args:
            authors: List of author objects

        Returns:
            List of unique authors
        """
        unique_authors = []
        seen_names = set()
        seen_emails = set()
        
        for author in authors:
            name = author.get('name', '').lower()
            email = author.get('email', '').lower()
            
            # Check if we've seen this author
            is_duplicate = False
            if name and name in seen_names:
                is_duplicate = True
            if email and email in seen_emails:
                is_duplicate = True
            
            if not is_duplicate:
                unique_authors.append(author)
                if name:
                    seen_names.add(name)
                if email:
                    seen_emails.add(email)
        
        return unique_authors

    def _validate_metadata(self) -> None:
        """Validate author metadata."""
        if not self.metadata:
            if self.REQUIRED:
                self.add_error(f"Required field '{self.CODEMETA_PROPERTY}' is missing")
            return

        authors = self.metadata.get(self.CODEMETA_PROPERTY)
        
        if not authors:
            if self.REQUIRED:
                self.add_error(f"'{self.CODEMETA_PROPERTY}' is empty")
            return
        
        # Validate that authors is a list
        if not isinstance(authors, list):
            self.add_error(f"'{self.CODEMETA_PROPERTY}' must be an array, got {type(authors).__name__}")
            return
        
        # Validate each author
        for i, author in enumerate(authors):
            if not isinstance(author, dict):
                self.add_error(f"Author {i+1} must be an object, got {type(author).__name__}")
                continue
            
            # Check @type
            if author.get('@type') != 'Person':
                self.add_warning(f"Author {i+1} should have @type 'Person'")
            
            # Check name
            if not author.get('name'):
                self.add_error(f"Author {i+1} is missing 'name' field")
            
            # Validate email if present
            email = author.get('email')
            if email and not self._is_valid_email(email):
                self.add_warning(f"Author {i+1} has invalid email format: {email}")
            
            # Validate ORCID if present
            orcid_id = author.get('@id')
            if orcid_id and 'orcid.org' in orcid_id:
                if not self.orcid_lookup.is_valid_orcid(orcid_id):
                    self.add_warning(f"Author {i+1} has invalid ORCID format: {orcid_id}")
        
        # Check for reasonable number of authors
        if len(authors) > 50:
            self.add_warning(f"Large number of authors ({len(authors)}), consider reviewing")

    def to_codemeta_dict(self) -> Dict[str, Any]:
        """
        Convert to Codemeta format.

        Returns:
            Dictionary in Codemeta format
        """
        if not self.metadata:
            return {}
        
        return {
            self.CODEMETA_PROPERTY: self.metadata[self.CODEMETA_PROPERTY]
        }
