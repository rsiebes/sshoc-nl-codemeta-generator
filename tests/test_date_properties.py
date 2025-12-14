"""
Tests for dateCreated and dateModified property modules.
"""

import unittest
from datetime import datetime
from src.properties.date_created import DateCreatedMetadata
from src.properties.date_modified import DateModifiedMetadata


class TestDateCreatedMetadata(unittest.TestCase):
    """Test DateCreatedMetadata class."""
    
    def test_extract_from_date_created_field(self):
        """Test extraction from date_created field."""
        raw_data = {'date_created': '2016-01-04T19:52:55.000Z'}
        metadata = DateCreatedMetadata(raw_data)
        result = metadata.extract()
        self.assertIn('dateCreated', result)
        self.assertTrue(result['dateCreated'].startswith('2016-01-04'))
    
    def test_extract_from_created_at_field(self):
        """Test extraction from created_at field."""
        raw_data = {'created_at': '2020-05-15T10:30:00Z'}
        metadata = DateCreatedMetadata(raw_data)
        result = metadata.extract()
        self.assertIn('dateCreated', result)
        self.assertTrue(result['dateCreated'].startswith('2020-05-15'))
    
    def test_extract_iso_format(self):
        """Test extraction of ISO 8601 format."""
        raw_data = {'date_created': '2021-03-20T14:25:30.123456Z'}
        metadata = DateCreatedMetadata(raw_data)
        result = metadata.extract()
        self.assertIn('dateCreated', result)
        self.assertTrue(result['dateCreated'].startswith('2021-03-20'))
    
    def test_extract_date_only(self):
        """Test extraction of date-only format."""
        raw_data = {'date_created': '2019-12-25'}
        metadata = DateCreatedMetadata(raw_data)
        result = metadata.extract()
        self.assertIn('dateCreated', result)
        self.assertTrue(result['dateCreated'].startswith('2019-12-25'))
    
    def test_extract_no_date(self):
        """Test extraction when no date is available."""
        raw_data = {}
        metadata = DateCreatedMetadata(raw_data)
        result = metadata.extract()
        self.assertEqual(result, {})
        self.assertTrue(len(metadata.warnings) > 0)
    
    def test_validation_valid_date(self):
        """Test validation of valid date."""
        raw_data = {'date_created': '2020-01-01T00:00:00Z'}
        metadata = DateCreatedMetadata(raw_data)
        metadata.extract()
        metadata.validate()
        self.assertEqual(len(metadata.errors), 0)
    
    def test_validation_future_date(self):
        """Test validation warns for future dates."""
        future_date = '2099-12-31T00:00:00Z'
        raw_data = {'date_created': future_date}
        metadata = DateCreatedMetadata(raw_data)
        metadata.extract()
        metadata.validate()
        self.assertTrue(len(metadata.warnings) > 0)
    
    def test_to_codemeta_dict(self):
        """Test conversion to Codemeta format."""
        raw_data = {'date_created': '2018-06-15T12:00:00Z'}
        metadata = DateCreatedMetadata(raw_data)
        metadata.extract()
        result = metadata.to_codemeta_dict()
        self.assertIn('dateCreated', result)
        self.assertTrue(result['dateCreated'].startswith('2018-06-15'))


class TestDateModifiedMetadata(unittest.TestCase):
    """Test DateModifiedMetadata class."""
    
    def test_extract_from_date_modified_field(self):
        """Test extraction from date_modified field."""
        raw_data = {'date_modified': '2023-11-20T15:45:30.000Z'}
        metadata = DateModifiedMetadata(raw_data)
        result = metadata.extract()
        self.assertIn('dateModified', result)
        self.assertTrue(result['dateModified'].startswith('2023-11-20'))
    
    def test_extract_from_updated_at_field(self):
        """Test extraction from updated_at field."""
        raw_data = {'updated_at': '2022-08-10T09:15:00Z'}
        metadata = DateModifiedMetadata(raw_data)
        result = metadata.extract()
        self.assertIn('dateModified', result)
        self.assertTrue(result['dateModified'].startswith('2022-08-10'))
    
    def test_extract_iso_format(self):
        """Test extraction of ISO 8601 format."""
        raw_data = {'date_modified': '2021-07-04T18:30:45.987654Z'}
        metadata = DateModifiedMetadata(raw_data)
        result = metadata.extract()
        self.assertIn('dateModified', result)
        self.assertTrue(result['dateModified'].startswith('2021-07-04'))
    
    def test_extract_no_date(self):
        """Test extraction when no date is available."""
        raw_data = {}
        metadata = DateModifiedMetadata(raw_data)
        result = metadata.extract()
        self.assertEqual(result, {})
        self.assertTrue(len(metadata.warnings) > 0)
    
    def test_validation_valid_date(self):
        """Test validation of valid date."""
        raw_data = {'date_modified': '2023-05-20T14:30:00Z'}
        metadata = DateModifiedMetadata(raw_data)
        metadata.extract()
        metadata.validate()
        self.assertEqual(len(metadata.errors), 0)
    
    def test_validation_future_date(self):
        """Test validation warns for future dates."""
        future_date = '2099-12-31T00:00:00Z'
        raw_data = {'date_modified': future_date}
        metadata = DateModifiedMetadata(raw_data)
        metadata.extract()
        metadata.validate()
        self.assertTrue(len(metadata.warnings) > 0)
    
    def test_to_codemeta_dict(self):
        """Test conversion to Codemeta format."""
        raw_data = {'date_modified': '2023-09-12T10:20:30Z'}
        metadata = DateModifiedMetadata(raw_data)
        metadata.extract()
        result = metadata.to_codemeta_dict()
        self.assertIn('dateModified', result)
        self.assertTrue(result['dateModified'].startswith('2023-09-12'))


if __name__ == '__main__':
    unittest.main()
