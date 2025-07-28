#!/usr/bin/env python3
"""
CodeMeta Enhancer - Enhancement and validation module

This module provides functionality for enhancing existing CodeMeta files
with additional metadata and upgrading between schema versions.

Author: Ronald Siebes (UCDS Group, VU Amsterdam)
ORCID: 0000-0001-8772-7904
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime


class CodeMetaEnhancer:
    """
    Class for enhancing and upgrading existing CodeMeta files.
    
    Provides functionality to:
    - Upgrade between CodeMeta schema versions
    - Add missing metadata fields
    - Enhance with organizational context
    - Validate CodeMeta compliance
    """
    
    def __init__(self, target_schema: str = "3.0"):
        """
        Initialize the CodeMeta enhancer.
        
        Args:
            target_schema: Target CodeMeta schema version
        """
        self.target_schema = target_schema
        self.target_context = f"https://doi.org/10.5063/schema/codemeta-{target_schema}"
    
    def enhance_file(self, filepath: str, output_path: Optional[str] = None) -> Dict:
        """
        Enhance a CodeMeta file with comprehensive metadata.
        
        Args:
            filepath: Path to input CodeMeta file
            output_path: Path for output file (overwrites input if None)
            
        Returns:
            Enhanced CodeMeta dictionary
        """
        # Load existing CodeMeta file
        with open(filepath, 'r', encoding='utf-8') as f:
            codemeta = json.load(f)
        
        # Enhance the CodeMeta data
        enhanced = self.enhance_codemeta(codemeta)
        
        # Save enhanced file
        output_file = output_path or filepath
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced, f, indent=2, ensure_ascii=False)
        
        return enhanced
    
    def enhance_codemeta(self, codemeta: Dict) -> Dict:
        """
        Enhance a CodeMeta dictionary with comprehensive metadata.
        
        Args:
            codemeta: Input CodeMeta dictionary
            
        Returns:
            Enhanced CodeMeta dictionary
        """
        # Create a copy to avoid modifying the original
        enhanced = codemeta.copy()
        
        # Upgrade schema version
        self._upgrade_schema(enhanced)
        
        # Add missing core fields
        self._add_missing_core_fields(enhanced)
        
        # Add comprehensive metadata
        self._add_comprehensive_metadata(enhanced)
        
        # Ensure proper field ordering
        self._reorder_fields(enhanced)
        
        return enhanced
    
    def _upgrade_schema(self, codemeta: Dict) -> None:
        """Upgrade CodeMeta to target schema version."""
        codemeta["@context"] = self.target_context
    
    def _add_missing_core_fields(self, codemeta: Dict) -> None:
        """Add missing core metadata fields."""
        # Add maintainer if missing (copy from author)
        if "maintainer" not in codemeta and "author" in codemeta:
            authors = codemeta["author"]
            if isinstance(authors, list) and len(authors) > 0:
                codemeta["maintainer"] = [authors[0]]
            elif isinstance(authors, dict):
                codemeta["maintainer"] = [authors]
        
        # Add development status
        if "developmentStatus" not in codemeta:
            codemeta["developmentStatus"] = "active"
        
        # Add software version if missing
        if "softwareVersion" not in codemeta:
            codemeta["softwareVersion"] = "1.0.0"
    
    def _add_comprehensive_metadata(self, codemeta: Dict) -> None:
        """Add comprehensive metadata fields for CodeMeta 3.0 compliance."""
        repo_url = codemeta.get("codeRepository", codemeta.get("url", ""))
        
        # Application categorization
        if "applicationCategory" not in codemeta:
            category_info = self._determine_application_category(codemeta)
            codemeta.update(category_info)
        
        # Technical specifications
        if "operatingSystem" not in codemeta:
            codemeta["operatingSystem"] = "Cross-platform"
        
        if "runtimePlatform" not in codemeta:
            codemeta["runtimePlatform"] = self._determine_runtime_platform(codemeta)
        
        # Documentation and support URLs
        if repo_url:
            self._add_repository_urls(codemeta, repo_url)
        
        # Research context fields
        research_fields = {
            "embargoDate": None,
            "funding": None,
            "hasSourceCode": repo_url,
            "targetProduct": f"{codemeta.get('name', 'Software')} software package"
        }
        
        for field, default_value in research_fields.items():
            if field not in codemeta:
                codemeta[field] = default_value
        
        # Initialize reference publication if not present
        if "referencePublication" not in codemeta:
            codemeta["referencePublication"] = None
        
        # Add related links if missing
        if "relatedLink" not in codemeta:
            codemeta["relatedLink"] = []
    
    def _determine_application_category(self, codemeta: Dict) -> Dict:
        """Determine application category based on project characteristics."""
        keywords = codemeta.get("keywords", [])
        name = codemeta.get("name", "").lower()
        description = codemeta.get("description", "").lower()
        
        # Combine text for analysis
        text_content = " ".join([name, description] + keywords).lower()
        
        # Category determination logic
        if any(word in text_content for word in ["data", "analysis", "statistics", "research", "science"]):
            return {
                "applicationCategory": "Data Science",
                "applicationSubCategory": "Research Tools"
            }
        elif any(word in text_content for word in ["web", "visualization", "dashboard", "interface"]):
            return {
                "applicationCategory": "Web Application",
                "applicationSubCategory": "Data Visualization"
            }
        elif any(word in text_content for word in ["workshop", "tutorial", "education", "teaching"]):
            return {
                "applicationCategory": "Education",
                "applicationSubCategory": "Training Materials"
            }
        elif any(word in text_content for word in ["synthetic", "generation", "simulation"]):
            return {
                "applicationCategory": "Data Science",
                "applicationSubCategory": "Data Generation"
            }
        else:
            return {
                "applicationCategory": "Research Software",
                "applicationSubCategory": "Scientific Computing"
            }
    
    def _determine_runtime_platform(self, codemeta: Dict) -> List[str]:
        """Determine runtime platform based on programming language."""
        prog_lang = codemeta.get("programmingLanguage", [])
        if isinstance(prog_lang, str):
            prog_lang = [prog_lang]
        
        platforms = []
        for lang in prog_lang:
            if lang == "Python":
                platforms.append("Python 3.8+")
            elif lang == "R":
                platforms.append("R 4.0+")
            elif lang == "JavaScript":
                platforms.extend(["Node.js", "Web Browser"])
            elif lang in ["Java"]:
                platforms.append("Java 8+")
            elif lang in ["C++", "C", "Go", "Rust"]:
                platforms.append("Cross-platform")
        
        return platforms if platforms else ["Cross-platform"]
    
    def _add_repository_urls(self, codemeta: Dict, repo_url: str) -> None:
        """Add repository-based URLs for documentation and support."""
        url_fields = {
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
            "contIntegration": f"{repo_url}/actions"
        }
        
        for field, value in url_fields.items():
            if field not in codemeta:
                codemeta[field] = value
    
    def _reorder_fields(self, codemeta: Dict) -> None:
        """Ensure proper field ordering with isPartOf near the end."""
        if "isPartOf" in codemeta:
            is_part_of = codemeta.pop("isPartOf")
            # Add it back at the end
            codemeta["isPartOf"] = is_part_of
    
    def add_organizational_context(self, codemeta: Dict, organization: Dict) -> None:
        """
        Add organizational context to CodeMeta file.
        
        Args:
            codemeta: CodeMeta dictionary to modify
            organization: Organization information
        """
        codemeta["isPartOf"] = organization
    
    def upgrade_software_requirements(self, codemeta: Dict, github_mapping: bool = True) -> None:
        """
        Upgrade software requirements to proper CodeMeta 3.0 format.
        
        Args:
            codemeta: CodeMeta dictionary to modify
            github_mapping: Whether to map package names to GitHub URLs
        """
        if "softwareRequirements" not in codemeta:
            return
        
        requirements = codemeta["softwareRequirements"]
        
        # If already in proper format, skip
        if isinstance(requirements, list) and len(requirements) > 0:
            if isinstance(requirements[0], dict) and "@type" in requirements[0]:
                return
        
        # Convert to proper format
        enhanced_requirements = []
        
        if isinstance(requirements, list):
            for req in requirements:
                if isinstance(req, str):
                    # Convert string requirement to proper format
                    enhanced_req = self._convert_string_requirement(req, github_mapping)
                    enhanced_requirements.append(enhanced_req)
                elif isinstance(req, dict):
                    enhanced_requirements.append(req)
        
        codemeta["softwareRequirements"] = enhanced_requirements
    
    def _convert_string_requirement(self, requirement: str, github_mapping: bool) -> Dict:
        """Convert string requirement to proper CodeMeta format."""
        # Extract package name from URL or string
        if requirement.startswith("https://github.com/"):
            # Extract package name from GitHub URL
            parts = requirement.split("/")
            package_name = parts[-1] if len(parts) > 0 else "unknown"
            github_url = requirement
        else:
            # Assume it's a package name
            package_name = requirement
            github_url = self._get_github_url_for_package(package_name) if github_mapping else requirement
        
        return {
            "@id": github_url,
            "@type": "SoftwareApplication",
            "identifier": package_name.lower(),
            "name": package_name
        }
    
    def _get_github_url_for_package(self, package_name: str) -> str:
        """Get GitHub URL for a package name (simplified mapping)."""
        # This is a simplified mapping - in practice, you'd want a more comprehensive database
        common_packages = {
            "numpy": "https://github.com/numpy/numpy",
            "pandas": "https://github.com/pandas-dev/pandas",
            "requests": "https://github.com/psf/requests",
            "flask": "https://github.com/pallets/flask",
            "django": "https://github.com/django/django",
            "tensorflow": "https://github.com/tensorflow/tensorflow",
            "pytorch": "https://github.com/pytorch/pytorch",
            "scikit-learn": "https://github.com/scikit-learn/scikit-learn"
        }
        
        return common_packages.get(package_name.lower(), f"https://github.com/search?q={package_name}")
    
    def validate_enhancement(self, codemeta: Dict) -> List[str]:
        """
        Validate the enhanced CodeMeta file.
        
        Args:
            codemeta: CodeMeta dictionary to validate
            
        Returns:
            List of validation messages
        """
        messages = []
        
        # Check schema version
        context = codemeta.get("@context", "")
        if self.target_schema not in context:
            messages.append(f"Warning: Schema version may not match target {self.target_schema}")
        
        # Check for comprehensive fields
        comprehensive_fields = [
            "maintainer", "developmentStatus", "applicationCategory",
            "operatingSystem", "runtimePlatform", "softwareHelp",
            "readme", "issueTracker", "downloadUrl"
        ]
        
        missing_fields = [field for field in comprehensive_fields if field not in codemeta]
        if missing_fields:
            messages.append(f"Missing comprehensive fields: {', '.join(missing_fields)}")
        
        # Check software requirements format
        if "softwareRequirements" in codemeta:
            reqs = codemeta["softwareRequirements"]
            if isinstance(reqs, list) and len(reqs) > 0:
                if isinstance(reqs[0], str):
                    messages.append("Software requirements should be in object format, not strings")
        
        if not messages:
            messages.append("Enhancement validation passed - CodeMeta file is comprehensive")
        
        return messages


def enhance_directory(directory_path: str, output_dir: Optional[str] = None) -> None:
    """
    Enhance all CodeMeta files in a directory.
    
    Args:
        directory_path: Path to directory containing CodeMeta files
        output_dir: Output directory (uses input directory if None)
    """
    enhancer = CodeMetaEnhancer()
    
    # Find all JSON files that look like CodeMeta files
    codemeta_files = []
    for filename in os.listdir(directory_path):
        if filename.endswith('.json') and ('codemeta' in filename.lower() or filename == 'codemeta.json'):
            codemeta_files.append(filename)
    
    print(f"Found {len(codemeta_files)} CodeMeta files to enhance...")
    
    for filename in codemeta_files:
        input_path = os.path.join(directory_path, filename)
        output_path = os.path.join(output_dir, filename) if output_dir else input_path
        
        try:
            enhanced = enhancer.enhance_file(input_path, output_path)
            validation_messages = enhancer.validate_enhancement(enhanced)
            print(f"✅ Enhanced: {filename}")
            for message in validation_messages:
                print(f"   {message}")
        except Exception as e:
            print(f"❌ Error enhancing {filename}: {e}")


if __name__ == "__main__":
    # Example usage
    enhancer = CodeMetaEnhancer(target_schema="3.0")
    
    # Enhance a single file
    # enhanced = enhancer.enhance_file("example_codemeta.json")
    
    # Enhance all files in a directory
    # enhance_directory("./examples/soda_science/")
    
    print("CodeMeta enhancer ready for use!")

