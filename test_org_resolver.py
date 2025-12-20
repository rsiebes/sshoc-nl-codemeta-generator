#!/usr/bin/env python3
"""
Test script for Organization URL Resolver

Tests the organization URL resolution functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.organization_url_resolver import OrganizationURLResolver


def test_organization_resolver():
    """Test the organization URL resolver."""
    resolver = OrganizationURLResolver()
    
    # Test cases
    test_cases = [
        ('VU', 'https://www.vu.nl'),
        ('VU Amsterdam', 'https://www.vu.nl'),
        ('Vrije Universiteit', 'https://www.vu.nl'),
        ('MIT', 'https://www.mit.edu'),
        ('Stanford', 'https://www.stanford.edu'),
        ('Harvard', 'https://www.harvard.edu'),
        ('University of Amsterdam', 'https://www.uva.nl'),
        ('Max Planck', 'https://www.mpg.de'),
        ('CERN', 'https://www.cern.ch'),
        ('Apache Software Foundation', 'https://www.apache.org'),
    ]
    
    print("=" * 70)
    print("Organization URL Resolver Test")
    print("=" * 70)
    print()
    
    passed = 0
    failed = 0
    
    for org_name, expected_url in test_cases:
        result = resolver.resolve_organization_url(org_name)
        
        if result == expected_url:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        print(f"{status}: {org_name}")
        print(f"  Expected: {expected_url}")
        print(f"  Got:      {result}")
        print()
    
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


def test_author_with_affiliation():
    """Test author property with affiliation URL resolution."""
    from src.properties.author import AuthorMetadata
    
    print("\n" + "=" * 70)
    print("Author Property with Affiliation URL Test")
    print("=" * 70)
    print()
    
    # Test data with organization affiliation
    raw_data = {
        'author': [
            {
                'name': 'John Doe',
                'email': 'john@example.com',
                'organization': 'VU'
            },
            {
                'name': 'Jane Smith',
                'email': 'jane@example.com',
                'affiliation': 'MIT'
            }
        ]
    }
    
    author_metadata = AuthorMetadata(raw_data)
    result = author_metadata.extract()
    
    print("Input:")
    print(f"  Author 1: John Doe (VU)")
    print(f"  Author 2: Jane Smith (MIT)")
    print()
    
    print("Output:")
    if 'author' in result:
        for i, author in enumerate(result['author'], 1):
            print(f"  Author {i}:")
            print(f"    Name: {author.get('name')}")
            print(f"    Email: {author.get('email')}")
            if 'affiliation' in author:
                aff = author['affiliation']
                print(f"    Affiliation: {aff.get('name')}")
                if 'url' in aff:
                    print(f"    Affiliation URL: {aff.get('url')}")
                else:
                    print(f"    Affiliation URL: (not resolved)")
            print()
    
    # Check if URLs were resolved
    success = True
    if 'author' in result:
        for author in result['author']:
            if 'affiliation' in author and 'url' not in author['affiliation']:
                print(f"⚠️  Warning: No URL found for {author['affiliation'].get('name')}")
                success = False
    
    if success:
        print("✅ All affiliations have URLs resolved!")
    
    print("=" * 70)
    return success


if __name__ == '__main__':
    print()
    
    # Test resolver
    test1_passed = test_organization_resolver()
    
    # Test author property
    test2_passed = test_author_with_affiliation()
    
    print()
    if test1_passed and test2_passed:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
