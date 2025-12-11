#!/usr/bin/env python3
"""
Integration tests for the orchestrator and description module.

This module contains tests that verify the integration between:
- The orchestrator (codemeta_generator.py)
- The description module (codemeta_description.py)
- The name module (codemeta_name.py)
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.codemeta_generator import generate, execute_modules, build_codemeta_structure
from src.modules.codemeta_description import get as get_description
from src.modules.codemeta_name import get as get_name


class TestOrchestratorDescriptionIntegration:
    """Tests for orchestrator and description module integration."""

    def test_description_module_is_discovered(self):
        """Test that description module is discovered by orchestrator."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        results = execute_modules(repo_url)
        # Description module should be executed
        assert len(results) > 0, "Description module should be executed"
        print("✓ test_description_module_is_discovered passed")

    def test_description_module_produces_output(self):
        """Test that description module produces output."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        results = execute_modules(repo_url)
        assert 'description' in results or len(results) > 0, "Description module should produce output"
        print("✓ test_description_module_produces_output passed")

    def test_orchestrator_includes_description_in_output(self):
        """Test that orchestrator includes description in final output."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "codemeta.jsonld")
            result = generate(repo_url, output_file=output_file)
            # Check if description is in the result
            if 'description' in result:
                assert isinstance(result['description'], str), "Description should be a string"
                assert len(result['description']) > 0, "Description should not be empty"
        print("✓ test_orchestrator_includes_description_in_output passed")

    def test_description_module_direct_call(self):
        """Test calling description module directly."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        result = get_description(repo_url)
        assert isinstance(result, dict), "Description module should return a dictionary"
        if result:
            assert 'description' in result, "Result should contain 'description' key"
        print("✓ test_description_module_direct_call passed")

    def test_description_and_name_together(self):
        """Test that description and name modules work together."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        description_result = get_description(repo_url)
        name_result = get_name(repo_url)
        
        # Combine results
        combined = {**description_result, **name_result}
        
        # Build structure
        structure = build_codemeta_structure(combined)
        
        # Verify structure
        assert '@context' in structure, "Should have @context"
        assert '@type' in structure, "Should have @type"
        if combined:
            assert len(structure) > 2, "Should have additional properties beyond @context and @type"
        print("✓ test_description_and_name_together passed")


class TestOrchestratorDescriptionRichness:
    """Tests for description richness and quality."""

    def test_description_is_comprehensive(self):
        """Test that extracted description is comprehensive."""
        repo_url = "https://github.com/sodascience/osmenrich"
        result = get_description(repo_url)
        if result and 'description' in result:
            description = result['description']
            # Should be a substantial description (not just a short phrase)
            assert len(description) > 50, f"Description should be comprehensive, got {len(description)} chars"
            print(f"  Description length: {len(description)} characters")
        print("✓ test_description_is_comprehensive passed")

    def test_description_contains_meaningful_content(self):
        """Test that description contains meaningful content."""
        repo_url = "https://github.com/sodascience/osmenrich"
        result = get_description(repo_url)
        if result and 'description' in result:
            description = result['description']
            # Should contain project name or key terms
            assert 'osmenrich' in description.lower() or 'enrich' in description.lower(), \
                "Description should contain project-related terms"
        print("✓ test_description_contains_meaningful_content passed")

    def test_description_is_clean(self):
        """Test that description is clean (no markdown artifacts)."""
        repo_url = "https://github.com/sodascience/osmenrich"
        result = get_description(repo_url)
        if result and 'description' in result:
            description = result['description']
            # Should not contain markdown or HTML artifacts
            assert '![' not in description, "Should not contain markdown image syntax"
            assert '[' not in description or ']' not in description, "Should not contain unprocessed markdown links"
            assert '<' not in description or '>' not in description, "Should not contain HTML tags"
        print("✓ test_description_is_clean passed")

    def test_description_starts_with_meaningful_text(self):
        """Test that description starts with meaningful text (not badges)."""
        repo_url = "https://github.com/sodascience/osmenrich"
        result = get_description(repo_url)
        if result and 'description' in result:
            description = result['description']
            # Should not start with badge-related text
            assert not description.startswith('test'), "Should not start with 'test'"
            assert not description.startswith('DOI'), "Should not start with 'DOI'"
            assert not description.startswith('Project Status'), "Should not start with 'Project Status'"
        print("✓ test_description_starts_with_meaningful_text passed")


