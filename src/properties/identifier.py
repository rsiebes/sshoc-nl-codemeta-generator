"""
Identifier property module for Codemeta 3.1 generator.

This module extracts persistent identifiers (DOI, ARK, PURL, etc.) from repositories.
Supports both GitHub and non-GitHub repositories.
"""

import re
from typing import Dict, Optional, List
from src.base_metadata import BaseMetadata
from src.execution_profiler import profile


class IdentifierMetadata(BaseMetadata):
    """Extract persistent identifiers from repository metadata."""
    
    PROPERTY_NAME = "identifier"
    SCHEMA_ORG_TYPE = "URL"
    
    # Identifier patterns
    DOI_PATTERN = r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+'
    ARK_PATTERN = r'ark:/\d{5,}/[A-Za-z0-9]+'
    PURL_PATTERN = r'http://purl\.org/[A-Za-z0-9/_-]+'
    SWHID_PATTERN = r'swh:1:(cnt|dir|rel|rev|snp):[0-9a-f]{40}'
    
    def __init__(self, raw_data: Dict):
        """Initialize the IdentifierMetadata extractor.
        
        Args:
            raw_data: Raw repository metadata from scraper
        """
        super().__init__(raw_data)
    
    def extract(self) -> Dict:
        """
        Extract identifier from repository metadata.
        
        Extraction sources (priority order):
        1. Direct 'identifier' field
        2. CITATION.cff file
        3. README badges and content
        4. Repository metadata
        5. Zenodo integration files
        
        Returns:
            Dictionary with identifier URL or empty dict
        """
        identifier = None
        
        # 1. Check direct identifier field
        direct_id = self._get_value('identifier')
        if direct_id:
            identifier = self._normalize_identifier(direct_id)
        
        # 2. Check for CITATION.cff
        if not identifier:
            identifier = self._extract_from_citation_cff()
        
        # 3. Check README content for identifier patterns
        if not identifier:
            identifier = self._extract_from_readme()
        
        # 4. Check repository description/about
        if not identifier:
            identifier = self._extract_from_description()
        
        # 5. Check for Zenodo integration
        if not identifier:
            identifier = self._extract_from_zenodo()
        
        # Store in metadata
        if identifier:
            self.metadata[self.PROPERTY_NAME] = identifier
        
        return self.metadata
    
    def _extract_from_citation_cff(self) -> Optional[str]:
        """
        Extract identifier from CITATION.cff file.
        
        CITATION.cff is a standard format for software citation metadata.
        It may contain DOI or other identifiers.
        
        Returns:
            Identifier string or None
        """
        # Check if CITATION.cff content is available
        citation_cff = self._get_value('citation_cff')
        if not citation_cff:
            return None
        
        # Look for identifiers field in CITATION.cff
        # Format: identifiers:
        #           - type: doi
        #             value: 10.5281/zenodo.1234567
        
        # Try to find DOI pattern
        doi_match = re.search(self.DOI_PATTERN, citation_cff)
        if doi_match:
            return f"https://doi.org/{doi_match.group()}"
        
        return None
    
    def _extract_from_readme(self) -> Optional[str]:
        """
        Extract identifier from README content.
        
        Looks for:
        - DOI badges ([![DOI](https://doi.org/...)])
        - Zenodo badges
        - Software Heritage badges
        - Direct identifier mentions
        
        Returns:
            Identifier string or None
        """
        readme_content = self._get_value('readme_content')
        if not readme_content:
            return None
        
        # Look for DOI in badges or links
        # Pattern: [![DOI](https://doi.org/10.XXXX/...)]
        # Pattern: [DOI](https://doi.org/10.XXXX/...)
        # Pattern: https://doi.org/10.XXXX/...
        
        doi_url_pattern = r'https?://doi\.org/(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)'
        doi_url_match = re.search(doi_url_pattern, readme_content)
        if doi_url_match:
            return f"https://doi.org/{doi_url_match.group(1)}"
        
        # Look for Zenodo DOI
        # Pattern: https://zenodo.org/badge/DOI/10.XXXX/...
        zenodo_pattern = r'zenodo\.org/badge/DOI/(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)'
        zenodo_match = re.search(zenodo_pattern, readme_content)
        if zenodo_match:
            return f"https://doi.org/{zenodo_match.group(1)}"
        
        # Look for plain DOI
        doi_match = re.search(self.DOI_PATTERN, readme_content)
        if doi_match:
            return f"https://doi.org/{doi_match.group()}"
        
        # Look for ARK
        ark_match = re.search(self.ARK_PATTERN, readme_content)
        if ark_match:
            return f"https://n2t.net/{ark_match.group()}"
        
        # Look for PURL
        purl_match = re.search(self.PURL_PATTERN, readme_content)
        if purl_match:
            return purl_match.group()
        
        # Look for Software Heritage ID
        swhid_match = re.search(self.SWHID_PATTERN, readme_content)
        if swhid_match:
            return f"https://archive.softwareheritage.org/{swhid_match.group()}"
        
        return None
    
    def _extract_from_description(self) -> Optional[str]:
        """
        Extract identifier from repository description.
        
        Returns:
            Identifier string or None
        """
        description = self._get_value('description')
        if not description:
            return None
        
        # Look for DOI in description
        doi_match = re.search(self.DOI_PATTERN, description)
        if doi_match:
            return f"https://doi.org/{doi_match.group()}"
        
        return None
    
    def _extract_from_zenodo(self) -> Optional[str]:
        """
        Extract identifier from Zenodo integration.
        
        Checks for .zenodo.json file which may contain DOI.
        
        Returns:
            Identifier string or None
        """
        zenodo_json = self._get_value('zenodo_json')
        if not zenodo_json:
            return None
        
        # Look for DOI in zenodo.json content
        doi_match = re.search(self.DOI_PATTERN, zenodo_json)
        if doi_match:
            return f"https://doi.org/{doi_match.group()}"
        
        return None
    
    def _normalize_identifier(self, identifier: str) -> str:
        """
        Normalize identifier to URL format.
        
        Args:
            identifier: Raw identifier string
            
        Returns:
            Normalized identifier URL
        """
        # If already a URL, return as-is
        if identifier.startswith(('http://', 'https://')):
            return identifier
        
        # If it's a DOI, convert to URL
        if re.match(self.DOI_PATTERN, identifier):
            return f"https://doi.org/{identifier}"
        
        # If it's an ARK, convert to URL
        if re.match(self.ARK_PATTERN, identifier):
            return f"https://n2t.net/{identifier}"
        
        # If it's a SWHID, convert to URL
        if re.match(self.SWHID_PATTERN, identifier):
            return f"https://archive.softwareheritage.org/{identifier}"
        
        # Otherwise return as-is
        return identifier
    
    def _validate_metadata(self) -> None:
        """
        Validate the extracted identifier.
        
        Raises:
            ValueError: If identifier is invalid
        """
        if self.PROPERTY_NAME not in self.metadata:
            return
        
        identifier = self.metadata[self.PROPERTY_NAME]
        
        # Check if it's a valid string
        if not isinstance(identifier, str):
            raise ValueError(f"Identifier must be a string, got {type(identifier)}")
        
        # Check if it's a URL
        if not identifier.startswith(('http://', 'https://', 'urn:')):
            self.warnings.append(f"Identifier should be a URL or URN: {identifier}")
        
        # Validate DOI format if it's a DOI URL
        if 'doi.org' in identifier:
            doi_match = re.search(self.DOI_PATTERN, identifier)
            if not doi_match:
                self.warnings.append(f"DOI URL may not contain valid DOI: {identifier}")
