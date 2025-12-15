"""
Software Requirements Property Module

Handles extraction and validation of the 'softwareRequirements' Codemeta property.
Extracts software dependencies and runtime requirements from multiple sources including
package manager files, README content, and language inference.

Supports extraction from:
- Python: requirements.txt, setup.py, pyproject.toml, Pipfile
- Node.js: package.json, package-lock.json, yarn.lock
- Ruby: Gemfile, Gemfile.lock
- Java: pom.xml, build.gradle
- Go: go.mod, go.sum
- Rust: Cargo.toml, Cargo.lock
- PHP: composer.json, composer.lock
- README files with requirements sections
- Language-based inference
"""

from typing import Dict, List, Optional, Any, Union
import re
import json
from ..base_metadata import BaseMetadata


class SoftwareRequirementsMetadata(BaseMetadata):
    """Handles softwareRequirements metadata extraction and validation."""

    CODEMETA_PROPERTY = 'softwareRequirements'
    CODEMETA_TYPE = 'schema:Text'
    REQUIRED = False

    # Version constraint patterns
    VERSION_PATTERNS = {
        'exact': r'^==\s*(.+)$',
        'gte': r'^>=\s*(.+)$',
        'lte': r'^<=\s*(.+)$',
        'gt': r'^>\s*(.+)$',
        'lt': r'^<\s*(.+)$',
        'compatible': r'^~=\s*(.+)$',
        'semver_caret': r'^\^\s*(.+)$',
        'semver_tilde': r'^~\s*(.+)$',
    }

    def __init__(self, raw_data: Dict[str, Any]):
        """
        Initialize SoftwareRequirementsMetadata.

        Args:
            raw_data: Raw scraped data from GitHub repository
        """
        super().__init__(raw_data)

    def extract(self) -> Dict[str, Any]:
        """
        Extract software requirements from multiple sources.

        Sources are tried in priority order:
        1. Explicit softwareRequirements field
        2. Package manager files (requirements.txt, package.json, etc.)
        3. README content with requirements sections
        4. Language-based inference

        Returns:
            Dictionary with 'softwareRequirements' key containing array of requirements
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

        # 3. Extract from README requirements section
        if not requirements:
            readme_content = self._get_value('readme_content')
            if readme_content:
                readme_reqs = self._extract_from_readme(readme_content)
                if readme_reqs:
                    requirements.extend(readme_reqs)

        # 4. Infer from programming language
        if not requirements:
            prog_langs = self._get_value('languages')
            if prog_langs:
                lang_reqs = self._infer_from_language(prog_langs)
                if lang_reqs:
                    requirements.extend(lang_reqs)

        # Remove duplicates while preserving order
        if requirements:
            unique_requirements = self._deduplicate_requirements(requirements)
            self.metadata[self.CODEMETA_PROPERTY] = unique_requirements
            return self.metadata

        self.add_warning(f"Optional field '{self.CODEMETA_PROPERTY}' could not be extracted")
        return {}

    def _normalize_requirements(self, value: Any) -> List[Union[str, Dict[str, Any]]]:
        """
        Normalize requirements from various input formats.

        Args:
            value: Raw requirements value (string, list, dict, or other)

        Returns:
            List of normalized requirement strings or objects
        """
        requirements = []

        if isinstance(value, str):
            # Single requirement as string
            if value.strip():
                requirements.append(value.strip())

        elif isinstance(value, list):
            # List of requirements
            for item in value:
                if isinstance(item, str) and item.strip():
                    requirements.append(item.strip())
                elif isinstance(item, dict):
                    requirements.append(item)

        elif isinstance(value, dict):
            # Single requirement as dict
            requirements.append(value)

        return requirements

    def _extract_from_package_files(self) -> List[str]:
        """
        Extract requirements from package manager files.

        Supports: requirements.txt, package.json, Gemfile, pom.xml, go.mod,
        Cargo.toml, composer.json, setup.py, pyproject.toml, Pipfile

        Returns:
            List of extracted requirements
        """
        requirements = []

        # Python: requirements.txt
        req_txt = self._get_value('requirements_txt_content')
        if req_txt:
            requirements.extend(self._parse_requirements_txt(req_txt))

        # Python: setup.py
        setup_py = self._get_value('setup_py_content')
        if setup_py and not requirements:
            requirements.extend(self._parse_setup_py(setup_py))

        # Python: pyproject.toml
        pyproject = self._get_value('pyproject_toml_content')
        if pyproject and not requirements:
            requirements.extend(self._parse_pyproject_toml(pyproject))

        # Python: Pipfile
        pipfile = self._get_value('pipfile_content')
        if pipfile and not requirements:
            requirements.extend(self._parse_pipfile(pipfile))

        # Node.js: package.json
        package_json = self._get_value('package_json_content')
        if package_json and not requirements:
            requirements.extend(self._parse_package_json(package_json))

        # Ruby: Gemfile
        gemfile = self._get_value('gemfile_content')
        if gemfile and not requirements:
            requirements.extend(self._parse_gemfile(gemfile))

        # Java: pom.xml
        pom_xml = self._get_value('pom_xml_content')
        if pom_xml and not requirements:
            requirements.extend(self._parse_pom_xml(pom_xml))

        # Go: go.mod
        go_mod = self._get_value('go_mod_content')
        if go_mod and not requirements:
            requirements.extend(self._parse_go_mod(go_mod))

        # Rust: Cargo.toml
        cargo_toml = self._get_value('cargo_toml_content')
        if cargo_toml and not requirements:
            requirements.extend(self._parse_cargo_toml(cargo_toml))

        # PHP: composer.json
        composer_json = self._get_value('composer_json_content')
        if composer_json and not requirements:
            requirements.extend(self._parse_composer_json(composer_json))

        return requirements

    def _parse_requirements_txt(self, content: str) -> List[str]:
        """
        Parse Python requirements.txt file.

        Args:
            content: Content of requirements.txt

        Returns:
            List of requirement strings
        """
        requirements = []
        for line in content.split('\n'):
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            # Skip option lines
            if line.startswith('-'):
                continue
            # Extract requirement (remove inline comments)
            if '#' in line:
                line = line.split('#')[0].strip()
            if line:
                requirements.append(line)

        return requirements[:20]  # Limit to first 20

    def _parse_setup_py(self, content: str) -> List[str]:
        """
        Parse Python setup.py file.

        Args:
            content: Content of setup.py

        Returns:
            List of requirement strings
        """
        requirements = []

        # Look for install_requires
        install_requires_match = re.search(
            r'install_requires\s*=\s*\[(.*?)\]',
            content,
            re.DOTALL
        )
        if install_requires_match:
            requires_str = install_requires_match.group(1)
            # Extract quoted strings
            quoted_reqs = re.findall(r'["\']([^"\']+)["\']', requires_str)
            requirements.extend(quoted_reqs)

        # Look for python_requires
        python_requires_match = re.search(
            r'python_requires\s*=\s*["\']([^"\']+)["\']',
            content
        )
        if python_requires_match:
            python_version = python_requires_match.group(1)
            requirements.insert(0, f'Python {python_version}')

        return requirements[:20]

    def _parse_pyproject_toml(self, content: str) -> List[str]:
        """
        Parse Python pyproject.toml file.

        Args:
            content: Content of pyproject.toml

        Returns:
            List of requirement strings
        """
        requirements = []

        # Look for dependencies section
        deps_match = re.search(
            r'\[project\].*?dependencies\s*=\s*\[(.*?)\]',
            content,
            re.DOTALL
        )
        if deps_match:
            deps_str = deps_match.group(1)
            # Extract quoted strings
            quoted_deps = re.findall(r'["\']([^"\']+)["\']', deps_str)
            requirements.extend(quoted_deps)

        # Look for requires-python
        python_match = re.search(
            r'requires-python\s*=\s*["\']([^"\']+)["\']',
            content
        )
        if python_match:
            python_version = python_match.group(1)
            requirements.insert(0, f'Python {python_version}')

        return requirements[:20]

    def _parse_pipfile(self, content: str) -> List[str]:
        """
        Parse Python Pipfile.

        Args:
            content: Content of Pipfile

        Returns:
            List of requirement strings
        """
        requirements = []

        # Look for [packages] section
        packages_match = re.search(
            r'\[packages\](.*?)(?:\[|$)',
            content,
            re.DOTALL
        )
        if packages_match:
            packages_str = packages_match.group(1)
            # Extract package names
            package_names = re.findall(r'^(\w+)\s*=', packages_str, re.MULTILINE)
            requirements.extend(package_names)

        # Look for python_version
        python_match = re.search(
            r'\[requires\].*?python_version\s*=\s*["\']([^"\']+)["\']',
            content,
            re.DOTALL
        )
        if python_match:
            python_version = python_match.group(1)
            requirements.insert(0, f'Python {python_version}')

        return requirements[:20]

    def _parse_package_json(self, content: str) -> List[str]:
        """
        Parse Node.js package.json file.

        Args:
            content: Content of package.json

        Returns:
            List of requirement strings
        """
        requirements = []

        try:
            data = json.loads(content)

            # Get Node.js version requirement
            engines = data.get('engines', {})
            if 'node' in engines:
                requirements.append(f'Node.js {engines["node"]}')

            # Get dependencies
            dependencies = data.get('dependencies', {})
            for pkg_name, version in list(dependencies.items())[:10]:
                requirements.append(f'{pkg_name} {version}')

        except (json.JSONDecodeError, ValueError):
            pass

        return requirements[:20]

    def _parse_gemfile(self, content: str) -> List[str]:
        """
        Parse Ruby Gemfile.

        Args:
            content: Content of Gemfile

        Returns:
            List of requirement strings
        """
        requirements = []

        # Look for ruby version
        ruby_match = re.search(r"ruby\s+['\"]([^'\"]+)['\"]", content)
        if ruby_match:
            ruby_version = ruby_match.group(1)
            requirements.append(f'Ruby {ruby_version}')

        # Extract gem declarations
        gem_matches = re.findall(r"gem\s+['\"]([^'\"]+)['\"](?:,\s+['\"]([^'\"]+)['\"])?", content)
        for gem_match in gem_matches[:10]:
            if gem_match[1]:
                requirements.append(f'{gem_match[0]} {gem_match[1]}')
            else:
                requirements.append(gem_match[0])

        return requirements[:20]

    def _parse_pom_xml(self, content: str) -> List[str]:
        """
        Parse Java pom.xml file.

        Args:
            content: Content of pom.xml

        Returns:
            List of requirement strings
        """
        requirements = []

        # Look for Java version
        java_match = re.search(
            r'<source>([^<]+)</source>',
            content
        )
        if java_match:
            java_version = java_match.group(1)
            requirements.append(f'Java >= {java_version}')

        # Extract dependencies (limited)
        dep_matches = re.findall(
            r'<artifactId>([^<]+)</artifactId>',
            content
        )
        for dep in dep_matches[:10]:
            requirements.append(dep)

        return requirements[:20]

    def _parse_go_mod(self, content: str) -> List[str]:
        """
        Parse Go go.mod file.

        Args:
            content: Content of go.mod

        Returns:
            List of requirement strings
        """
        requirements = []

        # Look for go version
        go_match = re.search(r'^go\s+(\d+\.\d+)', content, re.MULTILINE)
        if go_match:
            go_version = go_match.group(1)
            requirements.append(f'Go >= {go_version}')

        # Extract require statements (limited)
        require_matches = re.findall(
            r'^\s+([^\s/]+/[^\s]+)\s+v([^\s]+)',
            content,
            re.MULTILINE
        )
        for module, version in require_matches[:10]:
            requirements.append(f'{module} {version}')

        return requirements[:20]

    def _parse_cargo_toml(self, content: str) -> List[str]:
        """
        Parse Rust Cargo.toml file.

        Args:
            content: Content of Cargo.toml

        Returns:
            List of requirement strings
        """
        requirements = []

        # Look for Rust version
        rust_match = re.search(r'rust-version\s*=\s*["\']([^"\']+)["\']', content)
        if rust_match:
            rust_version = rust_match.group(1)
            requirements.append(f'Rust >= {rust_version}')

        # Extract dependencies (limited)
        dep_matches = re.findall(
            r'^\s*(\w+)\s*=\s*["\']([^"\']+)["\']',
            content,
            re.MULTILINE
        )
        for dep_name, version in dep_matches[:10]:
            requirements.append(f'{dep_name} {version}')

        return requirements[:20]

    def _parse_composer_json(self, content: str) -> List[str]:
        """
        Parse PHP composer.json file.

        Args:
            content: Content of composer.json

        Returns:
            List of requirement strings
        """
        requirements = []

        try:
            data = json.loads(content)

            # Get PHP version requirement
            if 'require' in data and 'php' in data['require']:
                php_version = data['require']['php']
                requirements.append(f'PHP {php_version}')

            # Get dependencies (limited)
            require = data.get('require', {})
            for pkg_name, version in list(require.items())[:10]:
                if pkg_name != 'php':
                    requirements.append(f'{pkg_name} {version}')

        except (json.JSONDecodeError, ValueError):
            pass

        return requirements[:20]

    def _extract_from_readme(self, readme: str) -> List[str]:
        """
        Extract requirements from README content.

        Looks for requirements/dependencies/prerequisites sections and
        extracts requirement strings from lists and code blocks.

        Args:
            readme: README content

        Returns:
            List of requirement strings
        """
        requirements = []

        # Look for requirements/dependencies sections (Markdown headers)
        patterns = [
            r'#{1,3}\s+(?:requirements|dependencies|prerequisites|installation|setup)\s*\n(.*?)(?=\n#{1,3}|\Z)',
            r'#{1,3}\s+(?:requirements|dependencies|prerequisites|installation|setup)\s*\n(.*?)(?=\n#{1,6}|\Z)',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, readme, re.IGNORECASE | re.DOTALL)
            for match in matches:
                section = match.group(1)

                # Extract items from bullet lists
                list_items = re.findall(r'[-*+]\s+(.+?)(?:\n|$)', section)
                for item in list_items:
                    item = item.strip()
                    # Remove markdown formatting
                    item = re.sub(r'`([^`]+)`', r'\1', item)
                    item = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', item)
                    # Remove trailing punctuation and extra text
                    item = re.sub(r'\s*[-–—].*$', '', item)
                    if item and len(item) < 100:
                        requirements.append(item)

                # Extract from code blocks
                code_blocks = re.findall(r'```(?:bash|shell|text)?\n(.*?)\n```', section, re.DOTALL)
                for code_block in code_blocks:
                    for line in code_block.split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            requirements.append(line)

        return requirements[:15]  # Limit to first 15

    def _infer_from_language(self, languages: List[str]) -> List[str]:
        """
        Infer basic requirements from programming language.

        Maps programming languages to their typical runtime requirements.

        Args:
            languages: List of programming languages (may include percentages)

        Returns:
            List of inferred requirements
        """
        requirements = []

        if not isinstance(languages, list):
            languages = [languages]

        # Parse language names (remove percentages like "Python 70.5%")
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
            'C#': '.NET >= 5.0',
            'Kotlin': 'Kotlin >= 1.4',
            'Swift': 'Swift >= 5.0',
            'Scala': 'Scala >= 2.12',
        }

        for lang in languages:
            if lang in language_map:
                requirements.append(language_map[lang])

        return requirements

    def _deduplicate_requirements(self, requirements: List[Union[str, Dict]]) -> List[Union[str, Dict]]:
        """
        Remove duplicate requirements while preserving order.

        Args:
            requirements: List of requirement strings or objects

        Returns:
            List of unique requirements
        """
        seen = set()
        unique = []

        for req in requirements:
            if isinstance(req, str):
                req_lower = req.lower()
                if req_lower not in seen:
                    seen.add(req_lower)
                    unique.append(req)
            elif isinstance(req, dict):
                # For dict objects, use name as key
                req_name = req.get('name', '').lower()
                if req_name and req_name not in seen:
                    seen.add(req_name)
                    unique.append(req)
                elif not req_name:
                    unique.append(req)

        return unique

    def _validate_metadata(self) -> None:
        """
        Validate softwareRequirements metadata.

        Checks:
        - Field is a list
        - Each requirement is string or dict
        - Requirement strings are reasonable length
        - Dict requirements have required fields
        """
        if not self.metadata or self.CODEMETA_PROPERTY not in self.metadata:
            return

        reqs = self.metadata[self.CODEMETA_PROPERTY]

        # Validate it's a list
        if not isinstance(reqs, list):
            self.add_error(f'{self.CODEMETA_PROPERTY} must be a list, got {type(reqs).__name__}')
            return

        # Validate each requirement
        for i, req in enumerate(reqs):
            if isinstance(req, str):
                # Validate string length
                if len(req) > 200:
                    self.add_warning(f'Requirement {i+1} string too long: {req[:50]}...')
                # Warn on suspicious patterns
                if req.count('http') > 1:
                    self.add_warning(f'Requirement {i+1} contains multiple URLs: {req[:50]}...')

            elif isinstance(req, dict):
                # Validate dict structure
                if 'name' not in req:
                    self.add_warning(f'Requirement {i+1} dict missing "name" field')
                if 'version' in req and not self._is_valid_version_constraint(req['version']):
                    self.add_warning(f'Requirement {i+1} has invalid version constraint: {req["version"]}')

            else:
                self.add_warning(f'Requirement {i+1} has invalid type: {type(req).__name__}')

    def _is_valid_version_constraint(self, version: str) -> bool:
        """
        Check if a version constraint string is valid.

        Args:
            version: Version constraint string

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(version, str):
            return False

        version = version.strip()
        if not version:
            return False

        # Check against known patterns
        for pattern in self.VERSION_PATTERNS.values():
            if re.match(pattern, version):
                return True

        # Allow simple version numbers
        if re.match(r'^\d+(\.\d+)*$', version):
            return True

        return False

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