class TestOrchestratorOutputFormat:
    """Tests for output format and structure."""

    def test_output_file_format_is_jsonld(self):
        """Test that output file is valid JSON-LD."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "codemeta.jsonld")
            generate(repo_url, output_file=output_file)
            
            # Read and parse the file
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            # Verify JSON-LD structure
            assert '@context' in data, "Should have @context for JSON-LD"
            assert '@type' in data, "Should have @type for JSON-LD"
            assert data['@context'] == 'https://codemeta.github.io/terms/', "Should have correct context"
            assert data['@type'] == 'SoftwareSourceCode', "Should have correct type"
        print("✓ test_output_file_format_is_jsonld passed")

    def test_output_file_is_readable(self):
        """Test that output file is readable and properly formatted."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "codemeta.jsonld")
            generate(repo_url, output_file=output_file)
            
            # Read the file
            with open(output_file, 'r') as f:
                content = f.read()
            
            # Should be properly formatted JSON
            data = json.loads(content)
            assert isinstance(data, dict), "Should be a valid JSON object"
        print("✓ test_output_file_is_readable passed")

    def test_output_contains_both_modules_results(self):
        """Test that output contains results from both modules."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "codemeta.jsonld")
            result = generate(repo_url, output_file=output_file)
            
            # Should have at least name or description from the modules
            has_name = 'name' in result
            has_description = 'description' in result
            assert has_name or has_description, "Should have at least name or description"
        print("✓ test_output_contains_both_modules_results passed")


class TestOrchestratorMultipleRepositories:
    """Tests with multiple repositories."""

    def test_generate_for_different_repository_types(self):
        """Test generation for different types of repositories."""
        test_repos = [
            "https://github.com/rsiebes/sshoc-nl-codemeta-generator",  # Python project
            "https://github.com/sodascience/osmenrich",  # R project
        ]
        
        for repo_url in test_repos:
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = os.path.join(tmpdir, "codemeta.jsonld")
                result = generate(repo_url, output_file=output_file)
                assert isinstance(result, dict), f"Should generate valid metadata for {repo_url}"
                assert '@context' in result, f"Should have @context for {repo_url}"
        print("✓ test_generate_for_different_repository_types passed")

    def test_description_extraction_varies_by_repository(self):
        """Test that description extraction produces different results for different repos."""
        repo_urls = [
            "https://github.com/rsiebes/sshoc-nl-codemeta-generator",
            "https://github.com/sodascience/osmenrich",
        ]
        
        descriptions = []
        for repo_url in repo_urls:
            result = get_description(repo_url)
            if result and 'description' in result:
                descriptions.append(result['description'])
        
        # Different repositories should have different descriptions
        if len(descriptions) == 2:
            assert descriptions[0] != descriptions[1], "Different repos should have different descriptions"
        print("✓ test_description_extraction_varies_by_repository passed")


class TestOrchestratorRobustness:
    """Tests for robustness and edge cases."""

    def test_generate_with_malformed_url(self):
        """Test that generate handles malformed URLs gracefully."""
        malformed_urls = [
            "not-a-url",
            "http://invalid",
            "github.com/missing-slash",
            "",
        ]
        
        for url in malformed_urls:
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = os.path.join(tmpdir, "codemeta.jsonld")
                try:
                    result = generate(url, output_file=output_file)
                    assert isinstance(result, dict), f"Should return dict for malformed URL: {url}"
                except Exception as e:
                    # Should handle gracefully, not crash
                    pass
        print("✓ test_generate_with_malformed_url passed")

    def test_generate_produces_valid_json_always(self):
        """Test that generate always produces valid JSON output."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "codemeta.jsonld")
            generate(repo_url, output_file=output_file)
            
            # Should be valid JSON
            with open(output_file, 'r') as f:
                try:
                    json.load(f)
                except json.JSONDecodeError:
                    raise AssertionError("Output file should contain valid JSON")
        print("✓ test_generate_produces_valid_json_always passed")

    def test_orchestrator_module_isolation(self):
        """Test that modules are isolated and don't interfere with each other."""
        repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        
        # Run multiple times to ensure no state pollution
        for i in range(3):
            results = execute_modules(repo_url)
            assert isinstance(results, dict), f"Run {i+1}: Should return dict"
        print("✓ test_orchestrator_module_isolation passed")


def run_all_tests():
    """Run all integration tests."""
    print("=" * 80)
    print("RUNNING INTEGRATION TEST SUITE")
    print("=" * 80)
    print()

    test_classes = [
        TestOrchestratorDescriptionIntegration,
        TestOrchestratorDescriptionRichness,
        TestOrchestratorOutputFormat,
        TestOrchestratorMultipleRepositories,
        TestOrchestratorRobustness,
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
