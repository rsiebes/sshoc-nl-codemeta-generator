#!/usr/bin/env python3
"""Test script for author submodule integration with Codemeta."""

import sys
import json

sys.path.insert(0, '.')

from src.submodules.author import AuthorSubmodule


def test_author_submodule():
    """Test author submodule with example repositories."""
    
    test_repos = [
        {
            "name": "amalgame",
            "url": "https://github.com/jrvosse/amalgame",
            "description": "Ontology alignment tool"
        },
        {
            "name": "osmenrich",
            "url": "https://github.com/sodascience/osmenrich",
            "description": "OpenStreetMap enrichment tool"
        },
    ]

    print("=" * 80)
    print("Author Submodule Integration Test")
    print("=" * 80)

    for repo in test_repos:
        print(f"\n{'=' * 80}")
        print(f"Repository: {repo['name']}")
        print(f"URL: {repo['url']}")
        print("=" * 80)

        # Create author submodule instance
        submodule = AuthorSubmodule(repo)

        # Execute the submodule
        print("\nExecuting author extraction and enrichment...")
        result = submodule.run()

        if result and 'author' in result:
            print(f"✓ Successfully extracted {len(result['author'])} authors:\n")
            print(json.dumps(result, indent=2))
        else:
            print("✗ No authors found or extraction failed")

    print(f"\n{'=' * 80}")
    print("All tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    test_author_submodule()
