#!/usr/bin/env python3
"""
Test script for the complete keywords pipeline with Codemeta output.

This script demonstrates the full workflow:
1. Extract keywords using Gemini
2. Enrich with Wikidata
3. Match to Wikidata concepts
4. Generate Codemeta DefinedTerm format
"""

import json
from src.submodules.keywords import KeywordsSubmodule
from src.core import get_logger

logger = get_logger(__name__)

# Test repositories
TEST_REPOSITORIES = [
    {
        "name": "amalgame",
        "html_url": "https://github.com/jrvosse/amalgame",
        "description": "Alignment tool for ontologies and vocabularies using semantic web technologies",
    },
    {
        "name": "osmenrich",
        "html_url": "https://github.com/sodascience/osmenrich",
        "description": "Enriches spatial data with OpenStreetMap features",
    },
    {
        "name": "metasyn",
        "html_url": "https://github.com/sodascience/metasyn",
        "description": "Generates synthetic data for privacy-preserving research",
    },
]


def test_single_repository():
    """Test keywords extraction and Codemeta output for a single repository."""
    print("\n" + "=" * 80)
    print("Test 1: Single Repository Keywords Pipeline")
    print("=" * 80 + "\n")

    repo = TEST_REPOSITORIES[0]

    print(f"Repository: {repo['name']}")
    print(f"URL: {repo['html_url']}")
    print(f"Description: {repo['description']}")
    print("-" * 80)

    # Create repo_data structure
    repo_data = {"data": repo}

    # Create and run keywords submodule
    keywords_submodule = KeywordsSubmodule(repo_data)
    defined_terms = keywords_submodule.extract()

    if defined_terms:
        print(f"\n✓ Successfully extracted {len(defined_terms)} keywords\n")
        print("Codemeta Keywords Output:\n")
        print(json.dumps({"keywords": defined_terms}, indent=2))
    else:
        print(f"\n✗ Failed to extract keywords")
        if keywords_submodule.error:
            print(f"Error: {keywords_submodule.error}")


def test_multiple_repositories():
    """Test keywords extraction for multiple repositories."""
    print("\n" + "=" * 80)
    print("Test 2: Multiple Repositories Keywords Pipeline")
    print("=" * 80 + "\n")

    for repo in TEST_REPOSITORIES:
        print(f"Repository: {repo['name']}")
        print(f"URL: {repo['html_url']}")
        print("-" * 80)

        # Create repo_data structure
        repo_data = {"data": repo}

        # Create and run keywords submodule
        keywords_submodule = KeywordsSubmodule(repo_data)
        defined_terms = keywords_submodule.extract()

        if defined_terms:
            print(f"✓ Extracted {len(defined_terms)} keywords\n")

            # Display keywords in a table format
            print(f"{'Keyword':<30} {'Wikidata URL'}")
            print("-" * 80)
            for term in defined_terms:
                print(f"{term['name']:<30} {term['url']}")
        else:
            print(f"✗ Failed to extract keywords")
            if keywords_submodule.error:
                print(f"Error: {keywords_submodule.error}")

        print()


def test_codemeta_format():
    """Test the complete Codemeta format with keywords."""
    print("\n" + "=" * 80)
    print("Test 3: Complete Codemeta Format with Keywords")
    print("=" * 80 + "\n")

    repo = TEST_REPOSITORIES[0]

    print(f"Repository: {repo['name']}")
    print("-" * 80)

    # Create repo_data structure
    repo_data = {"data": repo}

    # Create and run keywords submodule
    keywords_submodule = KeywordsSubmodule(repo_data)
    defined_terms = keywords_submodule.extract()

    if defined_terms:
        # Create a sample Codemeta object
        codemeta = {
            "@context": "https://w3id.org/codemeta/v2.0",
            "@type": "SoftwareSourceCode",
            "name": repo["name"],
            "description": repo["description"],
            "url": repo["html_url"],
            "keywords": defined_terms,
        }

        print("\n✓ Complete Codemeta Output:\n")
        print(json.dumps(codemeta, indent=2))
    else:
        print(f"\n✗ Failed to extract keywords")


def test_keywords_structure():
    """Test and display the structure of keywords output."""
    print("\n" + "=" * 80)
    print("Test 4: Keywords Structure Validation")
    print("=" * 80 + "\n")

    repo = TEST_REPOSITORIES[0]

    # Create repo_data structure
    repo_data = {"data": repo}

    # Create and run keywords submodule
    keywords_submodule = KeywordsSubmodule(repo_data)
    defined_terms = keywords_submodule.extract()

    if defined_terms:
        print("✓ Keywords structure validation:\n")

        # Validate structure
        all_valid = True
        for i, term in enumerate(defined_terms, 1):
            is_valid = (
                isinstance(term, dict)
                and "@type" in term
                and term["@type"] == "DefinedTerm"
                and "name" in term
                and "url" in term
                and term["url"].startswith("https://www.wikidata.org/wiki/Q")
            )

            status = "✓" if is_valid else "✗"
            print(f"  {status} Keyword {i}: {term.get('name', 'N/A')}")

            if not is_valid:
                print(f"     Invalid structure: {term}")
                all_valid = False

        print()
        if all_valid:
            print("✓ All keywords have valid structure!")
        else:
            print("✗ Some keywords have invalid structure")
    else:
        print("✗ Failed to extract keywords")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Complete Keywords Pipeline Test Suite")
    print("=" * 80)

    test_single_repository()
    test_multiple_repositories()
    test_codemeta_format()
    test_keywords_structure()

    print("\n" + "=" * 80)
    print("All tests completed!")
    print("=" * 80 + "\n")
