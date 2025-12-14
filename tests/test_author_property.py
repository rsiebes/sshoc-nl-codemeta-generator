"""
Tests for Author Property Module
"""

import unittest
from src.properties.author import AuthorMetadata


class TestAuthorMetadata(unittest.TestCase):
    """Test cases for AuthorMetadata class."""

    def test_extract_from_string(self):
        """Test extracting author from string."""
        raw_data = {
            'author': 'John Doe'
        }
        metadata = AuthorMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('author', result)
        self.assertEqual(len(result['author']), 1)
        self.assertEqual(result['author'][0]['@type'], 'Person')
        self.assertEqual(result['author'][0]['name'], 'John Doe')
    
    def test_extract_from_dict(self):
        """Test extracting author from dictionary."""
        raw_data = {
            'author': {
                'name': 'John Doe',
                'email': 'john@example.com'
            }
        }
        metadata = AuthorMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('author', result)
        self.assertEqual(len(result['author']), 1)
        self.assertEqual(result['author'][0]['name'], 'John Doe')
        self.assertEqual(result['author'][0]['email'], 'john@example.com')
    
    def test_extract_from_array(self):
        """Test extracting multiple authors from array."""
        raw_data = {
            'authors': [
                {'name': 'John Doe', 'email': 'john@example.com'},
                {'name': 'Jane Smith', 'email': 'jane@example.com'}
            ]
        }
        metadata = AuthorMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('author', result)
        self.assertEqual(len(result['author']), 2)
        self.assertEqual(result['author'][0]['name'], 'John Doe')
        self.assertEqual(result['author'][1]['name'], 'Jane Smith')
    
    def test_extract_with_given_family_names(self):
        """Test extracting author with given and family names."""
        raw_data = {
            'author': {
                'givenName': 'John',
                'familyName': 'Doe',
                'email': 'john@example.com'
            }
        }
        metadata = AuthorMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('author', result)
        self.assertEqual(result['author'][0]['name'], 'John Doe')
        self.assertEqual(result['author'][0]['givenName'], 'John')
        self.assertEqual(result['author'][0]['familyName'], 'Doe')
    
    def test_extract_with_affiliation(self):
        """Test extracting author with affiliation."""
        raw_data = {
            'author': {
                'name': 'John Doe',
                'affiliation': 'University of Example'
            }
        }
        metadata = AuthorMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('author', result)
        self.assertIn('affiliation', result['author'][0])
        self.assertEqual(result['author'][0]['affiliation']['@type'], 'Organization')
        self.assertEqual(result['author'][0]['affiliation']['name'], 'University of Example')
    
    def test_extract_with_orcid(self):
        """Test extracting author with ORCID."""
        raw_data = {
            'author': {
                'name': 'John Doe',
                'orcid': '0000-0002-1825-0097'
            }
        }
        metadata = AuthorMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('author', result)
        self.assertIn('@id', result['author'][0])
        self.assertIn('orcid.org', result['author'][0]['@id'])
    
    def test_extract_from_owner(self):
        """Test extracting author from repository owner."""
        raw_data = {
            'owner': {
                'name': 'John Doe',
                'email': 'john@example.com'
            }
        }
        metadata = AuthorMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('author', result)
        self.assertEqual(result['author'][0]['name'], 'John Doe')
    
    def test_extract_from_contributors(self):
        """Test extracting authors from contributors list."""
        raw_data = {
            'contributors': [
                {'name': 'John Doe', 'email': 'john@example.com'},
                {'name': 'Jane Smith', 'email': 'jane@example.com'}
            ]
        }
        metadata = AuthorMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('author', result)
        self.assertGreaterEqual(len(result['author']), 1)
    
    def test_remove_duplicate_authors(self):
        """Test that duplicate authors are removed."""
        raw_data = {
            'authors': [
                {'name': 'John Doe', 'email': 'john@example.com'},
                {'name': 'john doe', 'email': 'john@example.com'},
                {'name': 'Jane Smith', 'email': 'jane@example.com'}
            ]
        }
        metadata = AuthorMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('author', result)
        # Should remove case-insensitive duplicate
        self.assertEqual(len(result['author']), 2)
    
    def test_split_name_into_given_family(self):
        """Test that full name is split into given and family names."""
        raw_data = {
            'author': 'John Doe'
        }
        metadata = AuthorMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('author', result)
        self.assertEqual(result['author'][0]['givenName'], 'John')
        self.assertEqual(result['author'][0]['familyName'], 'Doe')
    
    def test_validate_email_format(self):
        """Test email validation."""
        metadata = AuthorMetadata({})
        
        self.assertTrue(metadata._is_valid_email('john@example.com'))
        self.assertTrue(metadata._is_valid_email('john.doe@example.co.uk'))
        self.assertFalse(metadata._is_valid_email('invalid-email'))
        self.assertFalse(metadata._is_valid_email(''))
        self.assertFalse(metadata._is_valid_email(None))
    
    def test_validate_authors_array(self):
        """Test validation of authors array."""
        raw_data = {
            'author': [
                {'name': 'John Doe', 'email': 'john@example.com'}
            ]
        }
        metadata = AuthorMetadata(raw_data)
        metadata.extract()
        metadata.validate()
        
        self.assertEqual(len(metadata.errors), 0)
    
    def test_validate_author_missing_name(self):
        """Test validation fails when author is missing name."""
        metadata = AuthorMetadata({})
        metadata.metadata = {
            'author': [
                {'@type': 'Person', 'email': 'john@example.com'}
            ]
        }
        metadata.validate()
        
        self.assertGreater(len(metadata.errors), 0)
    
    def test_validate_invalid_email(self):
        """Test validation warns for invalid email."""
        metadata = AuthorMetadata({})
        metadata.metadata = {
            'author': [
                {'@type': 'Person', 'name': 'John Doe', 'email': 'invalid-email'}
            ]
        }
        metadata.validate()
        
        self.assertGreater(len(metadata.warnings), 0)
    
    def test_to_codemeta_dict(self):
        """Test conversion to Codemeta format."""
        raw_data = {
            'author': {
                'name': 'John Doe',
                'email': 'john@example.com',
                'affiliation': 'University of Example'
            }
        }
        metadata = AuthorMetadata(raw_data)
        metadata.extract()
        result = metadata.to_codemeta_dict()
        
        self.assertIn('author', result)
        self.assertEqual(result['author'][0]['@type'], 'Person')
        self.assertEqual(result['author'][0]['name'], 'John Doe')
        self.assertEqual(result['author'][0]['affiliation']['@type'], 'Organization')
    
    def test_to_codemeta_dict_empty(self):
        """Test conversion with no authors."""
        metadata = AuthorMetadata({})
        result = metadata.to_codemeta_dict()
        
        self.assertEqual(result, {})
    
    def test_extract_empty_authors(self):
        """Test extraction with no authors."""
        raw_data = {}
        metadata = AuthorMetadata(raw_data)
        result = metadata.extract()
        
        self.assertEqual(result, {})
        self.assertEqual(len(metadata.warnings), 1)


if __name__ == '__main__':
    unittest.main()
