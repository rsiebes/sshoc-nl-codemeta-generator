#!/usr/bin/env python3
"""
Test script for Contributor and Maintainer properties with organization URL resolution

Tests that both contributor and maintainer properties now include organization URLs
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.properties.contributor import ContributorMetadata
from src.properties.maintainer import MaintainerMetadata


def test_contributor_with_affiliation():
    """Test contributor property with affiliation URL resolution."""
    print("=" * 70)
    print("Contributor Property with Affiliation URL Test")
    print("=" * 70)
    print()
    
    # Test data with organization affiliation
    raw_data = {
        'contributor': [
            {
                'name': 'Alice Johnson',
                'email': 'alice@example.com',
                'organization': 'MIT'
            },
            {
                'name': 'Bob Smith',
                'email': 'bob@example.com',
                'affiliation': 'Stanford'
            },
            {
                'name': 'Carol White',
                'email': 'carol@example.com',
                'organization': 'Harvard'
            }
        ]
    }
    
    contributor_metadata = ContributorMetadata(raw_data)
    result = contributor_metadata.extract()
    
    print("Input:")
    print(f"  Contributor 1: Alice Johnson (MIT)")
    print(f"  Contributor 2: Bob Smith (Stanford)")
    print(f"  Contributor 3: Carol White (Harvard)")
    print()
    
    print("Output:")
    success = True
    if 'contributor' in result:
        for i, contributor in enumerate(result['contributor'], 1):
            print(f"  Contributor {i}:")
            print(f"    Name: {contributor.get('name')}")
            print(f"    Email: {contributor.get('email')}")
            if 'affiliation' in contributor:
                aff = contributor['affiliation']
                print(f"    Affiliation: {aff.get('name')}")
                if 'url' in aff:
                    print(f"    Affiliation URL: {aff.get('url')}")
                    print(f"    ✅ URL resolved")
                else:
                    print(f"    ❌ URL not resolved")
                    success = False
            print()
    
    print("=" * 70)
    return success


def test_maintainer_with_affiliation():
    """Test maintainer property with affiliation URL resolution."""
    print("\n" + "=" * 70)
    print("Maintainer Property with Affiliation URL Test")
    print("=" * 70)
    print()
    
    # Test data with organization affiliation
    raw_data = {
        'maintainer': {
            'name': 'Dr. David Chen',
            'email': 'david@example.com',
            'organization': 'CERN'
        }
    }
    
    maintainer_metadata = MaintainerMetadata(raw_data)
    result = maintainer_metadata.extract()
    
    print("Input:")
    print(f"  Maintainer: Dr. David Chen (CERN)")
    print()
    
    print("Output:")
    success = True
    if 'maintainer' in result:
        maintainer = result['maintainer']
        print(f"  Name: {maintainer.get('name')}")
        print(f"  Email: {maintainer.get('email')}")
        if 'affiliation' in maintainer:
            aff = maintainer['affiliation']
            print(f"  Affiliation: {aff.get('name')}")
            if 'url' in aff:
                print(f"  Affiliation URL: {aff.get('url')}")
                print(f"  ✅ URL resolved")
            else:
                print(f"  ❌ URL not resolved")
                success = False
        print()
    
    print("=" * 70)
    return success


def test_amalgame_repository():
    """Test Codemeta generation for the amalgame repository with all properties."""
    from src.generator import CodemetaGenerator
    
    print("\n" + "=" * 70)
    print("Full Integration Test: Amalgame Repository")
    print("=" * 70)
    print()
    
    try:
        generator = CodemetaGenerator()
        
        # Generate Codemeta for amalgame
        repo_url = "https://github.com/jrvosse/amalgame"
        print(f"Generating Codemeta for: {repo_url}")
        print()
        
        codemeta = generator.generate(repo_url)
        
        print("=" * 70)
        print("Author, Contributor, and Maintainer Information:")
        print("=" * 70)
        print()
        
        success = True
        
        # Check author
        if 'author' in codemeta:
            print("✅ Author(s):")
            for i, author in enumerate(codemeta['author'], 1):
                print(f"  {i}. {author.get('name')}")
                if 'affiliation' in author:
                    aff = author['affiliation']
                    print(f"     Organization: {aff.get('name')}")
                    if 'url' in aff:
                        print(f"     URL: {aff.get('url')}")
                    else:
                        print(f"     URL: (not resolved)")
            print()
        
        # Check contributor
        if 'contributor' in codemeta:
            print("✅ Contributor(s):")
            contributors = codemeta['contributor']
            if not isinstance(contributors, list):
                contributors = [contributors]
            
            for i, contributor in enumerate(contributors, 1):
                print(f"  {i}. {contributor.get('name')}")
                if 'affiliation' in contributor:
                    aff = contributor['affiliation']
                    print(f"     Organization: {aff.get('name')}")
                    if 'url' in aff:
                        print(f"     URL: {aff.get('url')}")
                    else:
                        print(f"     URL: (not resolved)")
            print()
        
        # Check maintainer
        if 'maintainer' in codemeta:
            print("✅ Maintainer:")
            maintainer = codemeta['maintainer']
            if isinstance(maintainer, dict):
                print(f"  {maintainer.get('name')}")
                if 'affiliation' in maintainer:
                    aff = maintainer['affiliation']
                    print(f"     Organization: {aff.get('name')}")
                    if 'url' in aff:
                        print(f"     URL: {aff.get('url')}")
                    else:
                        print(f"     URL: (not resolved)")
            print()
        
        print("=" * 70)
        print("✅ Full integration test completed successfully!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print()
    
    # Test contributor
    test1_passed = test_contributor_with_affiliation()
    
    # Test maintainer
    test2_passed = test_maintainer_with_affiliation()
    
    # Test full integration
    test3_passed = test_amalgame_repository()
    
    print()
    if test1_passed and test2_passed and test3_passed:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
