#!/usr/bin/env python3
"""
Test script to verify author data is included in the final Codemeta output.
"""

import sys
import json
sys.path.insert(0, '/home/ubuntu/sshoc-nl-codemeta-generator')

from src.core import Config
from src.codemeta_generator import CodemetaGenerator

# Test with a repository
repo_url = "https://github.com/sodascience/kansenkaart_preprocessing"

print("=" * 80)
print("Testing Codemeta Generation with Author Data")
print("=" * 80)
print(f"\nRepository: {repo_url}\n")

try:
    # Create config
    config = Config(
        repo_url=repo_url,
        output_path="/tmp/codemeta_test.json",
        use_cache=False,
    )
    
    # Generate codemeta
    generator = CodemetaGenerator(config)
    codemeta = generator.generate()
    
    print("✓ Successfully generated Codemeta:\n")
    print(json.dumps(codemeta, indent=2))
    
    # Check if author data is present
    if "author" in codemeta:
        print(f"\n✓ Author data included: {len(codemeta['author'])} author(s) found")
        for author in codemeta['author']:
            name = f"{author.get('givenName', '')} {author.get('familyName', '')}"
            print(f"  - {name}")
    else:
        print("\n✗ No author data found in codemeta")
        
except Exception as e:
    print(f"✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
