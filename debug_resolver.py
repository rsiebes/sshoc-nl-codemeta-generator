#!/usr/bin/env python3
"""
Detailed debug script for organization URL resolver
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.organization_url_resolver import OrganizationURLResolver
import requests


def debug_wikidata_lookup(org_name):
    """Debug Wikidata lookup."""
    print(f"\n--- Testing Wikidata Lookup for '{org_name}' ---")
    
    try:
        sparql_query = f"""
        SELECT ?org ?orgLabel ?website WHERE {{
          ?org rdfs:label "{org_name}"@en ;
               wdt:P31 wd:Q43229 .  # instance of organization
          OPTIONAL {{ ?org wdt:P856 ?website . }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
        }}
        LIMIT 5
        """
        
        print(f"Query: {sparql_query[:100]}...")
        
        response = requests.get(
            "https://query.wikidata.org/sparql",
            params={
                'query': sparql_query,
                'format': 'json'
            },
            timeout=5
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {}).get('bindings', [])
            print(f"Results: {len(results)} found")
            
            for i, result in enumerate(results):
                print(f"  Result {i+1}:")
                if 'orgLabel' in result:
                    print(f"    Label: {result['orgLabel'].get('value')}")
                if 'website' in result:
                    print(f"    Website: {result['website'].get('value')}")
                if 'org' in result:
                    print(f"    Entity: {result['org'].get('value')}")
        else:
            print(f"Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"Exception: {e}")


def debug_duckduckgo_search(org_name):
    """Debug DuckDuckGo search."""
    print(f"\n--- Testing DuckDuckGo Search for '{org_name}' ---")
    
    try:
        search_query = f"{org_name} official website"
        print(f"Query: {search_query}")
        
        response = requests.get(
            "https://duckduckgo.com/api/v1/search",
            params={
                'q': search_query,
                'format': 'json'
            },
            timeout=5,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            results = data.get('Results', [])
            print(f"Results: {len(results)} found")
            for i, result in enumerate(results[:3]):
                print(f"  Result {i+1}:")
                print(f"    Title: {result.get('Title', 'N/A')[:50]}")
                print(f"    URL: {result.get('FirstURL', 'N/A')}")
            
            related = data.get('RelatedTopics', [])
            print(f"Related Topics: {len(related)} found")
            for i, topic in enumerate(related[:2]):
                print(f"  Topic {i+1}:")
                print(f"    Title: {topic.get('Text', 'N/A')[:50]}")
                print(f"    URL: {topic.get('FirstURL', 'N/A')}")
        else:
            print(f"Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"Exception: {e}")


def debug_resolver(org_name):
    """Debug the resolver."""
    print(f"\n--- Testing Resolver for '{org_name}' ---")
    
    resolver = OrganizationURLResolver()
    
    # Clear cache to force fresh lookup
    resolver.clear_cache()
    
    url = resolver.resolve_organization_url(org_name)
    print(f"Result: {url}")
    
    if url:
        print("✅ Resolved successfully")
    else:
        print("❌ Failed to resolve")


if __name__ == '__main__':
    org_names = [
        "Axel Springer",
        "Axel Springer SE",
        "Axel Springer AG",
    ]
    
    for org_name in org_names:
        print("\n" + "=" * 70)
        print(f"Debugging: {org_name}")
        print("=" * 70)
        
        debug_wikidata_lookup(org_name)
        debug_duckduckgo_search(org_name)
        debug_resolver(org_name)
