#!/usr/bin/env python3
"""
End-to-end tests using real GitHub repositories.

This module contains tests that verify the complete workflow with actual repositories:
- Fetching repository metadata from GitHub
- Extracting descriptions from README files
- Generating complete CodeMeta files
- Validating output against the CodeMeta 3.1 schema
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.codemeta_generator import generate
from src.schema_validator import validate_metadata


class TestE2EWithRealRepositories:
    """End-to-end tests with real GitHub repositories."""

    def test_e2e_codemeta_generator_repository(self):
        """Test complete workflow with codemeta-generator repository."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "codemeta.jsonld")
            result = generate(repo_url, output_file=output_file)
            
            # Verify result structure
            assert isinstance(result, dict), "Should return a dictionary"
            assert '@context' in result, "Should have @context"
            assert '@type' in result, "Should have @type"
            assert result['@type'] == 'SoftwareSourceCode', "Should have correct type"
            
            # Verify output file
            assert os.path.exists(output_file), "Output file should be created"
            with open(output_file, 'r') as f:
                file_data = json.load(f)
            assert file_data == result, "File content should match returned data"
            
            # Verify validation
            is_valid = validate_metadata(result)
            assert is_valid, "Generated metadata should be valid"
        
        print("✓ test_e2e_codemeta_generator_repository passed")

    def test_e2e_osmenrich_repository(self):
        """Test complete workflow with osmenrich repository."""
        repo_url = "https://github.com/sodascience/osmenrich"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "codemeta.jsonld")
            result = generate(repo_url, output_file=output_file)
            
            # Verify result structure
            assert isinstance(result, dict), "Should return a dictionary"
            assert '@context' in result, "Should have @context"
            assert '@type' in result, "Should have @type"
            
            # Verify name extraction (from README title)
            if 'name' in result:
                assert 'osmenrich' in result['name'].lower(), "Name should contain 'osmenrich'"
            
            # Verify description extraction (from README introduction)
            if 'description' in result:
                description = result['description']
                assert len(description) > 50, "Description should be comprehensive"
                assert 'enrich' in description.lower(), "Description should mention enriching"
                assert 'geocoded' in description.lower(), "Description should mention geocoded data"
            
            # Verify validation
            is_valid = validate_metadata(result)
            assert is_valid, "Generated metadata should be valid"
        
        print("✓ test_e2e_osmenrich_repository passed")

    def test_e2e_generates_valid_codemeta_jsonld(self):
        """Test that generated files are valid CodeMeta JSON-LD."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "codemeta.jsonld")
            result = generate(repo_url, output_file=output_file)
            
            # Verify JSON-LD structure
            assert result['@context'] == 'https://codemeta.github.io/terms/', "Should have correct context"
            assert result['@type'] == 'SoftwareSourceCode', "Should have correct type"
            
            # Verify file is valid JSON
            with open(output_file, 'r') as f:
                file_data = json.load(f)
            assert isinstance(file_data, dict), "File should contain a JSON object"
            
            # Verify file is valid JSON-LD
            assert file_data['@context'] == 'https://codemeta.github.io/terms/', "File should have correct context"
            assert file_data['@type'] == 'SoftwareSourceCode', "File should have correct type"
        
        print("✓ test_e2e_generates_valid_codemeta_jsonld passed")

    def test_e2e_extracts_name_correctly(self):
        """Test that name extraction works correctly."""
        test_cases = [
            ("https://github.com/rsiebes/sshoc-nl-codemeta-generator", "codemeta"),
            ("https://github.com/sodascience/osmenrich", "osmenrich"),
        ]
        
        for repo_url, expected_name_part in test_cases:
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = os.path.join(tmpdir, "codemeta.jsonld")
                result = generate(repo_url, output_file=output_file)
                
                if 'name' in result:
                    assert expected_name_part.lower() in result['name'].lower(), \
                        f"Name should contain '{expected_name_part}' for {repo_url}"
        
        print("✓ test_e2e_extracts_name_correctly passed")

    def test_e2e_extracts_description_correctly(self):
        """Test that description extraction works correctly."""
        repo_url = "https://github.com/sodascience/osmenrich"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "codemeta.jsonld")
            result = generate(repo_url, output_file=output_file)
            
            if 'description' in result:
                description = result['description']
                # Should be a meaningful description
                assert len(description) > 50, "Description should be comprehensive"
                # Should not contain markdown artifacts
                assert '![' not in description, "Should not contain markdown image syntax"
                assert '[' not in description or ']' not in description, "Should not contain unprocessed links"
                # Should contain relevant terms
                assert any(term in description.lower() for term in ['osmenrich', 'enrich', 'geocoded', 'openstreetmap']), \
                    "Description should contain relevant terms"
        
        print("✓ test_e2e_extracts_description_correctly passed")

    def test_e2e_handles_different_readme_formats(self):
        """Test that the system handles different README formats."""
        # Test with repositories that have different README structures
        test_repos = [
            "https://github.com/rsiebes/sshoc-nl-codemeta-generator",  # Python project
            "https://github.com/sodascience/osmenrich",  # R project
        ]
        
        for repo_url in test_repos:
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = os.path.join(tmpdir, "codemeta.jsonld")
                result = generate(repo_url, output_file=output_file)
                
                # Should successfully generate metadata
                assert isinstance(result, dict), f"Should generate metadata for {repo_url}"
                assert '@context' in result, f"Should have @context for {repo_url}"
                assert '@type' in result, f"Should have @type for {repo_url}"
        
        print("✓ test_e2e_handles_different_readme_formats passed")


class TestE2EDataQuality:
    """Tests for data quality in end-to-end scenarios."""

    def test_e2e_description_quality_osmenrich(self):
        """Test description quality for osmenrich repository."""
        repo_url = "https://github.com/sodascience/osmenrich"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "codemeta.jsonld")
            result = generate(repo_url, output_file=output_file)
            
            if 'description' in result:
                description = result['description']
                
                # Should mention the project goal
                assert 'goal' in description.lower() or 'enrich' in description.lower(), \
                    "Should mention the project's goal"
                
                # Should mention key technologies
                assert 'openstreetmap' in description.lower() or 'osm' in description.lower(), \
                    "Should mention OpenStreetMap"
                
                # Should be a complete sentence or multiple sentences
                assert description.count('.') > 0, "Should contain complete sentences"
        
        print("✓ test_e2e_description_quality_osmenrich passed")

    def test_e2e_output_consistency(self):
        """Test that multiple runs produce consistent output."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        
        results = []
        for i in range(2):
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = os.path.join(tmpdir, "codemeta.jsonld")
                result = generate(repo_url, output_file=output_file)
                results.append(result)
        
        # Results should be identical
        assert results[0] == results[1], "Multiple runs should produce identical output"
        
        print("✓ test_e2e_output_consistency passed")

    def test_e2e_no_sensitive_data_in_output(self):
        """Test that output doesn't contain sensitive data."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "codemeta.jsonld")
            result = generate(repo_url, output_file=output_file)
            
            # Convert to JSON string to check all values
            result_str = json.dumps(result)
            
            # Should not contain API keys or tokens
            assert 'token' not in result_str.lower(), "Should not contain tokens"
            assert 'api_key' not in result_str.lower(), "Should not contain API keys"
        
        print("✓ test_e2e_no_sensitive_data_in_output passed")


class TestE2EPerformance:
    """Tests for performance characteristics."""

    def test_e2e_generation_completes_in_reasonable_time(self):
        """Test that generation completes in reasonable time."""
        import time
        
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "codemeta.jsonld")
            
            start_time = time.time()
            result = generate(repo_url, output_file=output_file)
            elapsed_time = time.time() - start_time
            
            # Should complete in less than 30 seconds
            assert elapsed_time < 30, f"Generation took {elapsed_time:.2f}s, should be < 30s"
        
        print(f"✓ test_e2e_generation_completes_in_reasonable_time passed (took {elapsed_time:.2f}s)")

    def test_e2e_output_file_size_reasonable(self):
        """Test that output file size is reasonable."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "codemeta.jsonld")
            generate(repo_url, output_file=output_file)
            
            file_size = os.path.getsize(output_file)
            
            # Should be a reasonable size (less than 100KB for current implementation)
            assert file_size < 100000, f"Output file is {file_size} bytes, should be < 100KB"
        
        print(f"✓ test_e2e_output_file_size_reasonable passed (size: {file_size} bytes)")


def run_all_tests():
    """Run all end-to-end tests."""
    print("=" * 80)
    print("RUNNING END-TO-END TEST SUITE")
    print("=" * 80)
    print()

    test_classes = [
        TestE2EWithRealRepositories,
        TestE2EDataQuality,
        TestE2EPerformance,
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    for test_class in test_classes:
        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]

        for test_method in test_methods:
            total_tests += 1
            try:
                getattr(test_instance, test_method)()
                passed_tests += 1
            except AssertionError as e:
                failed_tests += 1
                print(f"✗ {test_method} failed: {str(e)}")
            except Exception as e:
                failed_tests += 1
                print(f"✗ {test_method} failed with exception: {str(e)}")

    print()
    print("=" * 80)
    print(f"RESULTS: {passed_tests} passed, {failed_tests} failed out of {total_tests} tests")
    print("=" * 80)

    return failed_tests == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
