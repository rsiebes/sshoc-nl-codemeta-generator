"""
Maintainer property implementation for Codemeta 3.1 metadata.

This module handles the extraction and validation of maintainer information,
representing the individual responsible for maintaining the software.
"""

from typing import Dict, List, Any, Optional
from src.base_metadata import BaseMetadata
from src.orcid_utils import ORCIDLookup
from src.organization_url_resolver import OrganizationURLResolver
from src.execution_profiler import profile


class MaintainerMetadata(BaseMetadata):
    """
    Handles maintainer metadata extraction and validation.
    
    Maintainer represents the individual responsible for maintaining the software,
    usually including an email contact address.
    """
    
    CODEMETA_PROPERTY = 'maintainer'
    CODEMETA_TYPE = 'schema:Person'
    SCHEMA_ORG_TYPE = 'Person'
    REQUIRED = False
    
    def __init__(self, raw_data: Dict[str, Any]):
        """
        Initialize MaintainerMetadata.
        
        Args:
            raw_data: Raw scraped data
        """
        super().__init__(raw_data)
        self.orcid_lookup = ORCIDLookup()
        self.org_url_resolver = OrganizationURLResolver()
    
    def extract(self) -> Dict[str, Any]:
        """
        Extract maintainer from raw data.
        
        Maintainer can come from:
        1. Direct 'maintainer' field
        2. 'maintainers' field
        3. Repository owner (if person, not organization)
        4. Primary contributor (most commits)
        5. Contact information from README
        
        Returns:
            Dictionary with 'maintainer' key containing Person object(s)
        """
        maintainers = []
        
        # Try to extract from different sources
        raw_maintainer = self._get_value('maintainer')
        if raw_maintainer:
            maintainers.extend(self._process_maintainers(raw_maintainer))
        
        # Try maintainers field
        if not maintainers:
            raw_maintainers = self._get_value('maintainers')
            if raw_maintainers:
                maintainers.extend(self._process_maintainers(raw_maintainers))
        
        # Try owner field (if person, not organization)
        if not maintainers:
            owner = self._get_value('owner')
            if owner:
                # If owner is a dict with a name, it's likely a person
                if isinstance(owner, dict) and owner.get('name'):
                    maintainer_obj = self._process_single_maintainer(owner)
                    if maintainer_obj:
                        maintainers.append(maintainer_obj)
        
        # Try primary contributor (first contributor with most commits)
        if not maintainers:
            contributors = self._get_value('contributors')
            if contributors and isinstance(contributors, list) and len(contributors) > 0:
                # Take the first contributor as potential maintainer
                primary_contributor = contributors[0]
                maintainer_obj = self._process_single_maintainer(primary_contributor)
                if maintainer_obj:
                    maintainers.append(maintainer_obj)
        
        if not maintainers:
            self.add_warning(f"Optional field '{self.CODEMETA_PROPERTY}' could not be extracted")
            return {}
        
        # Store in metadata - single maintainer or array based on count
        if len(maintainers) == 1:
            self.metadata[self.CODEMETA_PROPERTY] = maintainers[0]
        else:
            self.metadata[self.CODEMETA_PROPERTY] = maintainers
        
        return self.metadata
    
    def _process_maintainers(self, raw_maintainers: Any) -> List[Dict]:
        """
        Process raw maintainer data into structured Person objects.
        
        Args:
            raw_maintainers: Raw maintainer data (string, dict, or list)
            
        Returns:
            List of Person dictionaries
        """
        maintainers = []
        
        if isinstance(raw_maintainers, list):
            for item in raw_maintainers:
                maintainer = self._process_single_maintainer(item)
                if maintainer:
                    maintainers.append(maintainer)
        else:
            maintainer = self._process_single_maintainer(raw_maintainers)
            if maintainer:
                maintainers.append(maintainer)
        
        return maintainers
    
    def _process_single_maintainer(self, raw_maintainer: Any) -> Optional[Dict]:
        """
        Process a single maintainer into a Person object.
        
        Args:
            raw_maintainer: Raw maintainer data (string or dict)
            
        Returns:
            Person dictionary or None
        """
        if not raw_maintainer:
            return None
        
        maintainer = {"@type": self.SCHEMA_ORG_TYPE}
        
        if isinstance(raw_maintainer, dict):
            # Extract name - check display_name first (enriched data)
            name = (raw_maintainer.get('name') or 
                   raw_maintainer.get('display_name') or 
                   raw_maintainer.get('full_name') or
                   raw_maintainer.get('username') or
                   raw_maintainer.get('login'))
            
            if name:
                maintainer['name'] = name
            
            # Extract given name and family name if available
            given_name = raw_maintainer.get('givenName') or raw_maintainer.get('given_name')
            family_name = raw_maintainer.get('familyName') or raw_maintainer.get('family_name')
            
            if given_name:
                maintainer['givenName'] = given_name
            if family_name:
                maintainer['familyName'] = family_name
            
            # Extract email (important for maintainer)
            email = raw_maintainer.get('email')
            if email:
                maintainer['email'] = email
            
            # Try to enrich with ORCID if we have a name
            if self.orcid_lookup and name:
                orcid_info = self.orcid_lookup.lookup_orcid(name, email)
                if orcid_info:
                    maintainer['@id'] = f"https://orcid.org/{orcid_info['orcid']}"
                    # Update names if ORCID provides better data
                    if orcid_info.get('given_name') and not given_name:
                        maintainer['givenName'] = orcid_info['given_name']
                    if orcid_info.get('family_name') and not family_name:
                        maintainer['familyName'] = orcid_info['family_name']
            
            # Extract affiliation - check company field (enriched data)
            affiliation = (raw_maintainer.get('affiliation') or 
                          raw_maintainer.get('organization') or
                          raw_maintainer.get('company'))
            if affiliation:
                org_obj = {
                    "@type": "Organization",
                    "name": affiliation
                }
                
                # Try to resolve organization URL
                org_url = self.org_url_resolver.resolve_organization_url(affiliation)
                if org_url:
                    org_obj["url"] = org_url
                
                maintainer['affiliation'] = org_obj
            
            # Extract URL - check website field (enriched data)
            url = raw_maintainer.get('url') or raw_maintainer.get('website')
            if url:
                maintainer['url'] = url
                
        elif isinstance(raw_maintainer, str):
            # Simple string - could be name or email
            if '@' in raw_maintainer:
                # Looks like an email
                maintainer['email'] = raw_maintainer
                # Try to extract name from email
                name_part = raw_maintainer.split('@')[0]
                maintainer['name'] = name_part.replace('.', ' ').replace('_', ' ').title()
            else:
                # Assume it's a name
                maintainer['name'] = raw_maintainer
                
                # Try ORCID lookup
                if self.orcid_lookup:
                    orcid_info = self.orcid_lookup.lookup_orcid(raw_maintainer)
                    if orcid_info:
                        maintainer['@id'] = f"https://orcid.org/{orcid_info['orcid']}"
                        if orcid_info.get('given_name'):
                            maintainer['givenName'] = orcid_info['given_name']
                        if orcid_info.get('family_name'):
                            maintainer['familyName'] = orcid_info['family_name']
        
        # Validate that we have at least a name
        if 'name' not in maintainer:
            return None
        
        return maintainer
    
    def _validate_metadata(self) -> None:
        """
        Validate maintainer metadata.
        """
        if not self.metadata:
            return
        
        value = self.metadata.get(self.CODEMETA_PROPERTY)
        
        if not value:
            # Maintainer is optional
            return
        
        # Can be a single Person or array of Persons
        if isinstance(value, dict):
            self._validate_person(value)
        elif isinstance(value, list):
            if len(value) == 0:
                self.add_warning(f"'{self.CODEMETA_PROPERTY}' array is empty")
                return
            
            for person in value:
                self._validate_person(person)
        else:
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' must be a Person object or array of Person objects")
    
    def _validate_person(self, person: Dict) -> None:
        """
        Validate a Person object.
        
        Args:
            person: Person dictionary to validate
        """
        if not isinstance(person, dict):
            self.add_warning(f"Person in '{self.CODEMETA_PROPERTY}' must be an object")
            return
        
        # Check @type
        if person.get('@type') != self.SCHEMA_ORG_TYPE:
            self.add_warning(f"Person in '{self.CODEMETA_PROPERTY}' must have @type '{self.SCHEMA_ORG_TYPE}'")
            return
        
        # Check required field: name
        if 'name' not in person:
            self.add_warning(f"Person in '{self.CODEMETA_PROPERTY}' must have 'name' field")
            return
        
        # Validate name is not empty
        if not person['name'] or not isinstance(person['name'], str):
            self.add_warning(f"Person 'name' in '{self.CODEMETA_PROPERTY}' must be a non-empty string")
            return
        
        # Warn if no email (maintainer should usually have email)
        if 'email' not in person:
            self.add_warning(f"Maintainer '{person['name']}' does not have an email address (recommended)")
        
        # Validate email format if present
        if 'email' in person:
            email = person['email']
            if not isinstance(email, str) or '@' not in email:
                self.add_warning(f"Invalid email format for maintainer '{person['name']}'")
        
        # Validate ORCID format if present
        if '@id' in person:
            orcid_id = person['@id']
            if not isinstance(orcid_id, str) or 'orcid.org' not in orcid_id:
                self.add_warning(f"Invalid ORCID format for maintainer '{person['name']}'")
        

