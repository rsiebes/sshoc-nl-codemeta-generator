#!/usr/bin/env python3
"""
Test script to generate Codemeta for the amalgame repository

Tests the enhanced author property with organization URL resolution
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.generator import CodemetaGenerator


def test_amalgame_repository():
    """Test Codemeta generation for the amalgame repository."""
    print("=" * 70)
    print("Testing Codemeta Generation for Amalgame Repository")
    print("=" * 70)
    print()
    
    try:
        generator = CodemetaGenerator()
        
        # Generate Codemeta for amalgame
        repo_url = "https://github.com/jrvosse/amalgame"
        print(f"Generating Codemeta for: {repo_url}")
        print()
        
        codemeta = generator.generate(repo_url)
        
        print()
        print("=" * 70)
        print("Author Information with Affiliations:")
        print("=" * 70)
        print()
        
        if 'author' in codemeta:
            for i, author in enumerate(codemeta['author'], 1):
                print(f"Author {i}:")
                print(f"  Name: {author.get('name')}")
                if 'email' in author:
                    print(f"  Email: {author.get('email')}")
                if '@id' in author:
                    print(f"  ORCID: {author.get('@id')}")
                if 'affiliation' in author:
                    aff = author['affiliation']
                    print(f"  Affiliation: {aff.get('name')}")
                    if 'url' in aff:
                        print(f"  Affiliation URL: {aff.get('url')}")
                    else:
                        print(f"  Affiliation URL: (not found)")
                print()
        else:
            print("No authors found in the repository")
        
        print("=" * 70)
        print("Full Codemeta Output (first 2000 chars):")
        print("=" * 70)
        print()
        
        codemeta_json = json.dumps(codemeta, indent=2)
        print(codemeta_json[:2000])
        if len(codemeta_json) > 2000:
            print(f"\n... (truncated, total length: {len(codemeta_json)} chars)")
        
        print()
        print("=" * 70)
        print("✅ Test completed successfully!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_amalgame_repository()
    sys.exit(0 if success else 1)
