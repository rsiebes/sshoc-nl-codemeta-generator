"""
Test suite for License property module.

Tests extraction, validation, and conversion of license metadata.
"""

import unittest
from src.properties.license import LicenseMetadata
from src.utils import normalize_license, get_spdx_license, get_spdx_license_url


class TestSPDXLicenseMapping(unittest.TestCase):
    """Test cases for SPDX license mapping utilities."""

    def test_get_spdx_license_mit(self):
        """Test getting SPDX identifier for MIT license."""
        result = get_spdx_license('MIT')
        self.assertEqual(result, 'MIT')

    def test_get_spdx_license_gpl3(self):
        """Test getting SPDX identifier for GPL v3."""
        result = get_spdx_license('GNU General Public License v3')
        self.assertEqual(result, 'GPL-3.0-only')

    def test_get_spdx_license_apache(self):
        """Test getting SPDX identifier for Apache 2.0."""
        result = get_spdx_license('Apache 2.0')
        self.assertEqual(result, 'Apache-2.0')

    def test_get_spdx_license_bsd(self):
        """Test getting SPDX identifier for BSD."""
        result = get_spdx_license('BSD')
        self.assertEqual(result, 'BSD-3-Clause')

    def test_get_spdx_license_case_insensitive(self):
        """Test case-insensitive license matching."""
        result = get_spdx_license('mit')
        self.assertEqual(result, 'MIT')

    def test_get_spdx_license_unknown(self):
        """Test unknown license returns None."""
        result = get_spdx_license('Unknown License')
        self.assertIsNone(result)

    def test_get_spdx_license_url_mit(self):
        """Test getting SPDX URL for MIT."""
        result = get_spdx_license_url('MIT')
        self.assertEqual(result, 'https://spdx.org/licenses/MIT')

    def test_get_spdx_license_url_gpl(self):
        """Test getting SPDX URL for GPL."""
        result = get_spdx_license_url('GPL-3.0-only')
        self.assertEqual(result, 'https://spdx.org/licenses/GPL-3.0-only')

    def test_normalize_license_string(self):
        """Test normalizing license string."""
        spdx_id, spdx_url = normalize_license('MIT License')
        self.assertEqual(spdx_id, 'MIT')
        self.assertEqual(spdx_url, 'https://spdx.org/licenses/MIT')

    def test_normalize_license_url(self):
        """Test normalizing license from SPDX URL."""
        spdx_id, spdx_url = normalize_license('https://spdx.org/licenses/MIT')
        self.assertEqual(spdx_id, 'MIT')
        self.assertEqual(spdx_url, 'https://spdx.org/licenses/MIT')

    def test_normalize_license_proprietary(self):
        """Test normalizing proprietary license."""
        spdx_id, spdx_url = normalize_license('Proprietary')
        self.assertEqual(spdx_id, 'Proprietary')
        self.assertIsNone(spdx_url)


