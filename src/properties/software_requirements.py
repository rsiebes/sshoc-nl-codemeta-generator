"""
Software Requirements Property Module - Version 2

Handles extraction and validation of the 'softwareRequirements' Codemeta property.
Extracts software dependencies and runtime requirements from multiple sources.

Key improvements:
- Supports language percentage-based ordering
- Generates structured SoftwareSourceCode objects
- Includes version information for known languages
- Filters non-executable languages (CSS, HTML, etc.)
"""

from typing import Dict, List, Optional, Any, Tuple
import re
import json
from ..base_metadata import BaseMetadata


class SoftwareRequirementsMetadata(BaseMetadata):
    """Handles softwareRequirements metadata extraction and validation."""

    CODEMETA_PROPERTY = 'softwareRequirements'
    CODEMETA_TYPE = 'schema:Text'
    REQUIRED = False

    # Language to runtime requirement mapping
    LANGUAGE_REQUIREMENTS = {
        'Python': {
            'name': 'Python',
            'min_version': '3.7',
            'max_version': None,
            'description': 'Python runtime environment'
        },
        'JavaScript': {
            'name': 'Node.js',
            'min_version': '14.0',
            'max_version': None,
            'description': 'Node.js runtime environment'
        },
        'TypeScript': {
            'name': 'Node.js',
            'min_version': '14.0',
            'max_version': None,
            'description': 'Node.js runtime environment'
        },
        'Java': {
            'name': 'Java',
            'min_version': '11',
            'max_version': None,
            'description': 'Java runtime environment'
        },
        'Ruby': {
            'name': 'Ruby',
            'min_version': '2.7',
            'max_version': None,
            'description': 'Ruby runtime environment'
        },
        'Go': {
            'name': 'Go',
            'min_version': '1.16',
            'max_version': None,
            'description': 'Go runtime environment'
        },
        'Rust': {
            'name': 'Rust',
            'min_version': '1.56',
            'max_version': None,
            'description': 'Rust compiler and runtime'
        },
        'PHP': {
            'name': 'PHP',
            'min_version': '7.4',
            'max_version': None,
            'description': 'PHP runtime environment'
        },
        'C#': {
            'name': '.NET',
            'min_version': '5.0',
            'max_version': None,
            'description': '.NET runtime environment'
        },
        'Kotlin': {
            'name': 'Java',
            'min_version': '11',
            'max_version': None,
            'description': 'Java runtime environment'
        },
        'Swift': {
            'name': 'Swift',
            'min_version': '5.0',
            'max_version': None,
            'description': 'Swift compiler and runtime'
        },
        'Scala': {
            'name': 'Java',
            'min_version': '11',
            'max_version': None,
            'description': 'Java runtime environment'
        },
        'Prolog': {
            'name': 'Prolog',
            'min_version': None,
            'max_version': None,
            'description': 'Prolog runtime environment'
        },
    }

    def __init__(self, raw_data: Dict[str, Any]):
        """Initialize SoftwareRequirementsMetadata."""
        super().__init__(raw_data)

    def _validate_metadata(self) -> bool:
        """
        Validate extracted softwareRequirements metadata.

        Returns:
            True if metadata is valid, False otherwise
        """
        reqs = self.metadata.get(self.CODEMETA_PROPERTY)
        if reqs is None:
            return True  # Optional field

        if not isinstance(reqs, list):
            return False

        for req in reqs:
            if isinstance(req, dict):
                if '@type' not in req or 'name' not in req:
                    return False
            elif not isinstance(req, str):
                return False

        return True

    def extract(self) -> Dict[str, Any]:
        """
        Extract software requirements from multiple sources.

        Sources are tried in priority order:
        1. Explicit softwareRequirements field
        2. Package manager files
        3. Language-based inference (with percentage ordering)
        4. README content

        Returns:
            Dictionary with 'softwareRequirements' key
        """
        requirements = []

        # 1. Check for explicit softwareRequirements field
        explicit_reqs = self._get_value('software_requirements')
        if explicit_reqs:
            requirements.extend(self._normalize_requirements(explicit_reqs))

        # 2. Extract from package manager files
        if not requirements:
            file_reqs = self._extract_from_package_files()
            if file_reqs:
                requirements.extend(file_reqs)

        # 3. Infer from programming languages (with percentage ordering)
        if not requirements:
            prog_langs = self._get_value('languages')
            if prog_langs:
                lang_reqs = self._infer_from_language(prog_langs)
                if lang_reqs:
                    requirements.extend(lang_reqs)

        # 4. Extract from README (fallback)
        if not requirements:
            readme_content = self._get_value('readme_content')
            if readme_content:
                readme_reqs = self._extract_from_readme(readme_content)
                if readme_reqs:
                    requirements.extend(readme_reqs)

        # Remove duplicates while preserving order
        if requirements:
            unique_requirements = self._deduplicate_requirements(requirements)
            self.metadata[self.CODEMETA_PROPERTY] = unique_requirements
            return self.metadata

        return self.metadata

    def _infer_from_language(self, languages: List[str]) -> List[Dict[str, Any]]:
        """
        Infer requirements from programming languages sorted by percentage.

        Extracts language percentages and generates requirements for all
        significant languages. If percentages available, uses 5% threshold.
        If no percentages, includes all known executable languages.

        Args:
            languages: List of programming languages with or without percentages

        Returns:
            List of inferred requirements as SoftwareSourceCode objects
        """
        requirements = []

        if not isinstance(languages, list):
            languages = [languages]

        # Parse languages and percentages
        lang_percentages: List[Tuple[str, Optional[float]]] = []
        has_percentages = False

        for lang in languages:
            lang_name, percentage = self._parse_language_percentage(lang)
            if lang_name:
                lang_percentages.append((lang_name, percentage))
                if percentage is not None:
                    has_percentages = True

        # If we have percentages, sort by percentage (descending)
        if has_percentages:
            lang_percentages.sort(
                key=lambda x: (x[1] is not None, x[1] if x[1] is not None else 0),
                reverse=True
            )

        # Generate requirements for languages
        for lang_name, percentage in lang_percentages:
            # If we have percentages, only include languages with >= 5%
            if has_percentages and percentage is not None and percentage < 5.0:
                continue

            # Skip non-executable languages for runtime requirements
            if lang_name in ['CSS', 'HTML', 'Markdown', 'JSON', 'YAML', 'XML']:
                continue

            if lang_name in self.LANGUAGE_REQUIREMENTS:
                req_info = self.LANGUAGE_REQUIREMENTS[lang_name]
                # Create structured requirement object
                req_obj = self._create_requirement_object(
                    name=req_info['name'],
                    min_version=req_info['min_version'],
                    max_version=req_info['max_version'],
                    description=req_info['description'],
                    language=lang_name
                )
                requirements.append(req_obj)

        return requirements

    def _parse_language_percentage(self, lang_str: str) -> Tuple[Optional[str], Optional[float]]:
        """
        Parse language name and percentage from string.

        Handles: "Python 85.5%", "Python85.5%", "Python", "Jupyter Notebook"

        Args:
            lang_str: Language string with optional percentage

        Returns:
            Tuple of (language_name, percentage) or (language_name, None)
        """
        if not lang_str:
            return None, None

        lang_str = lang_str.strip()

        # Try to match "Language XX.X%" (with space)
        match = re.match(r'^(.+?)\s+(\d+\.\d+)%$', lang_str)
        if match:
            lang_name = match.group(1).strip()
            percentage = float(match.group(2))
            return lang_name, percentage

        # Try to match "LanguageXX.X%" (without space)
        match = re.match(r'^(.+?)(\d+\.\d+)%$', lang_str)
        if match:
            lang_name = match.group(1).strip()
            percentage = float(match.group(2))
            return lang_name, percentage

        # Return just language name
        if lang_str:
            return lang_str, None

        return None, None

    def _create_requirement_object(
        self,
        name: str,
        min_version: Optional[str] = None,
        max_version: Optional[str] = None,
        description: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a structured SoftwareSourceCode requirement object.

        Follows Codemeta 3.1 schema for softwareRequirements.

        Args:
            name: Name of the software/runtime
            min_version: Minimum version requirement
            max_version: Maximum version requirement
            description: Description of the requirement
            language: Programming language this requirement is for

        Returns:
            Dictionary representing a SoftwareSourceCode object
        """
        req_obj: Dict[str, Any] = {
            '@type': 'SoftwareSourceCode',
            'name': name,
        }

        # Add version information
        if min_version and max_version:
            req_obj['version'] = f'>= {min_version}, <= {max_version}'
        elif min_version:
            req_obj['version'] = f'>= {min_version}'
        elif max_version:
            req_obj['version'] = f'<= {max_version}'

        # Add description
        if description:
            req_obj['description'] = description

        # Add language (for reference)
        if language:
            req_obj['language'] = language

        return req_obj

    def _extract_from_package_files(self) -> List[str]:
        """Extract requirements from package manager files."""
        requirements = []

        # Python requirements.txt
        req_txt = self._get_value('requirements_txt_content')
        if req_txt:
            for line in req_txt.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)

        # Node.js package.json
        package_json = self._get_value('package_json_content')
        if package_json:
            try:
                data = json.loads(package_json)
                deps = data.get('dependencies', {})
                for pkg, version in deps.items():
                    requirements.append(f'{pkg} {version}')
            except (json.JSONDecodeError, ValueError):
                pass

        # Ruby Gemfile
        gemfile = self._get_value('gemfile_content')
        if gemfile:
            for line in gemfile.split('\n'):
                line = line.strip()
                if line.startswith('gem '):
                    requirements.append(line[4:])

        return requirements

    def _extract_from_readme(self, readme_content: str) -> List[str]:
        """Extract requirements from README content."""
        requirements = []

        # Look for requirements sections
        sections = re.split(
            r'#+\s*(requirements|dependencies|prerequisites|installation)',
            readme_content,
            flags=re.IGNORECASE
        )

        if len(sections) > 1:
            content = sections[1]
            # Extract lines that look like requirements
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Remove markdown formatting
                    line = re.sub(r'[`*_]', '', line)
                    if len(line) > 3 and len(line) < 100:
                        requirements.append(line)

        return requirements

    def _normalize_requirements(self, reqs: Any) -> List[str]:
        """Normalize requirements to list of strings."""
        if isinstance(reqs, str):
            return [reqs]
        elif isinstance(reqs, list):
            return reqs
        else:
            return []

    def _deduplicate_requirements(self, requirements: List[Any]) -> List[Any]:
        """Remove duplicate requirements while preserving order."""
        seen = set()
        unique = []

        for req in requirements:
            # Create a hashable key for comparison
            if isinstance(req, dict):
                key = req.get('name', str(req))
            else:
                key = str(req).lower()

            if key not in seen:
                seen.add(key)
                unique.append(req)

        return unique
