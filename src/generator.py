"""
Codemeta Generator

Main orchestrator that coordinates scraping and metadata generation.
"""

import json
import sys
from typing import Dict, Any, List
from datetime import datetime

from src.scraper import GitHubScraper
from src.properties.name import NameMetadata
from src.properties.description import DescriptionMetadata
from src.properties.url import UrlMetadata
from src.properties.version import VersionMetadata
from src.properties.code_repository import CodeRepositoryMetadata
from src.properties.license import LicenseMetadata
from src.properties.keywords import KeywordsMetadata
from src.properties.programming_language import ProgrammingLanguageMetadata
from src.properties.author import AuthorMetadata
from src.properties.contributor import ContributorMetadata
from src.properties.date_created import DateCreatedMetadata
from src.properties.date_modified import DateModifiedMetadata
from src.properties.readme import ReadmeMetadata
from src.properties.maintainer import MaintainerMetadata
from src.properties.build_instructions import BuildInstructionsMetadata
from src.properties.issue_tracker import IssueTrackerMetadata
from src.properties.identifier import IdentifierMetadata
from src.properties.download_url import DownloadUrlMetadata
from src.properties.date_published import DatePublishedMetadata
from src.properties.development_status import DevelopmentStatusMetadata
from src.properties.software_requirements import SoftwareRequirementsMetadata
from src.properties.application_category import ApplicationCategoryMetadata
from src.properties.application_sub_category import ApplicationSubCategoryMetadata
from src.properties.operating_system import OperatingSystemMetadata
from src.execution_profiler import get_profiler, profile
from src.wikidata_keyword_resolver import WikidataKeywordResolver


class CodemetaGenerator:
    """Generates Codemeta metadata from GitHub repositories."""

    CODEMETA_VERSION = "3.1"
    CODEMETA_CONTEXT = "https://w3id.org/codemeta/3.1"
    
    def __init__(self):
        """Initialize the generator."""
        self.scraper = GitHubScraper()
        self.property_modules = [
            NameMetadata,
            DescriptionMetadata,
            UrlMetadata,
            VersionMetadata,
            CodeRepositoryMetadata,
            LicenseMetadata,
            KeywordsMetadata,
            ProgrammingLanguageMetadata,
            AuthorMetadata,
            ContributorMetadata,
            MaintainerMetadata,
            DateCreatedMetadata,
            DateModifiedMetadata,
            ReadmeMetadata,
            BuildInstructionsMetadata,
            IssueTrackerMetadata,
            IdentifierMetadata,
            DownloadUrlMetadata,
            DatePublishedMetadata,
            DevelopmentStatusMetadata,
            SoftwareRequirementsMetadata,
            ApplicationCategoryMetadata,
            ApplicationSubCategoryMetadata,
            OperatingSystemMetadata,
        ]

    @profile("Generate Codemeta", "main")
    def generate(self, repo_url: str) -> Dict[str, Any]:
        """
        Generate Codemeta metadata for a GitHub repository.

        Args:
            repo_url: GitHub repository URL

        Returns:
            Dictionary containing Codemeta metadata
        """
        print(f"Scraping repository: {repo_url}")
        sys.stdout.flush()
        
        # Scrape repository data
        raw_data = self.scraper.scrape_repository(repo_url)
        
        print(f"Extracted data for: {raw_data.get('name', 'Unknown')}")
        sys.stdout.flush()
        
        # Generate metadata using property modules
        codemeta = self._build_codemeta(raw_data)
        
        return codemeta

    def _build_codemeta(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build Codemeta structure from raw data.

        Args:
            raw_data: Raw scraped data

        Returns:
            Codemeta dictionary
        """
        # Initialize Codemeta structure
        codemeta = {
            "@context": self.CODEMETA_CONTEXT,
            "@type": "SoftwareSourceCode"
        }
        
        # Process each property module
        errors = []
        warnings = []
        
        for ModuleClass in self.property_modules:
            try:
                module = ModuleClass(raw_data)
                module.extract()
                
                # Validate
                is_valid = module.validate()
                
                # Collect errors and warnings
                errors.extend(module.get_errors())
                warnings.extend(module.get_warnings())
                
                # Add to codemeta if valid or has data
                metadata_dict = module.to_codemeta_dict()
                if metadata_dict:
                    codemeta.update(metadata_dict)
                    
            except Exception as e:
                error_msg = f"Error processing {ModuleClass.__name__}: {e}"
                print(error_msg)
                sys.stdout.flush()
                errors.append(error_msg)
        
        # Keywords are now handled by KeywordsMetadata module
        # Programming languages are now handled by ProgrammingLanguageMetadata module
        # Dates are now handled by DateCreatedMetadata and DateModifiedMetadata modules
        
        # Print validation results
        if errors:
            print(f"\n⚠️  Errors ({len(errors)}):")
            sys.stdout.flush()
            for error in errors:
                print(f"  - {error}")
                sys.stdout.flush()
        
        if warnings:
            print(f"\n⚠️  Warnings ({len(warnings)}):")
            sys.stdout.flush()
            for warning in warnings:
                print(f"  - {warning}")
        
        return codemeta

    def generate_to_file(self, repo_url: str, output_file: str) -> None:
        """
        Generate Codemeta and save to file.

        Args:
            repo_url: GitHub repository URL
            output_file: Output file path
        """
        codemeta = self.generate(repo_url)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(codemeta, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Codemeta file generated: {output_file}")

    def generate_to_string(self, repo_url: str) -> str:
        """
        Generate Codemeta and return as JSON string.

        Args:
            repo_url: GitHub repository URL

        Returns:
            JSON string of Codemeta metadata
        """
        codemeta = self.generate(repo_url)
        return json.dumps(codemeta, indent=2, ensure_ascii=False)
