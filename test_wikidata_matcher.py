#!/usr/bin/env python3
"""
Test script for Wikidata concept matching with Gemini.

This script demonstrates how Gemini intelligently selects the best Wikidata
concept URI for keywords based on repository context.
"""

import json
from src.helpers.wikidata_enricher import fetch_wikidata_for_keyword
from src.helpers.wikidata_matcher import (
    match_keyword_to_wikidata_concept,
    match_keywords_to_wikidata_concepts,
)
from src.core import get_logger

logger = get_logger(__name__)

# Test data
TEST_KEYWORDS = ["Python", "Ontology", "Semantic Web", "Data Science"]

TEST_REPOSITORIES = [
    {
        "url": "https://github.com/jrvosse/amalgame",
        "description": "Alignment tool for ontologies and vocabularies using semantic web technologies",
    },
    {
        "url": "https://github.com/sodascience/osmenrich",
        "description": "Enriches spatial data with OpenStreetMap features",
    },
]


def test_single_keyword_matching():
    """Test matching a single keyword to Wikidata concept."""
    print("\n" + "=" * 80)
    print("Test 1: Single Keyword Concept Matching")
    print("=" * 80 + "\n")

    keyword = "Python"
    repo_url = "https://github.com/jrvosse/amalgame"
    repo_description = "Alignment tool for ontologies and vocabularies"

    print(f"Keyword: {keyword}")
    print(f"Repository: {repo_url}")
    print(f"Description: {repo_description}")
    print("-" * 80)

    # Fetch Wikidata results
    wikidata_json = fetch_wikidata_for_keyword(keyword)

    if not wikidata_json:
        print("✗ Failed to fetch Wikidata results")
        return

    # Match to concept
    match = match_keyword_to_wikidata_concept(
        keyword, wikidata_json, repo_url, repo_description
    )

    if match:
        print(f"\n✓ Successfully matched keyword to Wikidata concept:\n")
        print(f"  Keyword:      {match.keyword}")
        print(f"  Concept URI:  {match.concept_uri}")
        print(f"  Label:        {match.label}")
        print(f"  Description:  {match.description}")
        print(f"  Confidence:   {match.confidence}")
        print(f"  Reasoning:    {match.reasoning}")
    else:
        print("✗ Failed to match keyword to concept")


def test_multiple_keywords_matching():
    """Test matching multiple keywords to Wikidata concepts."""
    print("\n" + "=" * 80)
    print("Test 2: Multiple Keywords Concept Matching")
    print("=" * 80 + "\n")

    repo = TEST_REPOSITORIES[0]
    print(f"Repository: {repo['url']}")
    print(f"Description: {repo['description']}")
    print("-" * 80)

    # Fetch Wikidata results for all keywords
    print(f"\nFetching Wikidata results for {len(TEST_KEYWORDS)} keywords...")
    keywords_with_wikidata = {}

    for keyword in TEST_KEYWORDS:
        wikidata_json = fetch_wikidata_for_keyword(keyword)
        keywords_with_wikidata[keyword] = wikidata_json

    print("✓ Wikidata results fetched\n")

    # Match all keywords to concepts
    print("Matching keywords to Wikidata concepts using Gemini...")
    matches = match_keywords_to_wikidata_concepts(
        keywords_with_wikidata, repo["url"], repo["description"]
    )

    print("\nResults:\n")
    for keyword, match in matches.items():
        if match:
            print(f"  {keyword:20s} → {match.label:25s} ({match.confidence})")
            print(f"    URI: {match.concept_uri}")
            print(f"    Reason: {match.reasoning}\n")
        else:
            print(f"  {keyword:20s} → ✗ No match found\n")


def test_context_aware_matching():
    """Test that matching is context-aware for different repositories."""
    print("\n" + "=" * 80)
    print("Test 3: Context-Aware Matching Across Repositories")
    print("=" * 80 + "\n")

    keyword = "Data"

    print(f"Testing keyword: '{keyword}' across different repositories\n")

    # Fetch Wikidata results once
    wikidata_json = fetch_wikidata_for_keyword(keyword)

    if not wikidata_json:
        print("✗ Failed to fetch Wikidata results")
        return

    print("Matching in different repository contexts:\n")

    for repo in TEST_REPOSITORIES:
        print(f"Repository: {repo['url']}")
        print(f"Description: {repo['description']}")
        print("-" * 40)

        match = match_keyword_to_wikidata_concept(
            keyword, wikidata_json, repo["url"], repo["description"]
        )

        if match:
            print(f"  Matched to: {match.label}")
            print(f"  URI: {match.concept_uri}")
            print(f"  Confidence: {match.confidence}")
            print(f"  Reasoning: {match.reasoning}\n")
        else:
            print("  ✗ No match found\n")


def test_full_pipeline():
    """Test the complete pipeline: keywords → Wikidata → Concept matching."""
    print("\n" + "=" * 80)
    print("Test 4: Complete Pipeline (Keywords → Wikidata → Concepts)")
    print("=" * 80 + "\n")

    keywords = ["Python", "Machine Learning", "Data Science"]
    repo = TEST_REPOSITORIES[1]

    print(f"Repository: {repo['url']}")
    print(f"Description: {repo['description']}")
    print(f"Keywords: {', '.join(keywords)}")
    print("-" * 80)

    # Step 1: Fetch Wikidata results
    print("\nStep 1: Fetching Wikidata results...")
    keywords_with_wikidata = {}
    for keyword in keywords:
        wikidata_json = fetch_wikidata_for_keyword(keyword)
        keywords_with_wikidata[keyword] = wikidata_json
    print(f"✓ Fetched results for {len(keywords_with_wikidata)} keywords")

    # Step 2: Match to concepts
    print("\nStep 2: Matching keywords to Wikidata concepts...")
    matches = match_keywords_to_wikidata_concepts(
        keywords_with_wikidata, repo["url"], repo["description"]
    )
    print(f"✓ Matched {len([m for m in matches.values() if m])} keywords")

    # Step 3: Display results
    print("\nStep 3: Results\n")
    print(f"{'Keyword':<20} {'Concept Label':<30} {'Confidence':<12} {'URI'}")
    print("-" * 90)

    for keyword, match in matches.items():
        if match:
            print(
                f"{keyword:<20} {match.label:<30} {match.confidence:<12} {match.concept_uri}"
            )
        else:
            print(f"{keyword:<20} {'N/A':<30} {'N/A':<12} N/A")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Wikidata Concept Matcher Test Suite")
    print("=" * 80)

    test_single_keyword_matching()
    test_multiple_keywords_matching()
    test_context_aware_matching()
    test_full_pipeline()

    print("\n" + "=" * 80)
    print("All tests completed!")
    print("=" * 80 + "\n")
