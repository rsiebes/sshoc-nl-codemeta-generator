#!/usr/bin/env python3
"""Test script for Gemini author enricher."""

import sys
import json

sys.path.insert(0, '.')

from src.helpers.github_author_extractor import extract_unique_authors
from src.helpers.gemini_author_enricher import enrich_authors_with_gemini


def test_author_enrichment():
    """Test author enrichment with Gemini."""
    
    test_repos = [
        "https://github.com/jrvosse/amalgame",
        "https://github.com/sodascience/osmenrich",
    ]

    print("=" * 80)
    print("Gemini Author Enrichment Test")
    print("=" * 80)

    for repo_url in test_repos:
        print(f"\n{'=' * 80}")
        print(f"Repository: {repo_url}")
        print("=" * 80)

        # Step 1: Extract authors from GitHub
        print("\n[Step 1] Extracting authors from GitHub commits...")
        authors_json = extract_unique_authors(repo_url)

        if not authors_json:
            print("✗ Failed to extract authors from GitHub")
            continue

        authors_data = json.loads(authors_json)
        print(f"✓ Found {authors_data['total_unique_authors']} unique authors:")
        for author in authors_data['authors']:
            print(f"  - {author['name']} ({author['email']})")

        # Step 2: Enrich with Gemini
        print("\n[Step 2] Enriching authors with ORCID and affiliations via Gemini...")
        enriched_json = enrich_authors_with_gemini(authors_json, repo_url)

        if enriched_json:
            print("✓ Successfully enriched authors:\n")
            enriched_data = json.loads(enriched_json)
            print(json.dumps(enriched_data, indent=2))
        else:
            print("✗ Failed to enrich authors with Gemini")

    print(f"\n{'=' * 80}")
    print("All tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    test_author_enrichment()
