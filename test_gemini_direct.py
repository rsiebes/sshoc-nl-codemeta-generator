#!/usr/bin/env python3
"""
Direct test of Gemini keyword extraction for specific repositories.
"""

import sys
sys.path.insert(0, '/home/ubuntu/sshoc-nl-codemeta-generator')

from src.helpers.gemini_extractor import extract_keywords

# Test repositories
test_repos = [
    "https://github.com/jrvosse/amalgame",
    "https://github.com/sodascience/osmenrich",
]

print("=" * 80)
print("Direct Gemini Keyword Extraction Test")
print("=" * 80)

for repo_url in test_repos:
    print(f"\n{'=' * 80}")
    print(f"Repository: {repo_url}")
    print(f"{'=' * 80}\n")
    
    keywords = extract_keywords(repo_url)
    
    if keywords:
        print(f"✓ Extracted {len(keywords)} keywords:\n")
        for i, keyword in enumerate(keywords, 1):
            print(f"{i:2d}. {keyword.name:30s} | {keyword.context_clues}")
    else:
        print("✗ Failed to extract keywords")

print(f"\n{'=' * 80}")
print("Test completed")
print("=" * 80)
