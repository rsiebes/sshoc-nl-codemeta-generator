"""
Tests for Programming Language Property Module
"""

import unittest
from src.properties.programming_language import ProgrammingLanguageMetadata


class TestProgrammingLanguageMetadata(unittest.TestCase):
    """Test cases for ProgrammingLanguageMetadata class."""

    def test_extract_from_array(self):
        """Test extracting languages from array."""
        raw_data = {
            'programmingLanguage': ['Python', 'JavaScript', 'TypeScript']
        }
        metadata = ProgrammingLanguageMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('programmingLanguage', result)
        self.assertEqual(result['programmingLanguage'], ['Python', 'JavaScript', 'TypeScript'])
        self.assertEqual(len(metadata.errors), 0)
    
    def test_extract_from_languages_field(self):
        """Test extracting from languages field (GitHub format)."""
        raw_data = {
            'languages': ['Python95.2%', 'JavaScript4.8%']
        }
        metadata = ProgrammingLanguageMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('programmingLanguage', result)
        self.assertEqual(result['programmingLanguage'], ['Python', 'JavaScript'])
    
    def test_extract_from_dict(self):
        """Test extracting from dictionary format."""
        raw_data = {
            'languages': {'Python': 95.2, 'JavaScript': 4.8}
        }
        metadata = ProgrammingLanguageMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('programmingLanguage', result)
        self.assertIn('Python', result['programmingLanguage'])
        self.assertIn('JavaScript', result['programmingLanguage'])
    
    def test_extract_single_language(self):
        """Test extracting single language."""
        raw_data = {
            'language': 'Python'
        }
        metadata = ProgrammingLanguageMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('programmingLanguage', result)
        self.assertEqual(result['programmingLanguage'], ['Python'])
    
    def test_extract_with_percentages(self):
        """Test extracting languages with percentages."""
        raw_data = {
            'languages': ['Python 95.2%', 'JavaScript 4.8%']
        }
        metadata = ProgrammingLanguageMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('programmingLanguage', result)
        self.assertEqual(result['programmingLanguage'], ['Python', 'JavaScript'])
    
    def test_extract_removes_duplicates(self):
        """Test that duplicate languages are removed."""
        raw_data = {
            'programmingLanguage': ['Python', 'python', 'PYTHON', 'JavaScript']
        }
        metadata = ProgrammingLanguageMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('programmingLanguage', result)
        # Should keep first occurrence and remove case-insensitive duplicates
        self.assertEqual(len(result['programmingLanguage']), 2)
        self.assertIn('Python', result['programmingLanguage'])
        self.assertIn('JavaScript', result['programmingLanguage'])
    
    def test_extract_empty_languages(self):
        """Test extraction with no languages."""
        raw_data = {}
        metadata = ProgrammingLanguageMetadata(raw_data)
        result = metadata.extract()
        
        self.assertEqual(result, {})
        self.assertEqual(len(metadata.warnings), 1)
    
    def test_clean_language_normalizes_case(self):
        """Test that language names are normalized."""
        raw_data = {
            'programmingLanguage': ['javascript', 'typescript', 'python']
        }
        metadata = ProgrammingLanguageMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('programmingLanguage', result)
        self.assertEqual(result['programmingLanguage'], ['JavaScript', 'TypeScript', 'Python'])
    
    def test_clean_language_handles_special_chars(self):
        """Test handling of special characters in language names."""
        raw_data = {
            'programmingLanguage': ['C++', 'C#', 'F#', 'Objective-C']
        }
        metadata = ProgrammingLanguageMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('programmingLanguage', result)
        self.assertIn('C++', result['programmingLanguage'])
        self.assertIn('C#', result['programmingLanguage'])
        self.assertIn('F#', result['programmingLanguage'])
        self.assertIn('Objective-C', result['programmingLanguage'])
    
    def test_extract_from_comma_separated(self):
        """Test extracting from comma-separated string."""
        raw_data = {
            'programmingLanguage': 'Python, JavaScript, TypeScript'
        }
        metadata = ProgrammingLanguageMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('programmingLanguage', result)
        self.assertEqual(result['programmingLanguage'], ['Python', 'JavaScript', 'TypeScript'])
    
    def test_extract_from_dict_list(self):
        """Test extracting from list of dicts."""
        raw_data = {
            'programmingLanguage': [
                {'name': 'Python'},
                {'language': 'JavaScript'}
            ]
        }
        metadata = ProgrammingLanguageMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('programmingLanguage', result)
        self.assertEqual(result['programmingLanguage'], ['Python', 'JavaScript'])
    
    def test_validate_languages_array(self):
        """Test validation of languages array."""
        raw_data = {
            'programmingLanguage': ['Python', 'JavaScript']
        }
        metadata = ProgrammingLanguageMetadata(raw_data)
        metadata.extract()
        metadata.validate()
        
        self.assertEqual(len(metadata.errors), 0)
    
    def test_validate_languages_not_array(self):
        """Test validation fails when languages is not an array."""
        metadata = ProgrammingLanguageMetadata({})
        metadata.metadata = {'programmingLanguage': 'not-an-array'}
        metadata.validate()
        
        self.assertGreater(len(metadata.errors), 0)
    
    def test_validate_language_not_string(self):
        """Test validation fails when language is not a string."""
        metadata = ProgrammingLanguageMetadata({})
        metadata.metadata = {'programmingLanguage': ['Python', 123, 'JavaScript']}
        metadata.validate()
        
        self.assertGreater(len(metadata.errors), 0)
    
    def test_validate_empty_language(self):
        """Test validation fails for empty language."""
        metadata = ProgrammingLanguageMetadata({})
        metadata.metadata = {'programmingLanguage': ['Python', '', 'JavaScript']}
        metadata.validate()
        
        self.assertGreater(len(metadata.errors), 0)
    
    def test_validate_long_language_warning(self):
        """Test validation warns for very long language names."""
        metadata = ProgrammingLanguageMetadata({})
        metadata.metadata = {'programmingLanguage': ['Python', 'a' * 60]}
        metadata.validate()
        
        self.assertGreater(len(metadata.warnings), 0)
    
    def test_validate_many_languages_warning(self):
        """Test validation warns for too many languages."""
        metadata = ProgrammingLanguageMetadata({})
        metadata.metadata = {'programmingLanguage': [f'Lang-{i}' for i in range(25)]}
        metadata.validate()
        
        self.assertGreater(len(metadata.warnings), 0)
    
    def test_to_codemeta_dict(self):
        """Test conversion to Codemeta format."""
        raw_data = {
            'programmingLanguage': ['Python', 'JavaScript', 'TypeScript']
        }
        metadata = ProgrammingLanguageMetadata(raw_data)
        metadata.extract()
        result = metadata.to_codemeta_dict()
        
        self.assertIn('programmingLanguage', result)
        self.assertEqual(result['programmingLanguage'], ['Python', 'JavaScript', 'TypeScript'])
    
    def test_to_codemeta_dict_empty(self):
        """Test conversion with no languages."""
        metadata = ProgrammingLanguageMetadata({})
        result = metadata.to_codemeta_dict()
        
        self.assertEqual(result, {})
    
    def test_normalize_csharp(self):
        """Test normalization of C# variants."""
        raw_data = {
            'programmingLanguage': ['csharp', 'C#', 'CSharp']
        }
        metadata = ProgrammingLanguageMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('programmingLanguage', result)
        # All should be normalized to C# and duplicates removed
        self.assertEqual(len(result['programmingLanguage']), 1)
        self.assertEqual(result['programmingLanguage'][0], 'C#')
    
    def test_normalize_fsharp(self):
        """Test normalization of F# variants."""
        raw_data = {
            'programmingLanguage': ['fsharp', 'F#', 'FSharp']
        }
        metadata = ProgrammingLanguageMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('programmingLanguage', result)
        # All should be normalized to F# and duplicates removed
        self.assertEqual(len(result['programmingLanguage']), 1)
        self.assertEqual(result['programmingLanguage'][0], 'F#')


if __name__ == '__main__':
    unittest.main()
