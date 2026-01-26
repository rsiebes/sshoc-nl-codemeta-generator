#!/usr/bin/env python3
"""
Test script for author extraction using Gemini.
"""

import sys
sys.path.insert(0, '/home/ubuntu/sshoc-nl-codemeta-generator')

from src.helpers.gemini_author_extractor import extract_authors

# Test repositories
test_repos = [
    "https://github.com/jrvosse/amalgame",
    "https://github.com/sodascience/osmenrich",
]

print("=" * 80)
print("Author Extraction Test")
print("=" * 80)

for repo_url in test_repos:
    print(f"\n{'=' * 80}")
    print(f"Repository: {repo_url}")
    print(f"{'=' * 80}\n")
    
    author_data = extract_authors(repo_url)
    
    if author_data:
        print("✓ Successfully extracted author metadata:\n")
        import json
        print(json.dumps(author_data, indent=2))
    else:
        print("✗ Failed to extract author metadata")

print(f"\n{'=' * 80}")
print("Test completed")
print("=" * 80)