class TestLicenseMetadata(unittest.TestCase):
    """Test cases for LicenseMetadata."""

    def test_extract_from_license_field(self):
        """Test extracting license from direct field."""
        raw_data = {'license': 'MIT'}
        metadata = LicenseMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('license', result)
        self.assertIsInstance(result['license'], dict)
        self.assertEqual(result['license']['name'], 'MIT')

    def test_extract_license_with_spdx_url(self):
        """Test extracting license with SPDX URL."""
        raw_data = {'license': 'MIT License'}
        metadata = LicenseMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('license', result)
        self.assertIn('@id', result['license'])
        self.assertEqual(result['license']['@id'], 'https://spdx.org/licenses/MIT')

    def test_extract_license_dict(self):
        """Test extracting license from dictionary."""
        raw_data = {'license': {'name': 'MIT', 'url': 'https://spdx.org/licenses/MIT'}}
        metadata = LicenseMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('license', result)
        self.assertEqual(result['license']['name'], 'MIT')
        self.assertEqual(result['license']['@id'], 'https://spdx.org/licenses/MIT')

    def test_extract_multiple_licenses(self):
        """Test extracting multiple licenses."""
        raw_data = {'license': ['MIT', 'Apache-2.0']}
        metadata = LicenseMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('license', result)
        self.assertIsInstance(result['license'], list)
        self.assertEqual(len(result['license']), 2)

    def test_extract_empty_license(self):
        """Test extraction with empty license."""
        raw_data = {}
        metadata = LicenseMetadata(raw_data)
        result = metadata.extract()
        
        self.assertEqual(result, {})
        self.assertTrue(len(metadata.get_warnings()) > 0)

    def test_validate_license_with_name(self):
        """Test validation of license with name."""
        raw_data = {'license': 'MIT'}
        metadata = LicenseMetadata(raw_data)
        metadata.extract()
        is_valid = metadata.validate()
        
        self.assertTrue(is_valid)

    def test_validate_license_with_id(self):
        """Test validation of license with @id."""
        raw_data = {'license': {'@id': 'https://spdx.org/licenses/MIT'}}
        metadata = LicenseMetadata(raw_data)
        metadata.extract()
        is_valid = metadata.validate()
        
        self.assertTrue(is_valid)

    def test_validate_license_missing_name_and_id(self):
        """Test validation of license missing both name and @id."""
        raw_data = {'license': {}}
        metadata = LicenseMetadata(raw_data)
        result = metadata.extract()
        
        # Empty dict is not processed, so no license is extracted
        self.assertEqual(result, {})
        self.assertTrue(len(metadata.get_warnings()) > 0)

    def test_validate_multiple_licenses(self):
        """Test validation of multiple licenses."""
        raw_data = {'license': ['MIT', 'Apache-2.0']}
        metadata = LicenseMetadata(raw_data)
        metadata.extract()
        is_valid = metadata.validate()
        
        self.assertTrue(is_valid)

    def test_to_codemeta_dict_single_license(self):
        """Test conversion to Codemeta format with single license."""
        raw_data = {'license': 'MIT'}
        metadata = LicenseMetadata(raw_data)
        metadata.extract()
        result = metadata.to_codemeta_dict()
        
        self.assertIn('license', result)
        self.assertIsInstance(result['license'], dict)

    def test_to_codemeta_dict_multiple_licenses(self):
        """Test conversion to Codemeta format with multiple licenses."""
        raw_data = {'license': ['MIT', 'Apache-2.0']}
        metadata = LicenseMetadata(raw_data)
        metadata.extract()
        result = metadata.to_codemeta_dict()
        
        self.assertIn('license', result)
        self.assertIsInstance(result['license'], list)

    def test_process_license_string_mit(self):
        """Test processing MIT license string."""
        raw_data = {'license': 'MIT'}
        metadata = LicenseMetadata(raw_data)
        result = metadata.extract()
        
        self.assertEqual(result['license']['name'], 'MIT')
        self.assertEqual(result['license']['@id'], 'https://spdx.org/licenses/MIT')

    def test_process_license_string_gpl(self):
        """Test processing GPL license string."""
        raw_data = {'license': 'GNU General Public License v3'}
        metadata = LicenseMetadata(raw_data)
        result = metadata.extract()
        
        self.assertEqual(result['license']['name'], 'GNU General Public License v3')
        self.assertEqual(result['license']['@id'], 'https://spdx.org/licenses/GPL-3.0-only')

    def test_process_license_unknown_string(self):
        """Test processing unknown license string."""
        raw_data = {'license': 'Custom License'}
        metadata = LicenseMetadata(raw_data)
        result = metadata.extract()
        
        self.assertEqual(result['license']['name'], 'Custom License')
        self.assertNotIn('@id', result['license'])

    def test_process_license_dict_with_name(self):
        """Test processing license dict with name."""
        raw_data = {'license': {'name': 'MIT'}}
        metadata = LicenseMetadata(raw_data)
        result = metadata.extract()
        
        self.assertEqual(result['license']['name'], 'MIT')
        self.assertEqual(result['license']['@id'], 'https://spdx.org/licenses/MIT')

    def test_process_license_dict_with_url(self):
        """Test processing license dict with URL."""
        raw_data = {'license': {'name': 'MIT', 'url': 'https://example.com/mit'}}
        metadata = LicenseMetadata(raw_data)
        result = metadata.extract()
        
        self.assertEqual(result['license']['name'], 'MIT')
        self.assertEqual(result['license']['@id'], 'https://example.com/mit')

    def test_extract_from_license_identifier(self):
        """Test extracting from license_identifier field."""
        raw_data = {'license_identifier': 'Apache-2.0'}
        metadata = LicenseMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('license', result)
        self.assertEqual(result['license']['name'], 'Apache-2.0')

    def test_extract_from_license_url(self):
        """Test extracting from license_url field."""
        raw_data = {'license_url': 'https://spdx.org/licenses/MIT'}
        metadata = LicenseMetadata(raw_data)
        result = metadata.extract()
        
        self.assertIn('license', result)
        self.assertEqual(result['license']['@id'], 'https://spdx.org/licenses/MIT')


if __name__ == '__main__':
    unittest.main()
