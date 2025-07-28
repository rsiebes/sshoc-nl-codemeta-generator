#!/usr/bin/env python3
"""
Test script to demonstrate the CodeMeta Generator Python API
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from codemeta_generator import CodeMetaGenerator

def test_api():
    """Test the Python API directly."""
    print("Testing CodeMeta Generator Python API...")
    print("=" * 50)
    
    # Initialize generator
    generator = CodeMetaGenerator(schema_version="3.0")
    
    # Generate CodeMeta
    repo_url = "https://github.com/rsiebes/sshoc-nl-zotero"
    print(f"Generating CodeMeta for: {repo_url}")
    
    try:
        codemeta = generator.generate_from_github(repo_url)
        
        # Add author information (since we know this is Ronald's repo)
        authors = [
            {
                "@type": "Person",
                "@id": "https://orcid.org/0000-0001-8772-7904",
                "givenName": "Ronald",
                "familyName": "Siebes",
                "affiliation": {
                    "@type": "Organization",
                    "name": "VU Amsterdam",
                    "url": "https://www.vu.nl/"
                }
            }
        ]
        generator.add_authors(codemeta, authors)
        
        # Save the enhanced file
        output_file = "test_api_codemeta_sshoc.json"
        generator.save_codemeta(codemeta, output_file)
        
        # Validate
        warnings = generator.validate_codemeta(codemeta)
        if warnings:
            print("Validation warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        else:
            print("✅ Validation passed!")
        
        print(f"✅ Enhanced CodeMeta file generated: {output_file}")
        
        # Show some key fields
        print(f"\nGenerated metadata:")
        print(f"  Name: {codemeta.get('name')}")
        print(f"  Description: {codemeta.get('description')}")
        print(f"  Author: {codemeta.get('author', [{}])[0].get('givenName', 'N/A')} {codemeta.get('author', [{}])[0].get('familyName', 'N/A')}")
        print(f"  Programming Language: {codemeta.get('programmingLanguage')}")
        print(f"  Schema: {codemeta.get('@context')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api()

