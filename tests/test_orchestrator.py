#!/usr/bin/env python3
"""
Tests for the CodeMeta orchestrator.
"""

import sys
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.codemeta_generator import CodeMetaGenerator
from src.schema_validator import validate_metadata
from src.utils import filter_empty_values, is_url, is_email, is_date

def test_module_discovery():
    """Test that modules are discovered correctly."""
    generator = CodeMetaGenerator(verbose=False)
    modules = generator.discover_modules()
    assert len(modules) > 0, "No modules discovered"
    print(f"✓ Module discovery test passed: {len(modules)} modules found")

def test_module_execution():
    """Test that modules are executed correctly."""
    generator = CodeMetaGenerator(verbose=False)
    generator.discovered_modules = generator.discover_modules()
    
    repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
    aggregated_data = generator.execute_modules(repo_url)
    
    assert isinstance(aggregated_data, dict), "Aggregated data should be a dictionary"
    print(f"✓ Module execution test passed: {len(aggregated_data)} properties aggregated")

def test_codemeta_building():
    """Test that CodeMeta structure is built correctly."""
    generator = CodeMetaGenerator(verbose=False)
    generator.discovered_modules = generator.discover_modules()
    
    repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
    aggregated_data = generator.execute_modules(repo_url)
    codemeta_data = generator.build_codemeta(aggregated_data)
    
    assert "@context" in codemeta_data, "Missing @context"
    assert "@type" in codemeta_data, "Missing @type"
    assert codemeta_data["@context"] == "https://codemeta.github.io/terms/", "Invalid @context"
    assert codemeta_data["@type"] == "SoftwareSourceCode", "Invalid @type"
    print(f"✓ CodeMeta building test passed: {len(codemeta_data)} properties in final structure")

def test_validation():
    """Test that metadata validation works correctly."""
    generator = CodeMetaGenerator(verbose=False)
    generator.discovered_modules = generator.discover_modules()
    
    repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
    aggregated_data = generator.execute_modules(repo_url)
    codemeta_data = generator.build_codemeta(aggregated_data)
    
    is_valid, errors = generator.validate(codemeta_data)
    assert is_valid, f"Validation failed: {errors}"
    print(f"✓ Validation test passed: metadata is valid")

def test_output_writing(output_file: str = "/tmp/test_codemeta.jsonld"):
    """Test that output is written correctly."""
    generator = CodeMetaGenerator(verbose=False)
    generator.discovered_modules = generator.discover_modules()
    
    repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
    aggregated_data = generator.execute_modules(repo_url)
    codemeta_data = generator.build_codemeta(aggregated_data)
    
    success = generator.write_output(codemeta_data, output_file)
    assert success, "Failed to write output"
    
    # Verify the file was created and contains valid JSON
    with open(output_file, 'r') as f:
        data = json.load(f)
    
    assert isinstance(data, dict), "Output should be a dictionary"
    assert "@context" in data, "Output should have @context"
    
    # Clean up
    Path(output_file).unlink()
    print(f"✓ Output writing test passed: file created and contains valid JSON")

def test_utility_functions():
    """Test utility functions."""
    # Test is_url
    assert is_url("https://github.com/rsiebes/sshoc-nl-codemeta-generator"), "Valid URL not recognized"
    assert not is_url("not a url"), "Invalid URL recognized as valid"
    
    # Test is_email
    assert is_email("test@example.com"), "Valid email not recognized"
    assert not is_email("not an email"), "Invalid email recognized as valid"
    
    # Test is_date
    assert is_date("2024-01-01"), "Valid date not recognized"
    assert not is_date("not a date"), "Invalid date recognized as valid"
    
    # Test filter_empty_values
    data = {"a": 1, "b": "", "c": None, "d": [], "e": {}}
    filtered = filter_empty_values(data)
    assert "a" in filtered and "b" not in filtered, "Empty values not filtered correctly"
    
    print(f"✓ Utility functions test passed")

def test_full_generation():
    """Test the full generation process."""
    generator = CodeMetaGenerator(verbose=False)
    repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
    codemeta_data = generator.generate(repo_url, output_file="/tmp/test_full_codemeta.jsonld")
    
    assert isinstance(codemeta_data, dict), "Generated data should be a dictionary"
    assert "@context" in codemeta_data, "Missing @context"
    assert "@type" in codemeta_data, "Missing @type"
    assert len(codemeta_data) > 2, "Generated data should have more than just @context and @type"
    
    # Clean up
    Path("/tmp/test_full_codemeta.jsonld").unlink()
    print(f"✓ Full generation test passed: {len(codemeta_data)} properties generated")

def run_all_tests():
    """Run all tests."""
    print("=" * 80)
    print("RUNNING ORCHESTRATOR TESTS")
    print("=" * 80)
    print()
    
    tests = [
        test_module_discovery,
        test_module_execution,
        test_codemeta_building,
        test_validation,
        test_output_writing,
        test_utility_functions,
        test_full_generation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
    
    print()
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
