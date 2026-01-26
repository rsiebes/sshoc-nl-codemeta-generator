#!/usr/bin/env python3
"""Test script for GitHub author extractor."""

import sys
import json

sys.path.insert(0, '.')

from src.helpers.github_author_extractor import extract_unique_authors


def test_github_author_extraction():
    """Test GitHub author extraction with multiple repositories."""
    
    test_repos = [
        "https://github.com/jrvosse/amalgame",
        "https://github.com/sodascience/osmenrich",
        "https://github.com/firmao/codemeta-ro-crate-vm",
    ]

    print("=" * 80)
    print("GitHub Author Extraction Test")
    print("=" * 80)

    for repo_url in test_repos:
        print(f"\n{'=' * 80}")
        print(f"Repository: {repo_url}")
        print("=" * 80)

        authors_json = extract_unique_authors(repo_url)

        if authors_json:
            print("✓ Successfully extracted authors:\n")
            authors_data = json.loads(authors_json)
            print(json.dumps(authors_data, indent=2))
        else:
            print("✗ Failed to extract authors")

    print(f"\n{'=' * 80}")
    print("All tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    test_github_author_extraction()
