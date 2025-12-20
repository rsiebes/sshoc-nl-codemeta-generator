#!/usr/bin/env python3
"""
Debug script to analyze GitHub contributors graph page
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def debug_contributors_graph():
    """Debug the contributors graph page."""
    url = "https://github.com/sodascience/artscraper/graphs/contributors"
    
    print("=" * 70)
    print(f"Analyzing: {url}")
    print("=" * 70)
    print()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Look for all links
    print("1. All links on the page:")
    print("-" * 70)
    all_links = soup.find_all('a', href=True)
    print(f"Total links: {len(all_links)}")
    
    # Filter to user profile links
    user_links = []
    for link in all_links:
        href = link.get('href', '')
        if href.startswith('/') and href.count('/') == 1 and not href.startswith('/login') and not href.startswith('/signup'):
            user_links.append(link)
    
    print(f"User profile links: {len(user_links)}")
    for i, link in enumerate(user_links[:15]):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        print(f"  {i+1}. href={href}, text='{text}'")
    print()
    
    # Look for text content mentioning contributors
    print("2. Text content analysis:")
    print("-" * 70)
    text = soup.get_text()
    lines = text.split('\n')
    
    # Find lines with usernames
    username_pattern = r'[a-zA-Z0-9_-]+'
    interesting_lines = []
    for line in lines:
        line = line.strip()
        if len(line) > 5 and len(line) < 100:
            # Check if line contains what looks like a username followed by a number
            if re.search(r'[a-zA-Z0-9_-]+\s+\d+', line):
                interesting_lines.append(line)
    
    print(f"Found {len(interesting_lines)} lines with username-number patterns:")
    for i, line in enumerate(interesting_lines[:20]):
        print(f"  {i+1}. {line}")
    print()
    
    # Look for data in script tags
    print("3. Script tags with JSON data:")
    print("-" * 70)
    scripts = soup.find_all('script', type='application/json')
    print(f"Found {len(scripts)} JSON script tags")
    
    for i, script in enumerate(scripts[:3]):
        content = script.string
        if content:
            try:
                data = json.loads(content)
                print(f"\nScript {i+1} keys: {list(data.keys()) if isinstance(data, dict) else 'array'}")
                
                # Look for contributor-related data
                json_str = json.dumps(data)
                if 'contributor' in json_str.lower() or 'jgarciab' in json_str.lower():
                    print(f"  Contains contributor data!")
                    print(f"  First 500 chars: {json_str[:500]}")
            except:
                pass
    print()
    
    # Look for specific usernames in HTML
    print("4. Searching for specific usernames in HTML:")
    print("-" * 70)
    usernames = ['jgarciab', 'modhurita', 'j535d165', 'qubixes', 'J535D165']
    for username in usernames:
        if username.lower() in response.text.lower():
            print(f"  ✓ Found '{username}' in page")
            # Find context
            pattern = re.compile(re.escape(username), re.IGNORECASE)
            matches = pattern.finditer(response.text)
            for match in list(matches)[:2]:
                start = max(0, match.start() - 50)
                end = min(len(response.text), match.end() + 50)
                context = response.text[start:end]
                print(f"    Context: ...{context}...")
        else:
            print(f"  ✗ '{username}' not found in page")
    print()
    
    # Look for data attributes
    print("5. Elements with data attributes:")
    print("-" * 70)
    elements_with_data = soup.find_all(attrs=lambda x: x and any(k.startswith('data-') for k in x.keys()))
    print(f"Found {len(elements_with_data)} elements with data attributes")
    
    for i, elem in enumerate(elements_with_data[:10]):
        data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
        if data_attrs:
            print(f"  {i+1}. {elem.name}: {data_attrs}")
    print()
    
    # Save full HTML for manual inspection
    with open('/tmp/contributors_graph.html', 'w') as f:
        f.write(soup.prettify())
    print("Full HTML saved to /tmp/contributors_graph.html")

if __name__ == '__main__':
    debug_contributors_graph()
