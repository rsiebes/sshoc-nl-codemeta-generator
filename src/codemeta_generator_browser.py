"""
Browser-based CodeMeta 3.1 metadata generator.

This generator extracts metadata directly from GitHub web pages using browser
automation, avoiding the need for GitHub API authentication.
"""

import json
import time
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

from browser_github_extractor import extract_github_metadata, extract_readme_content
from utils import filter_empty_values


class BrowserCodeMetaGenerator:
    """Generate CodeMeta metadata using browser-based GitHub page extraction."""
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the browser-based CodeMeta generator.
        
        Args:
            verbose (bool): Enable verbose output
        """
        self.verbose = verbose
        self.metadata_cache = {}
    
    def generate_from_markdown(self, repo_url: str, markdown_content: str) -> Dict[str, Any]:
        """
        Generate CodeMeta metadata from markdown content extracted from GitHub page.
        
        Args:
            repo_url (str): The GitHub repository URL
            markdown_content (str): The markdown content from the GitHub page
            
        Returns:
            Dict[str, Any]: The generated CodeMeta metadata
        """
        if self.verbose:
            print(f"\n{'='*80}")
            print(f"CODEMETA GENERATION (BROWSER-BASED)")
            print(f"{'='*80}")
            print(f"\nRepository: {repo_url}")
        
        # Extract metadata from markdown
        if self.verbose:
            print(f"\n[1/3] Extracting metadata from GitHub page...")
        
        metadata = extract_github_metadata(markdown_content, repo_url)
        
        if self.verbose:
            print(f"      ✓ Extracted {len(metadata)} properties")
        
        # Build CodeMeta structure
        if self.verbose:
            print(f"\n[2/3] Building CodeMeta structure...")
        
        codemeta = self.build_codemeta(metadata)
        
        if self.verbose:
            print(f"      ✓ Generated {len(codemeta)} properties")
        
        # Validate and clean
        if self.verbose:
            print(f"\n[3/3] Validating metadata...")
        
        codemeta = filter_empty_values(codemeta)
        
        if self.verbose:
            print(f"      ✓ Metadata is valid")
            print(f"\n{'='*80}")
            print(f"GENERATION COMPLETE")
            print(f"{'='*80}")
            print(f"Total properties: {len(codemeta)}")
        
        return codemeta
    
    def build_codemeta(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build the CodeMeta structure from extracted metadata.
        
        Args:
            metadata (Dict[str, Any]): Extracted metadata
            
        Returns:
            Dict[str, Any]: CodeMeta structure
        """
        codemeta = {
            "@context": "https://codemeta.github.io/terms/",
            "@type": "SoftwareSourceCode",
        }
        
        # Map extracted metadata to CodeMeta properties
        property_mapping = {
            'name': 'name',
            'description': 'description',
            'url': 'url',
            'codeRepository': 'codeRepository',
            'programmingLanguage': 'programmingLanguage',
            'license': 'license',
            'keywords': 'keywords',
        }
        
        for source_key, codemeta_key in property_mapping.items():
            if source_key in metadata and metadata[source_key]:
                codemeta[codemeta_key] = metadata[source_key]
        
        # Add aggregate rating based on stars
        if 'stars' in metadata:
            codemeta['aggregateRating'] = self._create_rating(metadata['stars'])
        
        # Add repository statistics
        if 'commits' in metadata:
            codemeta['softwareVersion'] = f"Commits: {metadata['commits']}"
        
        return codemeta
    
    def _create_rating(self, stars: int) -> Dict[str, Any]:
        """
        Create an aggregate rating based on GitHub stars.
        
        Args:
            stars (int): Number of GitHub stars
            
        Returns:
            Dict[str, Any]: Rating object
        """
        # Map stars to rating scale (1-5)
        if stars == 0:
            rating_value = 0.0
        elif stars <= 10:
            rating_value = 1.0
        elif stars <= 100:
            rating_value = 2.0
        elif stars <= 500:
            rating_value = 3.0
        elif stars <= 2000:
            rating_value = 4.0
        else:
            rating_value = 5.0
        
        return {
            "@type": "AggregateRating",
            "ratingValue": rating_value,
            "bestRating": 5,
            "worstRating": 0,
            "ratingCount": stars,
            "name": f"GitHub Stars ({stars})"
        }
    
    def save_codemeta(self, codemeta: Dict[str, Any], output_path: Path) -> None:
        """
        Save CodeMeta to a JSON file.
        
        Args:
            codemeta (Dict[str, Any]): The CodeMeta metadata
            output_path (Path): The output file path
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(codemeta, f, indent=2)
        
        if self.verbose:
            print(f"\n✓ CodeMeta saved to {output_path}")
