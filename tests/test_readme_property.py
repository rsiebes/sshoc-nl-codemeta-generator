"""
Tests for the readme property module.
"""

import unittest
from src.properties.readme import ReadmeMetadata


class TestReadmeMetadata(unittest.TestCase):
    """Test cases for ReadmeMetadata class."""
    
    def test_extract_from_readme_url(self):
        """Test extracting readme from direct URL."""
        raw_data = {
            'readme': 'https://github.com/owner/repo#readme'
        }
        metadata = ReadmeMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('readme', result)
        self.assertEqual(result['readme'], 'https://github.com/owner/repo#readme')
    
    def test_extract_from_readme_url_field(self):
        """Test extracting from readme_url field."""
        raw_data = {
            'readme_url': 'https://github.com/owner/repo/blob/main/README.md'
        }
        metadata = ReadmeMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('readme', result)
        self.assertEqual(result['readme'], 'https://github.com/owner/repo/blob/main/README.md')
    
    def test_extract_from_documentation(self):
        """Test extracting from documentation field."""
        raw_data = {
            'documentation': 'https://docs.example.com/readme'
        }
        metadata = ReadmeMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('readme', result)
        self.assertEqual(result['readme'], 'https://docs.example.com/readme')
    
    def test_construct_from_github_repo(self):
        """Test constructing README URL from GitHub repository."""
        raw_data = {
            'code_repository': 'https://github.com/owner/repo'
        }
        metadata = ReadmeMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('readme', result)
        self.assertEqual(result['readme'], 'https://github.com/owner/repo#readme')
    
    def test_construct_from_gitlab_repo(self):
        """Test constructing README URL from GitLab repository."""
        raw_data = {
            'code_repository': 'https://gitlab.com/owner/repo'
        }
        metadata = ReadmeMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('readme', result)
        self.assertEqual(result['readme'], 'https://gitlab.com/owner/repo#readme')
    
    def test_construct_from_bitbucket_repo(self):
        """Test constructing README URL from Bitbucket repository."""
        raw_data = {
            'code_repository': 'https://bitbucket.org/owner/repo'
        }
        metadata = ReadmeMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('readme', result)
        self.assertEqual(result['readme'], 'https://bitbucket.org/owner/repo#readme')
    
    def test_readme_text_constructs_url(self):
        """Test that readme text content constructs URL from repository."""
        raw_data = {
            'readme': '# My Project\n\nThis is a README',
            'code_repository': 'https://github.com/owner/repo'
        }
        metadata = ReadmeMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('readme', result)
        self.assertEqual(result['readme'], 'https://github.com/owner/repo#readme')
    
    def test_no_readme(self):
        """Test when no readme is available."""
        raw_data = {}
        metadata = ReadmeMetadata(raw_data)
        result = metadata.extract()
        
        self.assertNotIn('readme', result)
    
    def test_validate_readme_url(self):
        """Test validation of readme URL."""
        raw_data = {
            'readme': 'https://github.com/owner/repo#readme'
        }
        metadata = ReadmeMetadata(raw_data)
        metadata.extract()
        metadata.validate()
        
        self.assertEqual(len(metadata.errors), 0)
        self.assertEqual(len(metadata.warnings), 0)
    
    def test_validate_readme_not_string(self):
        """Test validation fails when readme is not a string."""
        raw_data = {}
        metadata = ReadmeMetadata(raw_data)
        metadata.metadata = {'readme': 123}
        metadata.validate()
        
        self.assertGreater(len(metadata.errors), 0)
        self.assertIn("must be a string", metadata.errors[0])
    
    def test_validate_readme_empty(self):
        """Test validation fails for empty readme."""
        raw_data = {}
        metadata = ReadmeMetadata(raw_data)
        metadata.metadata = {'readme': '   '}
        metadata.validate()
        
        self.assertGreater(len(metadata.errors), 0)
        self.assertIn("cannot be empty", metadata.errors[0])
    
    def test_validate_readme_invalid_url(self):
        """Test validation warns for invalid URL format."""
        raw_data = {}
        metadata = ReadmeMetadata(raw_data)
        metadata.metadata = {'readme': 'not-a-url'}
        metadata.validate()
        
        self.assertGreater(len(metadata.warnings), 0)
        self.assertIn("valid URL", metadata.warnings[0])
    
    def test_validate_readme_very_long(self):
        """Test validation warns for very long URL."""
        raw_data = {}
        metadata = ReadmeMetadata(raw_data)
        metadata.metadata = {'readme': 'https://example.com/' + 'a' * 2000}
        metadata.validate()
        
        self.assertGreater(len(metadata.warnings), 0)
        self.assertIn("very long", metadata.warnings[0])
    
    def test_to_codemeta_dict(self):
        """Test conversion to Codemeta format."""
        raw_data = {
            'readme': 'https://github.com/owner/repo#readme'
        }
        metadata = ReadmeMetadata(raw_data)
        metadata.extract()
        codemeta = metadata.to_codemeta_dict()
        
        self.assertIn('readme', codemeta)
        self.assertEqual(codemeta['readme'], 'https://github.com/owner/repo#readme')
    
    def test_to_codemeta_dict_empty(self):
        """Test conversion with no readme."""
        raw_data = {}
        metadata = ReadmeMetadata(raw_data)
        metadata.extract()
        codemeta = metadata.to_codemeta_dict()
        
        self.assertEqual(codemeta, {})


if __name__ == '__main__':
    unittest.main()
