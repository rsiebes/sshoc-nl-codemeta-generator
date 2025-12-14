#!/usr/bin/env python3
"""
Codemeta Generator CLI

Command-line tool to generate Codemeta 3.1 metadata from GitHub repositories.

Usage:
    python codemeta_gen.py <github_repo_url> [options]

Examples:
    python codemeta_gen.py https://github.com/owner/repo
    python codemeta_gen.py https://github.com/owner/repo -o codemeta.json
    python codemeta_gen.py https://github.com/owner/repo --output my_codemeta.json
"""

import argparse
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.generator import CodemetaGenerator


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Generate Codemeta 3.1 metadata from GitHub repositories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://github.com/owner/repo
  %(prog)s https://github.com/owner/repo -o codemeta.json
  %(prog)s https://github.com/owner/repo --output my_codemeta.json

For more information, visit: https://codemeta.github.io/
        """
    )
    
    parser.add_argument(
        'repo_url',
        help='GitHub repository URL (e.g., https://github.com/owner/repo)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='codemeta.json',
        help='Output file path (default: codemeta.json)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0 (Codemeta 3.1)'
    )
    
    args = parser.parse_args()
    
    # Validate repository URL
    if not args.repo_url.startswith('http'):
        print(f"Error: Invalid repository URL: {args.repo_url}")
        print("URL must start with 'http://' or 'https://'")
        sys.exit(1)
    
    if 'github.com' not in args.repo_url:
        print(f"Error: Not a GitHub repository URL: {args.repo_url}")
        print("URL must contain 'github.com'")
        sys.exit(1)
    
    # Print header
    print("=" * 70)
    print("Codemeta 3.1 Generator")
    print("=" * 70)
    print()
    
    try:
        # Create generator
        generator = CodemetaGenerator()
        
        # Generate Codemeta
        generator.generate_to_file(args.repo_url, args.output)
        
        print()
        print("=" * 70)
        print("✅ Generation completed successfully!")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
