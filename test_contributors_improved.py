#!/usr/bin/env python3
"""
Test script for improved contributor extraction
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.github_contributors_scraper import GitHubContributorsScraper


def test_contributors_scraper():
    """Test the improved contributors scraper."""
    print("=" * 70)
    print("Testing Improved GitHub Contributors Scraper")
    print("=" * 70)
    print()
    
    scraper = GitHubContributorsScraper()
    
    # Test with artscraper
    owner = "sodascience"
    repo = "artscraper"
    
    print(f"Scraping contributors for: {owner}/{repo}")
    print()
    
    contributors = scraper.scrape_contributors(owner, repo)
    
    print(f"Found {len(contributors)} contributors:")
    print()
    
    for i, contrib in enumerate(contributors, 1):
        print(f"{i}. {contrib.get('name', 'Unknown')} (@{contrib.get('username', 'unknown')})")
        print(f"   URL: {contrib.get('url')}")
        print(f"   Source: {contrib.get('source', 'unknown')}")
        print()
    
    print("=" * 70)
    
    # Verify we found the expected contributors
    usernames = {c.get('username', '').lower() for c in contributors}
    expected = {'jgarciab', 'modhurita', 'j535d165', 'qubixes'}
    
    print()
    print("Verification:")
    print(f"Expected contributors: {expected}")
    print(f"Found contributors: {usernames}")
    print()
    
    found_all = expected.issubset(usernames)
    if found_all:
        print("✅ All expected contributors found!")
    else:
        missing = expected - usernames
        print(f"❌ Missing contributors: {missing}")
    
    print()
    return found_all


def test_with_codemeta_generator():
    """Test with the full Codemeta generator."""
    from src.generator import CodemetaGenerator
    
    print("\n" + "=" * 70)
    print("Testing with Full Codemeta Generator")
    print("=" * 70)
    print()
    
    generator = CodemetaGenerator()
    
    repo_url = "https://github.com/sodascience/artscraper"
    print(f"Generating Codemeta for: {repo_url}")
    print()
    
    try:
        codemeta = generator.generate(repo_url)
        
        if 'contributor' in codemeta:
            contributors = codemeta['contributor']
            if not isinstance(contributors, list):
                contributors = [contributors]
            
            print(f"Found {len(contributors)} contributors in Codemeta:")
            print()
            
            for i, contrib in enumerate(contributors, 1):
                name = contrib.get('name', 'Unknown')
                email = contrib.get('email', 'N/A')
                print(f"{i}. {name}")
                print(f"   Email: {email}")
                if 'affiliation' in contrib:
                    aff = contrib['affiliation']
                    print(f"   Affiliation: {aff.get('name')}")
                print()
            
            print("✅ Contributors successfully extracted!")
            return True
        else:
            print("❌ No contributors found in Codemeta")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print()
    
    # Test the scraper
    test1_passed = test_contributors_scraper()
    
    # Test with full generator
    test2_passed = test_with_codemeta_generator()
    
    print()
    if test1_passed and test2_passed:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("⚠️  Some tests did not pass")
        sys.exit(1)
