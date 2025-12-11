#!/usr/bin/env python3
"""
Enhanced test suite for the codemeta_generator orchestrator.

This module contains comprehensive tests for the orchestrator's:
- Module discovery mechanism
- Module execution and error handling
- Aggregation logic
- Validation
- File output
"""

import sys
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.codemeta_generator import generate, CodeMetaGenerator
from src.schema_validator import validate_metadata


class TestOrchestratorDiscovery:
    """Tests for module discovery functionality."""

    def test_discover_modules_finds_existing_modules(self):
        """Test that module discovery finds existing modules."""
        modules = discover_modules()
        assert len(modules) > 0, "Should find at least one module"
        assert any('codemeta_name' in str(m) for m in modules), "Should find codemeta_name module"
        assert any('codemeta_description' in str(m) for m in modules), "Should find codemeta_description module"
        print("✓ test_discover_modules_finds_existing_modules passed")

    def test_discover_modules_returns_list(self):
        """Test that module discovery returns a list."""
        modules = discover_modules()
        assert isinstance(modules, list), "Module discovery should return a list"
        print("✓ test_discover_modules_returns_list passed")

    def test_discover_modules_modules_are_strings(self):
        """Test that discovered modules are strings."""
        modules = discover_modules()
        for module in modules:
            assert isinstance(module, str), f"Module should be a string, got {type(module)}"
        print("✓ test_discover_modules_modules_are_strings passed")


