"""
SoftwareRequirements property extractor for CodeMeta.
Extracts software dependencies and requirements.
"""

from typing import Dict, List, Optional
import re
from ..base_metadata import BaseMetadata


class SoftwareRequirementsMetadata(BaseMetadata):
    """Extract softwareRequirements metadata."""
    
    PROPERTY_NAME = "softwareRequirements"
    SCHEMA_ORG_TYPE = "Text or URL"
    
    def __init__(self, raw_data: Dict):
        super().__init__(raw_data)
    
    def extract(self) -> Dict:
        """Extract software requirements from various sources."""
        requirements = []
        
        # 1. Check for explicit softwareRequirements field
        explicit_reqs = self._get_value('software_requirements')
        if explicit_reqs:
            if isinstance(explicit_reqs, list):
                requirements.extend(explicit_reqs)
            else:
                requirements.append(explicit_reqs)
        
        # 2. Extract from README requirements section
        readme_content = self._get_value('readme_content')
        if readme_content and not requirements:
            readme_reqs = self._extract_from_readme(readme_content)
            if readme_reqs:
                requirements.extend(readme_reqs)
        
        # 3. Infer from programming language
        if not requirements:
            prog_langs = self._get_value('languages')
            if prog_langs:
                lang_reqs = self._infer_from_language(prog_langs)
                if lang_reqs:
                    requirements.extend(lang_reqs)
        
        # Remove duplicates and store
        if requirements:
            requirements = list(dict.fromkeys(requirements))  # Preserve order
            self.metadata['softwareRequirements'] = requirements
        
        return self.metadata
    
    def _extract_from_readme(self, readme: str) -> List[str]:
        """
        Extract requirements from README content.
        
        Args:
            readme: README content
            
        Returns:
            List of requirement strings
        """
        requirements = []
        
        # Look for requirements/dependencies sections
        patterns = [
            r'##\s+(?:requirements|dependencies|prerequisites|installation)\s*\n(.*?)(?=\n##|\Z)',
            r'###\s+(?:requirements|dependencies|prerequisites)\s*\n(.*?)(?=\n###|\n##|\Z)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, readme, re.IGNORECASE | re.DOTALL)
            for match in matches:
                section = match.group(1)
                # Extract items from lists
                list_items = re.findall(r'[-*]\s+(.+?)(?:\n|$)', section)
                for item in list_items:
                    # Clean up the item
                    item = item.strip()
                    # Remove markdown formatting
                    item = re.sub(r'`([^`]+)`', r'\1', item)
                    item = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', item)
                    if item and len(item) < 100:  # Reasonable length
                        requirements.append(item)
        
        return requirements[:10]  # Limit to first 10
    
    def _infer_from_language(self, languages: List[str]) -> List[str]:
        """
        Infer basic requirements from programming language.
        
        Args:
            languages: List of programming languages (may include percentages)
            
        Returns:
            List of inferred requirements
        """
        requirements = []
        
        if not isinstance(languages, list):
            languages = [languages]
        
        # Parse language names (remove percentages like "Python0.7%")
        parsed_langs = []
        for lang in languages:
            # Extract language name before percentage
            match = re.match(r'([A-Za-z\s+#]+?)\d+\.\d+%', lang)
            if match:
                parsed_langs.append(match.group(1).strip())
            else:
                parsed_langs.append(lang.strip())
        
        languages = parsed_langs
        
        # Map languages to common runtime requirements
        language_map = {
            'Python': 'Python >= 3.7',
            'JavaScript': 'Node.js >= 14.0',
            'TypeScript': 'Node.js >= 14.0',
            'Ruby': 'Ruby >= 2.7',
            'Java': 'Java >= 11',
            'Go': 'Go >= 1.16',
            'Rust': 'Rust >= 1.50',
            'PHP': 'PHP >= 7.4',
            'R': 'R >= 4.0',
            'C++': 'C++ compiler (GCC >= 9 or Clang >= 10)',
            'C': 'C compiler (GCC >= 9 or Clang >= 10)',
        }
        
        for lang in languages:
            if lang in language_map:
                requirements.append(language_map[lang])
        
        return requirements
    
    def _validate_metadata(self) -> None:
        """Validate softwareRequirements metadata."""
        if not self.metadata or 'softwareRequirements' not in self.metadata:
            return
        
        reqs = self.metadata['softwareRequirements']
        
        # Validate it's a list
        if not isinstance(reqs, list):
            self.add_warning("softwareRequirements should be a list")
            return
        
        # Validate each requirement
        for req in reqs:
            if not isinstance(req, (str, dict)):
                self.add_warning(f"Invalid requirement type: {type(req).__name__}")
                continue
            
            if isinstance(req, str) and len(req) > 200:
                self.add_warning(f"Requirement string too long: {req[:50]}...")
