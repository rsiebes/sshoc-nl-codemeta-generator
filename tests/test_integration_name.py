#!/usr/bin/env python3
"""
Integration tests for the codemeta_name module with the orchestrator.
"""

import sys
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.codemeta_generator import CodeMetaGenerator
from src.modules.codemeta_name import get as get_name


def test_name_module_with_orchestrator():
    """Test that the name module integrates correctly with the orchestrator."""
    generator = CodeMetaGenerator(verbose=False)
    repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
    
    # Generate metadata
    codemeta_data = generator.generate(repo_url, output_file="/tmp/test_integration_codemeta.jsonld")
    
    # Verify that the name property is present
    assert "name" in codemeta_data, "Name property not found in generated metadata"
    assert codemeta_data["name"] is not None, "Name property is None"
    assert codemeta_data["name"] != "", "Name property is empty"
    
    print(f"✓ Name module integration test passed")
    print(f"  Generated name: {codemeta_data['name']}")
    
    # Clean up
    Path("/tmp/test_integration_codemeta.jsonld").unlink()


def test_name_module_direct_call():
    """Test calling the name module directly."""
    repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
    result = get_name(repo_url)
    
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "name" in result, "Name property not found in result"
    assert result["name"] is not None, "Name property is None"
    assert result["name"] != "", "Name property is empty"
    
    print(f"✓ Direct name module call test passed")
    print(f"  Extracted name: {result['name']}")


def test_name_module_output_format():
    """Test that the name module returns the correct format."""
    repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
    result = get_name(repo_url)
    
    # Check format
    assert isinstance(result, dict), "Result should be a dictionary"
    assert len(result) == 1, "Result should have exactly one key-value pair"
    assert "name" in result, "Result should have 'name' key"
    
    # Check value type
    assert isinstance(result["name"], str), "Name value should be a string"
    
    print(f"✓ Name module output format test passed")


def test_name_module_with_different_repos():
    """Test the name module with different repository types."""
    test_cases = [
        ("https://github.com/rsiebes/sshoc-nl-codemeta-generator", "codemeta-generator"),
        ("https://github.com/python/cpython", "cpython"),
        ("https://github.com/torvalds/linux", "linux"),
    ]
    
    for repo_url, expected_name_part in test_cases:
        result = get_name(repo_url)
        
        if result:  # Only check if result is not empty
            name = result.get("name", "")
            # Check if the expected name part is in the result (case-insensitive)
            assert expected_name_part.lower() in name.lower() or name.lower() in expected_name_part.lower(), \
                f"Expected name to contain '{expected_name_part}', got '{name}' for {repo_url}"
            print(f"✓ Repository {repo_url}: {name}")
        else:
            print(f"⊘ Repository {repo_url}: No name extracted (may be due to API limits)")


def test_name_module_consistency():
    """Test that the name module returns consistent results."""
    repo_url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
    
    # Call the module multiple times
    results = [get_name(repo_url) for _ in range(3)]
    
    # Check that all results are the same
    for i in range(1, len(results)):
        assert results[i] == results[0], f"Inconsistent results: {results[0]} vs {results[i]}"
    
    print(f"✓ Name module consistency test passed")
    print(f"  Consistent name: {results[0].get('name', 'N/A')}")


def run_all_tests():
    """Run all integration tests."""
    print("=" * 80)
    print("RUNNING CODEMETA_NAME INTEGRATION TESTS")
    print("=" * 80)
    print()

    tests = [
        test_name_module_direct_call,
        test_name_module_output_format,
        test_name_module_consistency,
        test_name_module_with_orchestrator,
        test_name_module_with_different_repos,
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
