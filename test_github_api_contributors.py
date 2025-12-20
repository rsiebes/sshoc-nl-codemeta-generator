#!/usr/bin/env python3
"""
Test script to fetch contributors using GitHub API and alternative methods
"""

import requests
import json

def test_github_api(owner, repo):
    """Test GitHub REST API for contributors."""
    print("=" * 70)
    print("Testing GitHub REST API for Contributors")
    print("=" * 70)
    print()
    
    # GitHub API endpoint for contributors
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Mozilla/5.0'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} contributors")
            print()
            
            for i, contributor in enumerate(data[:5]):
                print(f"Contributor {i+1}:")
                print(f"  Login: {contributor.get('login')}")
                print(f"  Name: {contributor.get('name', 'N/A')}")
                print(f"  URL: {contributor.get('html_url')}")
                print(f"  Avatar: {contributor.get('avatar_url')}")
                print(f"  Contributions: {contributor.get('contributions')}")
                print()
        else:
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def test_github_graphql(owner, repo):
    """Test GitHub GraphQL API for contributors."""
    print("\n" + "=" * 70)
    print("Testing GitHub GraphQL API for Contributors")
    print("=" * 70)
    print()
    
    url = "https://api.github.com/graphql"
    
    query = f"""
    query {{
      repository(owner: "{owner}", name: "{repo}") {{
        defaultBranchRef {{
          target {{
            ... on Commit {{
              history(first: 100) {{
                edges {{
                  node {{
                    author {{
                      name
                      email
                      user {{
                        login
                        url
                        name
                      }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    """
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
    
    try:
        response = requests.post(
            url,
            json={'query': query},
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"GraphQL Errors: {data['errors']}")
            else:
                print(f"Response: {json.dumps(data, indent=2)[:1000]}")
        else:
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"Error: {e}")


def test_raw_github_page(owner, repo):
    """Test fetching raw GitHub page without JavaScript."""
    print("\n" + "=" * 70)
    print("Testing Raw GitHub Page (No JavaScript)")
    print("=" * 70)
    print()
    
    # Try the main repo page
    url = f"https://github.com/{owner}/{repo}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html,application/xhtml+xml'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        # Look for contributor mentions in HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for any mention of contributors
        text = soup.get_text()
        
        # Find lines mentioning contributors
        lines = text.split('\n')
        contributor_lines = [line for line in lines if 'contributor' in line.lower()]
        
        print(f"Found {len(contributor_lines)} lines mentioning 'contributor'")
        for i, line in enumerate(contributor_lines[:10]):
            print(f"  {i+1}. {line.strip()[:100]}")
        print()
        
        # Look for user links
        user_links = soup.find_all('a', href=lambda x: x and x.startswith(f'/{owner}'))
        print(f"Found {len(user_links)} links in {owner} namespace")
        for i, link in enumerate(user_links[:10]):
            print(f"  {i+1}. href={link.get('href')}, text={link.get_text(strip=True)[:50]}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    owner = "sodascience"
    repo = "artscraper"
    
    print()
    print("Testing Different Methods to Extract Contributors")
    print()
    
    test_github_api(owner, repo)
    test_github_graphql(owner, repo)
    test_raw_github_page(owner, repo)