class TestOrchestratorExecution:
    """Tests for module execution functionality."""

    def test_execute_modules_returns_dict(self):
        """Test that module execution returns a dictionary."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        results = execute_modules(repo_url)
        assert isinstance(results, dict), "Module execution should return a dictionary"
        print("✓ test_execute_modules_returns_dict passed")

    def test_execute_modules_with_valid_repo(self):
        """Test module execution with a valid repository."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        results = execute_modules(repo_url)
        assert len(results) > 0, "Should have results from module execution"
        print("✓ test_execute_modules_with_valid_repo passed")

    def test_execute_modules_handles_invalid_url(self):
        """Test that module execution handles invalid URLs gracefully."""
        repo_url = "invalid-url"
        results = execute_modules(repo_url)
        assert isinstance(results, dict), "Should still return a dictionary"
        print("✓ test_execute_modules_handles_invalid_url passed")

    def test_execute_modules_contains_expected_keys(self):
        """Test that executed modules produce expected keys."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        results = execute_modules(repo_url)
        # Check for keys that should be present from implemented modules
        assert 'name' in results or 'description' in results, "Should have at least name or description"
        print("✓ test_execute_modules_contains_expected_keys passed")


class TestOrchestratorAggregation:
    """Tests for metadata aggregation functionality."""

    def test_build_codemeta_structure_returns_dict(self):
        """Test that aggregation returns a dictionary."""
        module_results = {
            'name': 'Test Project',
            'description': 'A test project'
        }
        structure = build_codemeta_structure(module_results)
        assert isinstance(structure, dict), "Should return a dictionary"
        print("✓ test_build_codemeta_structure_returns_dict passed")

    def test_build_codemeta_structure_includes_context(self):
        """Test that the structure includes the @context."""
        module_results = {'name': 'Test Project'}
        structure = build_codemeta_structure(module_results)
        assert '@context' in structure, "Should include @context"
        assert structure['@context'] == 'https://codemeta.github.io/terms/', "Should have correct context URL"
        print("✓ test_build_codemeta_structure_includes_context passed")

    def test_build_codemeta_structure_includes_type(self):
        """Test that the structure includes the @type."""
        module_results = {'name': 'Test Project'}
        structure = build_codemeta_structure(module_results)
        assert '@type' in structure, "Should include @type"
        assert structure['@type'] == 'SoftwareSourceCode', "Should have correct type"
        print("✓ test_build_codemeta_structure_includes_type passed")

    def test_build_codemeta_structure_includes_module_results(self):
        """Test that the structure includes module results."""
        module_results = {
            'name': 'Test Project',
            'description': 'A test project'
        }
        structure = build_codemeta_structure(module_results)
        assert structure['name'] == 'Test Project', "Should include name"
        assert structure['description'] == 'A test project', "Should include description"
        print("✓ test_build_codemeta_structure_includes_module_results passed")

    def test_build_codemeta_structure_with_empty_results(self):
        """Test aggregation with empty module results."""
        module_results = {}
        structure = build_codemeta_structure(module_results)
        assert '@context' in structure, "Should still include @context"
        assert '@type' in structure, "Should still include @type"
        print("✓ test_build_codemeta_structure_with_empty_results passed")


class TestOrchestratorValidation:
    """Tests for metadata validation functionality."""

    def test_validate_metadata_with_valid_structure(self):
        """Test validation with a valid CodeMeta structure."""
        metadata = {
            '@context': 'https://codemeta.github.io/terms/',
            '@type': 'SoftwareSourceCode',
            'name': 'Test Project'
        }
        is_valid = validate_metadata(metadata)
        assert is_valid, "Valid metadata should pass validation"
        print("✓ test_validate_metadata_with_valid_structure passed")

    def test_validate_metadata_with_multiple_properties(self):
        """Test validation with multiple properties."""
        metadata = {
            '@context': 'https://codemeta.github.io/terms/',
            '@type': 'SoftwareSourceCode',
            'name': 'Test Project',
            'description': 'A test project'
        }
        is_valid = validate_metadata(metadata)
        assert is_valid, "Valid metadata with multiple properties should pass validation"
        print("✓ test_validate_metadata_with_multiple_properties passed")

    def test_validate_metadata_returns_boolean(self):
        """Test that validation returns a boolean."""
        metadata = {
            '@context': 'https://codemeta.github.io/terms/',
            '@type': 'SoftwareSourceCode',
            'name': 'Test Project'
        }
        result = validate_metadata(metadata)
        assert isinstance(result, bool), "Validation should return a boolean"
        print("✓ test_validate_metadata_returns_boolean passed")


class TestOrchestratorGeneration:
    """Tests for the complete generation process."""

    def test_generate_returns_dict(self):
        """Test that generate returns a dictionary."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "codemeta.jsonld")
            result = generate(repo_url, output_file=output_file)
            assert isinstance(result, dict), "Generate should return a dictionary"
        print("✓ test_generate_returns_dict passed")

    def test_generate_creates_output_file(self):
        """Test that generate creates an output file."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "codemeta.jsonld")
            generate(repo_url, output_file=output_file)
            assert os.path.exists(output_file), "Output file should be created"
        print("✓ test_generate_creates_output_file passed")

    def test_generate_output_file_is_valid_json(self):
        """Test that the output file contains valid JSON."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "codemeta.jsonld")
            generate(repo_url, output_file=output_file)
            with open(output_file, 'r') as f:
                data = json.load(f)
            assert isinstance(data, dict), "Output file should contain valid JSON"
        print("✓ test_generate_output_file_is_valid_json passed")

    def test_generate_output_has_required_fields(self):
        """Test that the generated output has required fields."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "codemeta.jsonld")
            result = generate(repo_url, output_file=output_file)
            assert '@context' in result, "Should have @context"
            assert '@type' in result, "Should have @type"
        print("✓ test_generate_output_has_required_fields passed")

    def test_generate_with_different_repository(self):
        """Test generation with a different repository."""
        repo_url = "https://github.com/sodascience/osmenrich"
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "codemeta.jsonld")
            result = generate(repo_url, output_file=output_file)
            assert isinstance(result, dict), "Should generate valid metadata"
            assert 'name' in result or 'description' in result, "Should have extracted properties"
        print("✓ test_generate_with_different_repository passed")

    def test_generate_with_invalid_url(self):
        """Test generation with an invalid URL."""
        repo_url = "invalid-url"
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "codemeta.jsonld")
            result = generate(repo_url, output_file=output_file)
            assert isinstance(result, dict), "Should still return a dictionary"
        print("✓ test_generate_with_invalid_url passed")


class TestOrchestratorErrorHandling:
    """Tests for error handling in the orchestrator."""

    def test_generate_handles_missing_output_file_parameter(self):
        """Test that generate works without specifying output file."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        result = generate(repo_url)
        assert isinstance(result, dict), "Should return a dictionary even without output file"
        print("✓ test_generate_handles_missing_output_file_parameter passed")

    def test_generate_handles_none_output_file(self):
        """Test that generate handles None as output file."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        result = generate(repo_url, output_file=None)
        assert isinstance(result, dict), "Should return a dictionary with None output file"
        print("✓ test_generate_handles_none_output_file passed")

    def test_execute_modules_continues_on_module_error(self):
        """Test that orchestrator continues even if a module fails."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        results = execute_modules(repo_url)
        # Should still get results even if one module fails
        assert isinstance(results, dict), "Should return results despite potential module errors"
        print("✓ test_execute_modules_continues_on_module_error passed")


def run_all_tests():
    """Run all orchestrator tests."""
    print("=" * 80)
    print("RUNNING ORCHESTRATOR TEST SUITE")
    print("=" * 80)
    print()

    test_classes = [
        TestOrchestratorDiscovery,
        TestOrchestratorExecution,
        TestOrchestratorAggregation,
        TestOrchestratorValidation,
        TestOrchestratorGeneration,
        TestOrchestratorErrorHandling,
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
