"""
Tests for the contributor property module.
"""

import unittest
from src.properties.contributor import ContributorMetadata


class TestContributorMetadata(unittest.TestCase):
    """Test cases for ContributorMetadata class."""
    
    def test_extract_from_contributor_string(self):
        """Test extracting contributor from string."""
        raw_data = {
            'contributor': 'John Doe'
        }
        metadata = ContributorMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('contributor', result)
        self.assertEqual(len(result['contributor']), 1)
        self.assertEqual(result['contributor'][0]['name'], 'John Doe')
        self.assertEqual(result['contributor'][0]['@type'], 'Person')
    
    def test_extract_from_contributors_list(self):
        """Test extracting from contributors list."""
        raw_data = {
            'contributors': ['Alice Smith', 'Bob Johnson']
        }
        metadata = ContributorMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('contributor', result)
        self.assertEqual(len(result['contributor']), 2)
        self.assertEqual(result['contributor'][0]['name'], 'Alice Smith')
        self.assertEqual(result['contributor'][1]['name'], 'Bob Johnson')
    
    def test_extract_from_contributor_dict(self):
        """Test extracting from contributor dictionary."""
        raw_data = {
            'contributor': {
                'name': 'Jane Doe',
                'email': 'jane@example.com'
            }
        }
        metadata = ContributorMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('contributor', result)
        self.assertEqual(len(result['contributor']), 1)
        self.assertEqual(result['contributor'][0]['name'], 'Jane Doe')
        self.assertEqual(result['contributor'][0]['email'], 'jane@example.com')
    
    def test_extract_with_orcid(self):
        """Test extracting contributor with ORCID."""
        raw_data = {
            'contributor': {
                'name': 'Dr. Smith',
                'orcid': '0000-0002-1825-0097'
            }
        }
        metadata = ContributorMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('contributor', result)
        self.assertEqual(result['contributor'][0]['@id'], 'https://orcid.org/0000-0002-1825-0097')
    
    def test_extract_with_affiliation(self):
        """Test extracting contributor with affiliation."""
        raw_data = {
            'contributor': {
                'name': 'Prof. Johnson',
                'affiliation': 'MIT'
            }
        }
        metadata = ContributorMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('contributor', result)
        self.assertIn('affiliation', result['contributor'][0])
        self.assertEqual(result['contributor'][0]['affiliation']['@type'], 'Organization')
        self.assertEqual(result['contributor'][0]['affiliation']['name'], 'MIT')
    
    def test_name_splitting(self):
        """Test automatic name splitting into given and family names."""
        raw_data = {
            'contributor': 'John Michael Doe'
        }
        metadata = ContributorMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('contributor', result)
        self.assertEqual(result['contributor'][0]['givenName'], 'John')
        self.assertEqual(result['contributor'][0]['familyName'], 'Michael Doe')
    
    def test_remove_duplicates(self):
        """Test duplicate removal."""
        raw_data = {
            'contributors': ['John Doe', 'jane smith', 'John Doe', 'Jane Smith']
        }
        metadata = ContributorMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('contributor', result)
        self.assertEqual(len(result['contributor']), 2)  # Only unique names
    
    def test_no_contributors(self):
        """Test when no contributors are available."""
        raw_data = {}
        metadata = ContributorMetadata(raw_data)
        result = metadata.extract()
        
        self.assertNotIn('contributor', result)
    
    def test_validate_contributors_array(self):
        """Test validation of contributors array."""
        raw_data = {
            'contributor': 'John Doe'
        }
        metadata = ContributorMetadata(raw_data)
        metadata.extract()
        metadata.validate()
        
        self.assertEqual(len(metadata.errors), 0)
    
    def test_validate_contributor_person_type(self):
        """Test validation of Person type."""
        raw_data = {
            'contributor': 'John Doe'
        }
        metadata = ContributorMetadata(raw_data)
        metadata.extract()
        metadata.validate()
        
        self.assertEqual(len(metadata.errors), 0)
        # Should have @type='Person'
        self.assertEqual(metadata.metadata['contributor'][0]['@type'], 'Person')
    
    def test_validate_contributor_has_name(self):
        """Test validation requires name."""
        raw_data = {}
        metadata = ContributorMetadata(raw_data)
        metadata.metadata = {
            'contributor': [
                {'@type': 'Person'}  # Missing name
            ]
        }
        metadata.validate()
        
        self.assertGreater(len(metadata.errors), 0)
        self.assertIn("must have a 'name'", metadata.errors[0])
    
    def test_validate_invalid_email(self):
        """Test validation warns for invalid email."""
        raw_data = {}
        metadata = ContributorMetadata(raw_data)
        metadata.metadata = {
            'contributor': [
                {
                    '@type': 'Person',
                    'name': 'John Doe',
                    'email': 'invalid-email'
                }
            ]
        }
        metadata.validate()
        
        self.assertGreater(len(metadata.warnings), 0)
        self.assertIn("invalid email", metadata.warnings[0])
    
    def test_to_codemeta_dict(self):
        """Test conversion to Codemeta format."""
        raw_data = {
            'contributor': 'John Doe'
        }
        metadata = ContributorMetadata(raw_data)
        metadata.extract()
        codemeta = metadata.to_codemeta_dict()
        
        self.assertIn('contributor', codemeta)
        self.assertEqual(len(codemeta['contributor']), 1)
        self.assertEqual(codemeta['contributor'][0]['name'], 'John Doe')
    
    def test_to_codemeta_dict_empty(self):
        """Test conversion with no contributors."""
        raw_data = {}
        metadata = ContributorMetadata(raw_data)
        metadata.extract()
        codemeta = metadata.to_codemeta_dict()
        
        self.assertEqual(codemeta, {})
    
    def test_extract_from_commit_authors(self):
        """Test extracting from commit_authors field."""
        raw_data = {
            'commit_authors': [
                {'name': 'Alice Developer', 'email': 'alice@example.com'},
                {'name': 'Bob Coder', 'username': 'bobcoder'}
            ]
        }
        metadata = ContributorMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('contributor', result)
        self.assertEqual(len(result['contributor']), 2)
        self.assertEqual(result['contributor'][0]['name'], 'Alice Developer')
        self.assertEqual(result['contributor'][1]['name'], 'Bob Coder')


if __name__ == '__main__':
    unittest.main()
