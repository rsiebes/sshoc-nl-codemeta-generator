#!/usr/bin/env python3
"""
Debug script for OnlySwitch repository

Tests organization URL resolution for "Axel Springer"
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.organization_url_resolver import OrganizationURLResolver


def test_axel_springer():
    """Test resolution of Axel Springer organization."""
    print("=" * 70)
    print("Testing Organization URL Resolution for Axel Springer")
    print("=" * 70)
    print()
    
    resolver = OrganizationURLResolver()
    
    test_cases = [
        "Axel Springer",
        "axel springer",
        "Axel Springer SE",
        "Axel Springer AG",
    ]
    
    for org_name in test_cases:
        print(f"Testing: '{org_name}'")
        url = resolver.resolve_organization_url(org_name)
        print(f"  Result: {url}")
        if url:
            print(f"  ✅ Resolved")
        else:
            print(f"  ❌ Not resolved")
        print()
    
    print("=" * 70)


def test_onlyswitch_repository():
    """Test Codemeta generation for OnlySwitch repository."""
    from src.generator import CodemetaGenerator
    
    print("\n" + "=" * 70)
    print("Testing OnlySwitch Repository")
    print("=" * 70)
    print()
    
    try:
        generator = CodemetaGenerator()
        
        repo_url = "https://github.com/jacklandrin/OnlySwitch"
        print(f"Generating Codemeta for: {repo_url}")
        print()
        
        codemeta = generator.generate(repo_url)
        
        print("=" * 70)
        print("Author Information:")
        print("=" * 70)
        print()
        
        if 'author' in codemeta:
            for i, author in enumerate(codemeta['author'], 1):
                print(f"Author {i}:")
                print(f"  Name: {author.get('name')}")
                if 'affiliation' in author:
                    aff = author['affiliation']
                    print(f"  Affiliation: {aff.get('name')}")
                    if 'url' in aff:
                        print(f"  Affiliation URL: {aff.get('url')}")
                        print(f"  ✅ URL found")
                    else:
                        print(f"  ❌ NO URL found")
                print()
        else:
            print("No authors found")
        
        print("=" * 70)
        print("Full Codemeta (first 2000 chars):")
        print("=" * 70)
        print()
        
        codemeta_json = json.dumps(codemeta, indent=2)
        print(codemeta_json[:2000])
        if len(codemeta_json) > 2000:
            print(f"\n... (truncated, total length: {len(codemeta_json)} chars)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print()
    
    # Test Axel Springer resolution
    test_axel_springer()
    
    # Test OnlySwitch repository
    test_onlyswitch_repository()
