#!/usr/bin/env python3
"""
Test script for Wikidata enricher functionality.

This script demonstrates how to fetch Wikidata information for keywords.
"""

import json
from src.helpers.wikidata_enricher import fetch_wikidata_for_keyword, enrich_keywords_with_wikidata
from src.core import get_logger

logger = get_logger(__name__)

# Test keywords
TEST_KEYWORDS = [
    "Python",
    "Machine Learning",
    "Data Science",
    "Ontology",
    "Semantic Web",
]


def test_single_keyword():
    """Test fetching Wikidata for a single keyword."""
    print("\n" + "=" * 80)
    print("Test 1: Single Keyword Wikidata Lookup")
    print("=" * 80 + "\n")

    keyword = "Python"
    print(f"Searching Wikidata for: {keyword}")
    print("-" * 80)

    result = fetch_wikidata_for_keyword(keyword)

    if result is None:
        print("✗ Error fetching data from Wikidata")
    elif result == "":
        print("✗ No results found in Wikidata")
    else:
        data = json.loads(result)
        print(f"✓ Found {len(data['search'])} results in Wikidata\n")
        print("Top 3 results:")
        for i, item in enumerate(data["search"][:3], 1):
            print(f"\n  {i}. {item.get('label', 'N/A')}")
            print(f"     Description: {item.get('description', 'N/A')}")
            print(f"     ID: {item.get('id', 'N/A')}")


def test_multiple_keywords():
    """Test fetching Wikidata for multiple keywords."""
    print("\n" + "=" * 80)
    print("Test 2: Multiple Keywords Wikidata Enrichment")
    print("=" * 80 + "\n")

    print(f"Searching Wikidata for {len(TEST_KEYWORDS)} keywords...")
    print("-" * 80)

    enriched = enrich_keywords_with_wikidata(TEST_KEYWORDS)

    found_count = 0
    not_found_count = 0
    error_count = 0

    print("\nResults:\n")
    for keyword, result in enriched.items():
        if result is None:
            print(f"  ✗ {keyword:25s} | Error fetching data")
            error_count += 1
        elif result == "":
            print(f"  ✗ {keyword:25s} | Not found in Wikidata")
            not_found_count += 1
        else:
            data = json.loads(result)
            num_results = len(data.get("search", []))
            print(f"  ✓ {keyword:25s} | {num_results} results found")
            found_count += 1

    print("\n" + "-" * 80)
    print(f"Summary: {found_count} found, {not_found_count} not found, {error_count} errors")


def test_detailed_output():
    """Test with detailed output showing JSON structure."""
    print("\n" + "=" * 80)
    print("Test 3: Detailed JSON Output Example")
    print("=" * 80 + "\n")

    keyword = "Semantic Web"
    print(f"Fetching Wikidata for: {keyword}")
    print("-" * 80)

    result = fetch_wikidata_for_keyword(keyword)

    if result is None:
        print("✗ Error fetching data from Wikidata")
    elif result == "":
        print("✗ No results found in Wikidata")
    else:
        data = json.loads(result)
        print(f"\n✓ Full JSON Response (first result only):\n")
        
        # Show structure
        if data.get("search"):
            first_result = data["search"][0]
            print(json.dumps(first_result, indent=2))
        
        print(f"\nTotal results: {len(data.get('search', []))}")


def test_empty_results():
    """Test with a keyword that likely has no results."""
    print("\n" + "=" * 80)
    print("Test 4: Empty Results Handling")
    print("=" * 80 + "\n")

    # Use a very specific/uncommon keyword
    keyword = "xyzabc123notreal"
    print(f"Searching for unlikely keyword: {keyword}")
    print("-" * 80)

    result = fetch_wikidata_for_keyword(keyword)

    if result is None:
        print("✗ Error fetching data from Wikidata")
    elif result == "":
        print("✓ Correctly returned empty string for no results")
    else:
        print("✗ Unexpected: Found results for non-existent keyword")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Wikidata Enricher Test Suite")
    print("=" * 80)

    test_single_keyword()
    test_multiple_keywords()
    test_detailed_output()
    test_empty_results()

    print("\n" + "=" * 80)
    print("All tests completed!")
    print("=" * 80 + "\n")
