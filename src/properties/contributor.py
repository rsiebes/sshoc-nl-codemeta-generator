"""
Contributor Property Module

Handles extraction and validation of the 'contributor' Codemeta property.
Extracts contributor information including ORCID lookup and organization affiliation.
Reuses the logic from the author module.
"""

from typing import Dict, Any, Optional, List, Union
from src.base_metadata import BaseMetadata
from src.orcid_utils import ORCIDLookup
from src.organization_url_resolver import OrganizationURLResolver
from src.execution_profiler import profile


class ContributorMetadata(BaseMetadata):
    """Handles contributor metadata extraction and validation."""

    CODEMETA_PROPERTY = 'contributor'
    CODEMETA_TYPE = 'schema:Person'
    REQUIRED = False

    def __init__(self, raw_data: Dict[str, Any]):
        """
        Initialize ContributorMetadata.
        
        Args:
            raw_data: Raw scraped data
        """
        super().__init__(raw_data)
        self.orcid_lookup = ORCIDLookup()
        self.org_url_resolver = OrganizationURLResolver()

    def extract(self) -> Dict[str, Any]:
        """
        Extract contributors from raw data.

        Contributors can come from:
        1. Direct 'contributor' field
        2. 'contributors' field (GitHub contributors list)
        3. 'commit_authors' field (from commit history)
        4. 'collaborators' field

        Returns:
            Dictionary with 'contributor' key containing array of Person objects
        """
        contributors = []
        
        # Try to extract from different sources
        raw_contributors = self._get_value('contributor')
        if raw_contributors:
            contributors.extend(self._process_contributors(raw_contributors))
        
        # Try contributors field (GitHub contributors list)
        if not contributors:
            raw_contributors = self._get_value('contributors')
            if raw_contributors:
                contributors.extend(self._process_contributors(raw_contributors))
        
        # Try commit_authors field
        if not contributors:
            commit_authors = self._get_value('commit_authors')
            if commit_authors and isinstance(commit_authors, list):
                # Take all commit authors as contributors
                for commit_author in commit_authors:
                    contributor_obj = self._process_single_contributor(commit_author)
                    if contributor_obj:
                        contributors.append(contributor_obj)
        
        # Try collaborators field
        if not contributors:
            collaborators = self._get_value('collaborators')
            if collaborators:
                contributors.extend(self._process_contributors(collaborators))
        
        # Remove duplicates (by name, case-insensitive)
        contributors = self._remove_duplicates(contributors)
        
        if contributors:
            self.metadata[self.CODEMETA_PROPERTY] = contributors
            return self.metadata
        else:
            self.add_warning("Contributors could not be extracted from any source")
            return {}

    def _process_contributors(self, raw_contributors: Any) -> List[Dict[str, Any]]:
        """
        Process raw contributor data into Person objects.
        
        Args:
            raw_contributors: Raw contributor data (string, dict, or list)
            
        Returns:
            List of Person objects
        """
        contributors = []
        
        if isinstance(raw_contributors, list):
            for item in raw_contributors:
                contributor = self._process_single_contributor(item)
                if contributor:
                    contributors.append(contributor)
        elif isinstance(raw_contributors, (str, dict)):
            contributor = self._process_single_contributor(raw_contributors)
            if contributor:
                contributors.append(contributor)
        
        return contributors

    def _process_single_contributor(self, raw_contributor: Union[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Process a single contributor into a Person object.
        
        Args:
            raw_contributor: Raw contributor data (string or dict)
            
        Returns:
            Person object or None
        """
        person = {
            "@type": "Person"
        }
        
        name = None
        email = None
        orcid = None
        affiliation = None
        username = None
        
        # Extract data based on type
        if isinstance(raw_contributor, str):
            # Simple string name or username
            name = raw_contributor.strip()
            username = name
        elif isinstance(raw_contributor, dict):
            # Dictionary with contributor information
            name = raw_contributor.get('name') or raw_contributor.get('full_name') or raw_contributor.get('display_name')
            email = raw_contributor.get('email')
            orcid = raw_contributor.get('orcid') or raw_contributor.get('orcid_id')
            affiliation = raw_contributor.get('affiliation') or raw_contributor.get('organization') or raw_contributor.get('company')
            username = raw_contributor.get('username') or raw_contributor.get('login')
            
            # If no name but has username, use username as name
            if not name and username:
                name = username
        
        if not name:
            return None
        
        # Set name
        person['name'] = name
        
        # Try to split name into given and family names
        if ' ' in name and not name.startswith('@'):
            parts = name.strip().split()
            if len(parts) >= 2:
                person['givenName'] = parts[0]
                person['familyName'] = ' '.join(parts[1:])
        
        # Add email if available
        if email and self._is_valid_email(email):
            person['email'] = email
        
        # ORCID lookup and enrichment
        if orcid:
            # Validate and add ORCID
            if self.orcid_lookup.is_valid_orcid(orcid):
                person['@id'] = f"https://orcid.org/{orcid}"
                # Try to enrich from ORCID
                orcid_details = self.orcid_lookup.get_orcid_details(self.orcid_lookup.extract_orcid_id(orcid))
                if orcid_details:
                    if not person.get('givenName') and orcid_details.get('givenName'):
                        person['givenName'] = orcid_details['givenName']
                    if not person.get('familyName') and orcid_details.get('familyName'):
                        person['familyName'] = orcid_details['familyName']
                    if not affiliation and orcid_details.get('affiliation'):
                        affiliation = orcid_details['affiliation']
        else:
             # Try to find ORCID by name and email
            orcid_info = self.orcid_lookup.lookup_orcid(name, email)
            if orcid_info:
                person['@id'] = orcid_info['orcid_url']
                # Enrich from ORCID
                if not person.get('givenName') and orcid_info.get('givenName'):
                    person['givenName'] = orcid_info['givenName']
                if not person.get('familyName') and orcid_info.get('familyName'):
                    person['familyName'] = orcid_info['familyName']
                if not affiliation and orcid_info.get('affiliation'):
                    affiliation = orcid_info['affiliation']
        
        # Add affiliation if available
        if affiliation:
            org_obj = {
                "@type": "Organization",
                "name": affiliation
            }
            
            # Try to resolve organization URL with contributor context
            contributor_name = person.get("name", None)
            contributor_email = person.get("email", None)
            org_url = self.org_url_resolver.resolve_organization_url(
                affiliation, 
                author_name=contributor_name,
                author_email=contributor_email
            )
            if org_url:
                org_obj["url"] = org_url
            
            person['affiliation'] = org_obj
        
        return person

    def _remove_duplicates(self, contributors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate contributors based on name (case-insensitive).
        
        Args:
            contributors: List of Person objects
            
        Returns:
            List without duplicates
        """
        seen_names = set()
        unique_contributors = []
        
        for contributor in contributors:
            name = contributor.get('name', '').lower()
            if name and name not in seen_names:
                seen_names.add(name)
                unique_contributors.append(contributor)
        
        return unique_contributors

    def _is_valid_email(self, email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email address
            
        Returns:
            True if valid, False otherwise
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _validate_metadata(self) -> None:
        """
        Validate the extracted contributor metadata.
        
        Checks:
        - contributor must be an array
        - Each contributor must be a Person object
        - Each Person must have a name
        """
        if not self.metadata:
            return
        
        contributors = self.metadata.get(self.CODEMETA_PROPERTY)
        
        if contributors is None:
            return
        
        # Check type
        if not isinstance(contributors, list):
            self.errors.append("contributor must be an array")
            return
        
        # Check each contributor
        for i, contributor in enumerate(contributors):
            if not isinstance(contributor, dict):
                self.errors.append(f"contributor[{i}] must be a Person object (dict)")
                continue
            
            # Check @type
            if contributor.get('@type') != 'Person':
                self.warnings.append(f"contributor[{i}] should have @type='Person'")
            
            # Check name
            if not contributor.get('name'):
                self.errors.append(f"contributor[{i}] must have a 'name' field")
            
            # Check email format if present
            if 'email' in contributor:
                if not self._is_valid_email(contributor['email']):
                    self.warnings.append(f"contributor[{i}] has invalid email format")
            
            # Check ORCID format if present
            if '@id' in contributor:
                orcid_id = contributor['@id']
                if not orcid_id.startswith('https://orcid.org/'):
                    self.warnings.append(f"contributor[{i}] @id should be an ORCID URL")

    def to_codemeta_dict(self) -> Dict[str, Any]:
        """
        Convert metadata to Codemeta format.
        
        Returns:
            Dictionary in Codemeta format
        """
        if not self.metadata or self.CODEMETA_PROPERTY not in self.metadata:
            return {}
        
        return {
            self.CODEMETA_PROPERTY: self.metadata[self.CODEMETA_PROPERTY]
        }
