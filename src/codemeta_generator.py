#!/usr/bin/env python3
"""
CodeMeta Generator - Main generation module

This module provides the core functionality for generating CodeMeta files
from GitHub repositories and other sources.

Author: Ronald Siebes (UCDS Group, VU Amsterdam)
ORCID: 0000-0001-8772-7904
"""

import json
import requests
import re
from datetime import datetime
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse


class CodeMetaGenerator:
    """
    Main class for generating CodeMeta files from repository information.
    
    Supports both CodeMeta 2.0 and 3.0 schemas with comprehensive metadata
    extraction from GitHub repositories.
    """
    
    def __init__(self, schema_version: str = "3.0"):
        """
        Initialize the CodeMeta generator.
        
        Args:
            schema_version: CodeMeta schema version ("2.0" or "3.0")
        """
        self.schema_version = schema_version
        self.context_url = f"https://doi.org/10.5063/schema/codemeta-{schema_version}"
        
    def generate_from_github(self, repo_url: str, **kwargs) -> Dict:
        """
        Generate a CodeMeta file from a GitHub repository.
        
        Args:
            repo_url: GitHub repository URL
            **kwargs: Additional metadata to include
            
        Returns:
            Dictionary containing CodeMeta metadata
        """
        # Parse repository information
        repo_info = self._parse_github_url(repo_url)
        if not repo_info:
            raise ValueError(f"Invalid GitHub URL: {repo_url}")
            
        # Fetch repository data from GitHub API
        repo_data = self._fetch_github_data(repo_info['owner'], repo_info['repo'])
        
        # Generate base CodeMeta structure
        codemeta = self._create_base_structure(repo_data, repo_url)
        
        # Add comprehensive metadata
        self._add_comprehensive_metadata(codemeta, repo_data)
        
        # Apply any additional metadata from kwargs
        codemeta.update(kwargs)
        
        return codemeta
    
    def _parse_github_url(self, url: str) -> Optional[Dict[str, str]]:
        """Parse GitHub URL to extract owner and repository name."""
        pattern = r'https://github\.com/([^/]+)/([^/]+)/?'
        match = re.match(pattern, url)
        if match:
            return {
                'owner': match.group(1),
                'repo': match.group(2)
            }
        return None
    
    def _fetch_github_data(self, owner: str, repo: str) -> Dict:
        """
        Fetch repository data from GitHub API.
        
        Note: This is a simplified version. In production, you would want to:
        - Add authentication for higher rate limits
        - Handle API errors gracefully
        - Cache responses
        """
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # Fallback to basic information if API fails
            return {
                'name': repo,
                'full_name': f"{owner}/{repo}",
                'html_url': f"https://github.com/{owner}/{repo}",
                'description': f"Repository: {repo}",
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'language': 'Unknown',
                'license': None
            }
    
    def _create_base_structure(self, repo_data: Dict, repo_url: str) -> Dict:
        """Create the base CodeMeta structure."""
        return {
            "@context": self.context_url,
            "@type": "SoftwareSourceCode",
            "name": repo_data.get('name', 'Unknown'),
            "description": repo_data.get('description', 'No description available'),
            "url": repo_url,
            "codeRepository": repo_url,
            "dateCreated": repo_data.get('created_at', '').split('T')[0] if repo_data.get('created_at') else None,
            "dateModified": repo_data.get('updated_at', '').split('T')[0] if repo_data.get('updated_at') else None,
            "license": self._format_license(repo_data.get('license')),
            "programmingLanguage": [repo_data.get('language')] if repo_data.get('language') else []
        }
    
    def _add_comprehensive_metadata(self, codemeta: Dict, repo_data: Dict) -> None:
        """Add comprehensive metadata fields for CodeMeta 3.0 compliance."""
        repo_url = codemeta['codeRepository']
        
        # Development and maintenance information
        codemeta.update({
            "developmentStatus": "active",
            "applicationCategory": "Research Software",
            "applicationSubCategory": "Scientific Computing",
            "operatingSystem": "Cross-platform",
            "runtimePlatform": self._determine_runtime_platform(repo_data.get('language')),
            
            # Documentation and support
            "softwareHelp": {
                "@type": "WebSite",
                "url": f"{repo_url}/blob/main/README.md"
            },
            "readme": f"{repo_url}/blob/main/README.md",
            "issueTracker": f"{repo_url}/issues",
            "downloadUrl": f"{repo_url}/archive/refs/heads/main.zip",
            "buildInstructions": {
                "@type": "WebSite",
                "url": f"{repo_url}/blob/main/README.md"
            },
            
            # Development infrastructure
            "contIntegration": f"{repo_url}/actions",
            "hasSourceCode": repo_url,
            
            # Research context (to be filled)
            "embargoDate": None,
            "funding": None,
            "referencePublication": None,
            "isPartOf": None,
            
            # Additional metadata
            "targetProduct": f"{codemeta['name']} software package"
        })
    
    def _determine_runtime_platform(self, language: str) -> List[str]:
        """Determine runtime platform based on programming language."""
        if not language:
            return ["Cross-platform"]
            
        language_platforms = {
            'Python': ["Python 3.8+"],
            'R': ["R 4.0+"],
            'JavaScript': ["Node.js", "Web Browser"],
            'Java': ["Java 8+"],
            'C++': ["Cross-platform"],
            'C': ["Cross-platform"],
            'Go': ["Cross-platform"],
            'Rust': ["Cross-platform"]
        }
        
        return language_platforms.get(language, ["Cross-platform"])
    
    def _format_license(self, license_data: Optional[Dict]) -> Optional[Dict]:
        """Format license information for CodeMeta."""
        if not license_data:
            return None
            
        license_name = license_data.get('name', 'Unknown License')
        spdx_id = license_data.get('spdx_id')
        
        if spdx_id:
            return {
                "@id": f"http://spdx.org/licenses/{spdx_id}",
                "name": license_name
            }
        else:
            return {
                "name": license_name
            }
    
    def add_organizational_context(self, codemeta: Dict, organization_info: Dict) -> None:
        """
        Add organizational context to CodeMeta file.
        
        Args:
            codemeta: CodeMeta dictionary to modify
            organization_info: Organization information dictionary
        """
        codemeta["isPartOf"] = organization_info
    
    def add_authors(self, codemeta: Dict, authors: List[Dict]) -> None:
        """
        Add author information to CodeMeta file.
        
        Args:
            codemeta: CodeMeta dictionary to modify
            authors: List of author dictionaries with name, ORCID, etc.
        """
        codemeta["author"] = authors
        
        # Set first author as maintainer if not already set
        if authors and "maintainer" not in codemeta:
            codemeta["maintainer"] = [authors[0]]
    
    def add_software_requirements(self, codemeta: Dict, requirements: List[Dict]) -> None:
        """
        Add software requirements to CodeMeta file.
        
        Args:
            codemeta: CodeMeta dictionary to modify
            requirements: List of software requirement dictionaries
        """
        codemeta["softwareRequirements"] = requirements
    
    def add_reference_publications(self, codemeta: Dict, publications: Union[Dict, List[Dict]]) -> None:
        """
        Add reference publications to CodeMeta file.
        
        Args:
            codemeta: CodeMeta dictionary to modify
            publications: Publication dictionary or list of publications
        """
        codemeta["referencePublication"] = publications
    
    def validate_codemeta(self, codemeta: Dict) -> List[str]:
        """
        Validate CodeMeta file for completeness and correctness.
        
        Args:
            codemeta: CodeMeta dictionary to validate
            
        Returns:
            List of validation warnings/errors
        """
        warnings = []
        
        # Required fields
        required_fields = ["@context", "@type", "name", "description", "url"]
        for field in required_fields:
            if field not in codemeta:
                warnings.append(f"Missing required field: {field}")
        
        # Recommended fields
        recommended_fields = ["author", "license", "programmingLanguage", "dateCreated"]
        for field in recommended_fields:
            if field not in codemeta or not codemeta[field]:
                warnings.append(f"Missing recommended field: {field}")
        
        # Schema version check
        if "@context" in codemeta:
            if self.schema_version not in codemeta["@context"]:
                warnings.append(f"Schema version mismatch: expected {self.schema_version}")
        
        return warnings
    
    def save_codemeta(self, codemeta: Dict, filepath: str) -> None:
        """
        Save CodeMeta dictionary to JSON file.
        
        Args:
            codemeta: CodeMeta dictionary
            filepath: Output file path
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(codemeta, f, indent=2, ensure_ascii=False)


# Example usage and helper functions
def create_soda_science_organization() -> Dict:
    """Create SODA Science organization information for CodeMeta files."""
    return {
        "@type": "Organization",
        "@id": "https://github.com/sodascience",
        "name": "SODA Science",
        "description": "SODA (Scalable Open Data Analytics) Science is a research group focused on developing scalable and open data analytics solutions for scientific research. The group works on advancing computational methods, tools, and infrastructure for data-intensive research across multiple domains.",
        "url": "https://github.com/sodascience",
        "sameAs": [
            "https://sodascience.github.io/"
        ],
        "parentOrganization": {
            "@type": "Organization",
            "name": "Utrecht University",
            "url": "https://www.uu.nl/"
        },
        "foundingDate": "2020",
        "location": {
            "@type": "Place",
            "name": "Utrecht, Netherlands"
        },
        "keywords": [
            "data science",
            "open science",
            "scalable analytics",
            "research software",
            "computational methods",
            "data infrastructure"
        ]
    }


def create_publication_reference(doi: str, title: str, pub_type: str = "ScholarlyArticle", 
                               publisher: str = None, year: str = None) -> Dict:
    """
    Create a publication reference for CodeMeta.
    
    Args:
        doi: DOI of the publication
        title: Title of the publication
        pub_type: Type of publication (ScholarlyArticle, Dataset, etc.)
        publisher: Publisher name
        year: Publication year
        
    Returns:
        Publication reference dictionary
    """
    publication = {
        "@type": pub_type,
        "@id": doi,
        "name": title,
        "url": doi
    }
    
    if year:
        publication["datePublished"] = year
        
    if publisher:
        publication["publisher"] = {
            "@type": "Organization",
            "name": publisher
        }
    
    return publication


if __name__ == "__main__":
    # Example usage
    generator = CodeMetaGenerator(schema_version="3.0")
    
    # Generate CodeMeta for a repository
    repo_url = "https://github.com/sodascience/metasyn"
    codemeta = generator.generate_from_github(repo_url)
    
    # Add SODA Science organizational context
    soda_org = create_soda_science_organization()
    generator.add_organizational_context(codemeta, soda_org)
    
    # Add example publication
    publication = create_publication_reference(
        doi="https://doi.org/10.21105/joss.07099",
        title="Metasyn: A Python package for synthetic data generation",
        publisher="Journal of Open Source Software",
        year="2024"
    )
    generator.add_reference_publications(codemeta, publication)
    
    # Validate and save
    warnings = generator.validate_codemeta(codemeta)
    if warnings:
        print("Validation warnings:", warnings)
    
    generator.save_codemeta(codemeta, "example_codemeta.json")
    print("CodeMeta file generated successfully!")

