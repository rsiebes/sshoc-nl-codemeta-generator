"""
Test suite for core Codemeta property modules.

Tests extraction, validation, and conversion of core properties:
- name
- description
- url
- version
- codeRepository
"""

import unittest
from src.properties.name import NameMetadata
from src.properties.description import DescriptionMetadata
from src.properties.url import UrlMetadata
from src.properties.version import VersionMetadata
from src.properties.code_repository import CodeRepositoryMetadata


class TestNameMetadata(unittest.TestCase):
    """Test cases for NameMetadata."""

    def test_extract_from_name_field(self):
        """Test extracting name from direct 'name' field."""
        raw_data = {'name': 'TestSoftware'}
        metadata = NameMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('name', result)
        self.assertEqual(result['name'], 'TestSoftware')

    def test_extract_from_repo_name(self):
        """Test extracting name from 'repo_name' field."""
        raw_data = {'repo_name': 'my-repo'}
        metadata = NameMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('name', result)
        self.assertEqual(result['name'], 'my-repo')

    def test_extract_empty_name(self):
        """Test extraction with empty name."""
        raw_data = {}
        metadata = NameMetadata(raw_data)
        result = metadata.extract()
        
        self.assertEqual(result, {})
        self.assertTrue(len(metadata.get_errors()) > 0)

    def test_validate_required_field(self):
        """Test validation of required name field."""
        raw_data = {}
        metadata = NameMetadata(raw_data)
        metadata.extract()
        is_valid = metadata.validate()
        
        self.assertFalse(is_valid)
        self.assertTrue(any('required' in err.lower() for err in metadata.get_errors()))

    def test_to_codemeta_dict(self):
        """Test conversion to Codemeta format."""
        raw_data = {'name': 'TestSoftware'}
        metadata = NameMetadata(raw_data)
        metadata.extract()
        result = metadata.to_codemeta_dict()
        
        self.assertIn('name', result)
        self.assertEqual(result['name'], 'TestSoftware')


class TestDescriptionMetadata(unittest.TestCase):
    """Test cases for DescriptionMetadata."""

    def test_extract_from_description_field(self):
        """Test extracting description from direct field."""
        raw_data = {'description': 'This is a test software'}
        metadata = DescriptionMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('description', result)
        self.assertEqual(result['description'], 'This is a test software')

    def test_extract_from_readme(self):
        """Test extracting description from README."""
        readme_text = "# My Project\n\nThis is the first paragraph.\n\nThis is the second paragraph."
        raw_data = {'readme': readme_text}
        metadata = DescriptionMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('description', result)
        # The first paragraph after header should be extracted
        self.assertIn('first paragraph', result['description'].lower())

    def test_validate_description_length(self):
        """Test validation of description length."""
        raw_data = {'description': 'x' * 6000}  # Too long
        metadata = DescriptionMetadata(raw_data)
        metadata.extract()
        metadata.validate()
        
        self.assertTrue(any('long' in warn.lower() for warn in metadata.get_warnings()))

    def test_to_codemeta_dict(self):
        """Test conversion to Codemeta format."""
        raw_data = {'description': 'Test description'}
        metadata = DescriptionMetadata(raw_data)
        metadata.extract()
        result = metadata.to_codemeta_dict()
        
        self.assertIn('description', result)


class TestUrlMetadata(unittest.TestCase):
    """Test cases for UrlMetadata."""

    def test_extract_valid_url(self):
        """Test extracting a valid URL."""
        raw_data = {'url': 'https://example.com'}
        metadata = UrlMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('url', result)
        self.assertEqual(result['url'], 'https://example.com')

    def test_extract_url_without_protocol(self):
        """Test extracting URL without protocol."""
        raw_data = {'url': 'example.com'}
        metadata = UrlMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('url', result)
        self.assertTrue(result['url'].startswith('https://'))

    def test_validate_invalid_url(self):
        """Test validation of invalid URL."""
        raw_data = {'url': 'not a url'}
        metadata = UrlMetadata(raw_data)
        result = metadata.extract()
        
        # URL will be normalized to https://not a url which is invalid
        # Validation should catch this
        metadata.validate()
        self.assertTrue(len(metadata.get_errors()) > 0 or len(metadata.get_warnings()) > 0)

    def test_to_codemeta_dict(self):
        """Test conversion to Codemeta format."""
        raw_data = {'url': 'https://example.com'}
        metadata = UrlMetadata(raw_data)
        metadata.extract()
        result = metadata.to_codemeta_dict()
        
        self.assertIn('url', result)


class TestVersionMetadata(unittest.TestCase):
    """Test cases for VersionMetadata."""

    def test_extract_version_string(self):
        """Test extracting version from string."""
        raw_data = {'version': '1.2.3'}
        metadata = VersionMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('version', result)
        self.assertEqual(result['version'], '1.2.3')

    def test_extract_version_with_v_prefix(self):
        """Test extracting version with 'v' prefix."""
        raw_data = {'version': 'v1.2.3'}
        metadata = VersionMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('version', result)
        self.assertEqual(result['version'], '1.2.3')

    def test_extract_from_releases(self):
        """Test extracting version from releases."""
        raw_data = {
            'releases': [
                {'tag': '2.0.0'},
                {'tag': '1.0.0'}
            ]
        }
        metadata = VersionMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('version', result)
        self.assertEqual(result['version'], '2.0.0')

    def test_validate_version_format(self):
        """Test validation of version format."""
        raw_data = {'version': '1.2.3'}
        metadata = VersionMetadata(raw_data)
        metadata.extract()
        is_valid = metadata.validate()
        
        self.assertTrue(is_valid)

    def test_to_codemeta_dict(self):
        """Test conversion to Codemeta format."""
        raw_data = {'version': '1.0.0'}
        metadata = VersionMetadata(raw_data)
        metadata.extract()
        result = metadata.to_codemeta_dict()
        
        self.assertIn('version', result)


class TestCodeRepositoryMetadata(unittest.TestCase):
    """Test cases for CodeRepositoryMetadata."""

    def test_extract_repository_url(self):
        """Test extracting repository URL."""
        raw_data = {'code_repository': 'https://github.com/user/repo'}
        metadata = CodeRepositoryMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('codeRepository', result)
        self.assertEqual(result['codeRepository'], 'https://github.com/user/repo')

    def test_extract_from_owner_and_name(self):
        """Test constructing repository URL from owner and name."""
        raw_data = {'owner': 'user', 'name': 'repo'}
        metadata = CodeRepositoryMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('codeRepository', result)
        self.assertEqual(result['codeRepository'], 'https://github.com/user/repo')

    def test_normalize_repository_url(self):
        """Test normalizing repository URL."""
        raw_data = {'code_repository': 'https://github.com/user/repo.git/'}
        metadata = CodeRepositoryMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('codeRepository', result)
        self.assertFalse(result['codeRepository'].endswith('.git'))
        self.assertFalse(result['codeRepository'].endswith('/'))

    def test_validate_repository_url(self):
        """Test validation of repository URL."""
        raw_data = {'code_repository': 'https://github.com/user/repo'}
        metadata = CodeRepositoryMetadata(raw_data)
        metadata.extract()
        is_valid = metadata.validate()
        
        self.assertTrue(is_valid)

    def test_to_codemeta_dict(self):
        """Test conversion to Codemeta format."""
        raw_data = {'code_repository': 'https://github.com/user/repo'}
        metadata = CodeRepositoryMetadata(raw_data)
        metadata.extract()
        result = metadata.to_codemeta_dict()
        
        self.assertIn('codeRepository', result)


if __name__ == '__main__':
    unittest.main()
