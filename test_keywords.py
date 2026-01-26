"""Test script for keywords extraction."""

import sys
import json
from src.submodules.keywords import KeywordsSubmodule
from src.core import get_logger

logger = get_logger(__name__)

# Test repositories
test_repos = [
    {
        "name": "amalgame",
        "url": "https://github.com/jrvosse/amalgame",
    },
    {
        "name": "osmenrich",
        "url": "https://github.com/sodascience/osmenrich",
    },
    {
        "name": "metasyn",
        "url": "https://github.com/sodascience/metasyn",
    },
]

def test_keywords_extraction():
    """Test keywords extraction for multiple repositories."""
    
    print("\n" + "="*80)
    print("Testing Keywords Extraction with Gemini API")
    print("="*80 + "\n")
    
    for repo in test_repos:
        print(f"Testing repository: {repo['name']}")
        print(f"URL: {repo['url']}")
        print("-" * 80)
        
        # Create repo_data structure
        repo_data = {
            "data": {
                "name": repo["name"],
                "html_url": repo["url"],
            }
        }
        
        # Extract keywords
        submodule = KeywordsSubmodule(repo_data)
        keywords = submodule.run()
        
        if keywords:
            print(f"✓ Successfully extracted {len(keywords)} keywords:")
            for i, keyword in enumerate(keywords, 1):
                print(f"  {i}. {keyword}")
        else:
            print(f"✗ Failed to extract keywords")
        
        print(f"Extraction time: {submodule.extraction_time:.3f}s")
        print()

if __name__ == "__main__":
    test_keywords_extraction()
