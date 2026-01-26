#!/usr/bin/env python3
"""
Auto-install dependencies and run keywords extraction test.

This script automatically installs all required dependencies before running.
Simply execute: python test_keywords_auto_install.py
"""

import subprocess
import sys
import os


def ensure_dependencies():
    """Automatically install dependencies if missing."""
    required_packages = [
        ("google.genai", "google-genai"),
        ("pydantic", "pydantic"),
        ("dotenv", "python-dotenv"),
        ("requests", "requests"),
    ]

    missing = []

    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)

    if missing:
        print("Installing missing dependencies:", ", ".join(missing))
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q"] + missing
        )
        print("✓ Dependencies installed!\n")


def main():
    """Main entry point."""
    # Ensure all dependencies are installed
    ensure_dependencies()

    # Now run the test
    from src.submodules.keywords import KeywordsSubmodule
    from src.core import get_logger

    logger = get_logger(__name__)

    # Test repositories
    test_repos = [
        {
            "name": "amalgame",
            "url": "https://github.com/jrvosse/amalgame",
        },
        {
            "name": "osmenrich",
            "url": "https://github.com/sodascience/osmenrich",
        },
        {
            "name": "metasyn",
            "url": "https://github.com/sodascience/metasyn",
        },
    ]

    print("\n" + "=" * 80)
    print("Testing Keywords Extraction with Gemini API")
    print("=" * 80 + "\n")

    for repo in test_repos:
        print(f"Testing repository: {repo['name']}")
        print(f"URL: {repo['url']}")
        print("-" * 80)

        # Create repo_data structure
        repo_data = {
            "data": {
                "name": repo["name"],
                "html_url": repo["url"],
            }
        }

        # Extract keywords
        submodule = KeywordsSubmodule(repo_data)
        keywords = submodule.run()

        if keywords:
            print(f"✓ Successfully extracted {len(keywords)} keywords:")
            for i, keyword in enumerate(keywords, 1):
                print(f"  {i}. {keyword}")
        else:
            print(f"✗ Failed to extract keywords")

        print(f"Extraction time: {submodule.extraction_time:.3f}s")
        print()


if __name__ == "__main__":
    main()
