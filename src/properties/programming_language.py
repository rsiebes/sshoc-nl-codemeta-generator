"""
Programming Language Property Module

Handles extraction and validation of the 'programmingLanguage' Codemeta property.
Extracts and formats the programming languages used in the software.
"""

from typing import Dict, Any, Optional, List, Union
import re
from src.base_metadata import BaseMetadata


class ProgrammingLanguageMetadata(BaseMetadata):
    """Handles programmingLanguage metadata extraction and validation."""

    CODEMETA_PROPERTY = 'programmingLanguage'
    CODEMETA_TYPE = 'schema:ComputerLanguage'
    REQUIRED = False

    def extract(self) -> Dict[str, Any]:
        """
        Extract programming languages from raw data.

        Languages can come from:
        1. Direct 'programmingLanguage' field
        2. 'languages' field (GitHub language statistics)
        3. 'language' field (primary language)
        4. 'programming_languages' field

        Returns:
            Dictionary with 'programmingLanguage' key containing array of languages
        """
        languages = []
        
        # Try to extract from different sources
        raw_languages = self._get_value('programmingLanguage')
        if raw_languages:
            languages.extend(self._process_languages(raw_languages))
        
        # Try languages field (GitHub language statistics)
        if not languages:
            github_languages = self._get_value('languages')
            if github_languages:
                languages.extend(self._process_languages(github_languages))
        
        # Try language field (primary language)
        if not languages:
            primary_language = self._get_value('language')
            if primary_language:
                languages.extend(self._process_languages(primary_language))
        
        # Try programming_languages field
        if not languages:
            prog_langs = self._get_value('programming_languages')
            if prog_langs:
                languages.extend(self._process_languages(prog_langs))
        
        if not languages:
            self.add_warning(f"Optional field '{self.CODEMETA_PROPERTY}' could not be extracted")
            return {}
        
        # Remove duplicates while preserving order
        unique_languages = []
        seen = set()
        for lang in languages:
            lang_lower = lang.lower()
            if lang_lower not in seen:
                seen.add(lang_lower)
                unique_languages.append(lang)
        
        if unique_languages:
            self.metadata[self.CODEMETA_PROPERTY] = unique_languages
            return self.metadata
        else:
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' could not be processed")
            return {}

    def _process_languages(self, value: Any) -> List[str]:
        """
        Process and normalize programming languages from various formats.

        Args:
            value: Raw languages value (string, list, dict, or other)

        Returns:
            List of normalized language names
        """
        languages = []
        
        if isinstance(value, str):
            # Handle comma-separated string
            if ',' in value:
                languages = [self._clean_language(lang) for lang in value.split(',')]
            # Handle semicolon-separated string
            elif ';' in value:
                languages = [self._clean_language(lang) for lang in value.split(';')]
            # Handle single language with percentage (e.g., "Python 95.2%")
            elif '%' in value:
                lang = self._extract_language_name(value)
                if lang:
                    languages = [lang]
            # Single language
            else:
                lang = self._clean_language(value)
                if lang:
                    languages = [lang]
        
        elif isinstance(value, list):
            # Handle list of languages
            for item in value:
                if isinstance(item, str):
                    # Check if it has percentage
                    if '%' in item:
                        lang = self._extract_language_name(item)
                        if lang:
                            languages.append(lang)
                    else:
                        lang = self._clean_language(item)
                        if lang:
                            languages.append(lang)
                elif isinstance(item, dict):
                    # Handle dict with 'name' or 'language' key
                    lang = item.get('name') or item.get('language')
                    if lang and isinstance(lang, str):
                        lang = self._clean_language(lang)
                        if lang:
                            languages.append(lang)
        
        elif isinstance(value, dict):
            # Handle dict of languages (e.g., {"Python": 95.2, "JavaScript": 4.8})
            for lang_name in value.keys():
                lang = self._clean_language(lang_name)
                if lang:
                    languages.append(lang)
        
        # Filter out invalid languages
        valid_languages = [lang for lang in languages if self._is_valid_language(lang)]
        
        return valid_languages

    def _extract_language_name(self, text: str) -> Optional[str]:
        """
        Extract language name from text with percentage.

        Args:
            text: Text like "Python95.2%" or "Python 95.2%"

        Returns:
            Language name without percentage
        """
        # Remove percentage and numbers
        match = re.match(r'^([a-zA-Z\+\#\s]+?)[\d\.\s]*%?$', text)
        if match:
            return self._clean_language(match.group(1))
        return self._clean_language(text)

    def _clean_language(self, language: str) -> Optional[str]:
        """
        Clean and normalize language name.

        Args:
            language: Raw language name

        Returns:
            Cleaned language name or None
        """
        if not isinstance(language, str):
            return None
        
        # Remove extra whitespace
        language = language.strip()
        
        if not language:
            return None
        
        # Remove percentages and numbers
        language = re.sub(r'[\d\.]+%?$', '', language).strip()
        
        # Remove special characters except + and #
        language = re.sub(r'[^\w\s\+\#\-]', '', language).strip()
        
        if not language:
            return None
        
        # Normalize common language names
        language_map = {
            'javascript': 'JavaScript',
            'typescript': 'TypeScript',
            'python': 'Python',
            'java': 'Java',
            'c++': 'C++',
            'c#': 'C#',
            'csharp': 'C#',
            'c': 'C',
            'ruby': 'Ruby',
            'go': 'Go',
            'rust': 'Rust',
            'php': 'PHP',
            'swift': 'Swift',
            'kotlin': 'Kotlin',
            'scala': 'Scala',
            'r': 'R',
            'matlab': 'MATLAB',
            'perl': 'Perl',
            'shell': 'Shell',
            'bash': 'Bash',
            'powershell': 'PowerShell',
            'html': 'HTML',
            'css': 'CSS',
            'sql': 'SQL',
            'objective-c': 'Objective-C',
            'dart': 'Dart',
            'lua': 'Lua',
            'haskell': 'Haskell',
            'clojure': 'Clojure',
            'elixir': 'Elixir',
            'erlang': 'Erlang',
            'f#': 'F#',
            'fsharp': 'F#',
            'groovy': 'Groovy',
            'julia': 'Julia',
            'prolog': 'Prolog',
        }
        
        # Normalize to proper case
        language_lower = language.lower()
        if language_lower in language_map:
            return language_map[language_lower]
        
        # Return with first letter capitalized if not in map
        return language.title()

    def _is_valid_language(self, language: str) -> bool:
        """
        Check if language name is valid.

        Args:
            language: Language name to check

        Returns:
            True if valid, False otherwise
        """
        if not language or len(language) < 1:
            return False
        
        if len(language) > 50:
            return False
        
        # Must contain at least one letter
        if not re.search(r'[a-zA-Z]', language):
            return False
        
        return True

    def _validate_metadata(self) -> None:
        """Validate programmingLanguage metadata."""
        if not self.metadata:
            if self.REQUIRED:
                self.add_error(f"Required field '{self.CODEMETA_PROPERTY}' is missing")
            return

        languages = self.metadata.get(self.CODEMETA_PROPERTY)
        
        if not languages:
            if self.REQUIRED:
                self.add_error(f"'{self.CODEMETA_PROPERTY}' is empty")
            return
        
        # Validate that languages is a list
        if not isinstance(languages, list):
            self.add_error(f"'{self.CODEMETA_PROPERTY}' must be an array, got {type(languages).__name__}")
            return
        
        # Validate each language
        for i, lang in enumerate(languages):
            if not isinstance(lang, str):
                self.add_error(f"Language {i+1} must be a string, got {type(lang).__name__}")
            elif not lang.strip():
                self.add_error(f"Language {i+1} is empty")
            elif len(lang) > 50:
                self.add_warning(f"Language {i+1} is very long ({len(lang)} characters)")
        
        # Check for reasonable number of languages
        if len(languages) > 20:
            self.add_warning(f"Large number of languages ({len(languages)}), consider reducing")
        elif len(languages) == 0:
            self.add_warning("Languages array is empty")

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
