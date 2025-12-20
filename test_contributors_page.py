#!/usr/bin/env python3
"""
Test script to analyze GitHub contributors page structure
"""

import requests
from bs4 import BeautifulSoup
import json

def fetch_contributors_page(owner, repo):
    """Fetch and analyze the GitHub contributors page."""
    url = f"https://github.com/{owner}/{repo}/graphs/contributors"
    
    print(f"Fetching: {url}")
    print("=" * 70)
    print()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for different patterns
        print("1. Looking for data attributes:")
        print("-" * 70)
        
        # Find all elements with data-hovercard-type="user"
        user_hovers = soup.find_all(attrs={'data-hovercard-type': 'user'})
        print(f"Found {len(user_hovers)} elements with data-hovercard-type='user'")
        for i, elem in enumerate(user_hovers[:5]):
            print(f"  {i+1}. {elem}")
        print()
        
        # Find all links to user profiles
        print("2. Looking for user profile links:")
        print("-" * 70)
        user_links = soup.find_all('a', href=lambda x: x and '/graphs/contributors' not in x and x.startswith('/'))
        print(f"Found {len(user_links)} potential user links")
        
        # Filter to likely user links
        user_profile_links = []
        for link in user_links:
            href = link.get('href', '')
            if href.startswith('/') and href.count('/') == 1:  # /username format
                user_profile_links.append(link)
        
        print(f"Filtered to {len(user_profile_links)} user profile links")
        for i, link in enumerate(user_profile_links[:10]):
            print(f"  {i+1}. href={link.get('href')}, text={link.get_text(strip=True)}")
        print()
        
        # Look for table rows or list items
        print("3. Looking for table structures:")
        print("-" * 70)
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        if tables:
            for i, table in enumerate(tables[:1]):
                print(f"Table {i+1}:")
                rows = table.find_all('tr')
                print(f"  Rows: {len(rows)}")
                for j, row in enumerate(rows[:3]):
                    print(f"    Row {j+1}: {row}")
        print()
        
        # Look for list items
        print("4. Looking for list structures:")
        print("-" * 70)
        lists = soup.find_all(['ul', 'ol'])
        print(f"Found {len(lists)} lists")
        
        # Look for divs with specific classes
        print("5. Looking for div structures:")
        print("-" * 70)
        divs = soup.find_all('div', class_=lambda x: x and ('contributor' in x.lower() or 'user' in x.lower()))
        print(f"Found {len(divs)} divs with contributor/user classes")
        for i, div in enumerate(divs[:5]):
            print(f"  {i+1}. classes={div.get('class')}")
        print()
        
        # Look for script tags with JSON data
        print("6. Looking for JSON data in scripts:")
        print("-" * 70)
        scripts = soup.find_all('script', type='application/json')
        print(f"Found {len(scripts)} JSON script tags")
        
        # Look for data in any script
        scripts_all = soup.find_all('script')
        print(f"Found {len(scripts_all)} total script tags")
        
        for i, script in enumerate(scripts_all[:3]):
            content = script.string
            if content:
                print(f"Script {i+1} (first 200 chars): {content[:200]}")
        print()
        
        # Look for specific GitHub patterns
        print("7. Looking for GitHub-specific patterns:")
        print("-" * 70)
        
        # Check for data in data attributes
        all_with_data = soup.find_all(attrs={'data-filterable-for': True})
        print(f"Found {len(all_with_data)} elements with data-filterable-for")
        
        # Look for avatar containers
        avatars = soup.find_all(attrs={'class': lambda x: x and 'avatar' in x.lower()})
        print(f"Found {len(avatars)} avatar elements")
        for i, avatar in enumerate(avatars[:5]):
            print(f"  {i+1}. {avatar}")
        print()
        
        # Print full HTML of first 5000 chars
        print("8. Full HTML (first 3000 chars):")
        print("-" * 70)
        print(soup.prettify()[:3000])
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # Test with artscraper
    print("\n" + "=" * 70)
    print("Analyzing GitHub Contributors Page Structure")
    print("=" * 70)
    print()
    
    fetch_contributors_page("sodascience", "artscraper")
