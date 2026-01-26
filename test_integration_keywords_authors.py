#!/usr/bin/env python3
"""Comprehensive integration test for keywords and authors in CodeMeta output."""

import sys
import json
import os
from dotenv import load_dotenv

sys.path.insert(0, '.')

# Load environment variables from .env file
load_dotenv()

from src.submodules.manager import SubmoduleManager


def test_integration_amalgame():
    """Test keywords and authors integration for amalgame repository."""
    
    repo_url = "https://github.com/jrvosse/amalgame"
    
    print("=" * 80)
    print("Integration Test: Keywords and Authors in CodeMeta")
    print("=" * 80)
    print(f"\nRepository: {repo_url}\n")
    
    # Prepare repository data
    repo_data = {
        "url": repo_url,
        "data": {
            "html_url": repo_url,
            "name": "amalgame",
            "description": "Alignment tool for ontologies and vocabularies"
        }
    }
    
    # Create and configure manager
    manager = SubmoduleManager()
    manager.register_ai_extraction_submodules(repo_data)
    
    # Execute all submodules
    print("Executing submodules...")
    print("-" * 80)
    codemeta_data = manager.execute_all()
    
    # Display status
    print("\nSubmodule Execution Status:")
    print("-" * 80)
    status = manager.get_status()
    print(f"Total submodules: {status['total_submodules']}")
    print(f"Properties extracted: {status['total_extracted']}")
    print(f"Total execution time: {status['total_time']:.3f}s\n")
    
    for submodule_status in status["submodules"]:
        status_icon = "✓" if submodule_status["extracted"] else "✗"
        print(f"  {status_icon} {submodule_status['property']}: {submodule_status['extraction_time']:.3f}s")
    
    # Display extracted data
    print("\n" + "=" * 80)
    print("Extracted CodeMeta Properties:")
    print("=" * 80)
    
    # Check keywords
    if 'keywords' in codemeta_data:
        keywords = codemeta_data['keywords']
        print(f"\n✓ Keywords ({len(keywords)} items):")
        for i, kw in enumerate(keywords[:3], 1):
            print(f"  {i}. {kw.get('name')} → {kw.get('url')}")
        if len(keywords) > 3:
            print(f"  ... and {len(keywords) - 3} more")
    else:
        print("\n✗ Keywords: NOT FOUND")
    
    # Check authors
    if 'author' in codemeta_data:
        authors = codemeta_data['author']
        print(f"\n✓ Authors ({len(authors)} items):")
        for i, author in enumerate(authors, 1):
            name = author.get('name', 'Unknown')
            orcid = author.get('@id', 'No ORCID')
            affiliation = author.get('affiliation', {}).get('name', 'Unknown')
            print(f"  {i}. {name}")
            print(f"     ORCID: {orcid}")
            print(f"     Affiliation: {affiliation}")
    else:
        print("\n✗ Authors: NOT FOUND")
    
    # Display full JSON
    print("\n" + "=" * 80)
    print("Full CodeMeta JSON Output:")
    print("=" * 80)
    
    full_codemeta = {
        "@context": "https://w3id.org/codemeta/3.1",
        "@type": "SoftwareSourceCode",
        "name": repo_data["data"]["name"],
        "description": repo_data["data"]["description"],
        "url": repo_url,
    }
    full_codemeta.update(codemeta_data)
    
    print(json.dumps(full_codemeta, indent=2))
    
    # Verification
    print("\n" + "=" * 80)
    print("Verification Results:")
    print("=" * 80)
    
    has_keywords = 'keywords' in codemeta_data and len(codemeta_data['keywords']) > 0
    has_authors = 'author' in codemeta_data and len(codemeta_data['author']) > 0
    
    print(f"✓ Keywords present: {has_keywords}")
    print(f"✓ Authors present: {has_authors}")
    print(f"✓ Integration successful: {has_keywords and has_authors}")
    
    return has_keywords and has_authors


def test_integration_osmenrich():
    """Test keywords and authors integration for osmenrich repository."""
    
    repo_url = "https://github.com/sodascience/osmenrich"
    
    print("\n\n" + "=" * 80)
    print("Integration Test: Keywords and Authors in CodeMeta")
    print("=" * 80)
    print(f"\nRepository: {repo_url}\n")
    
    # Prepare repository data
    repo_data = {
        "url": repo_url,
        "data": {
            "html_url": repo_url,
            "name": "osmenrich",
            "description": "osmenrich"
        }
    }
    
    # Create and configure manager
    manager = SubmoduleManager()
    manager.register_ai_extraction_submodules(repo_data)
    
    # Execute all submodules
    print("Executing submodules...")
    print("-" * 80)
    codemeta_data = manager.execute_all()
    
    # Display status
    print("\nSubmodule Execution Status:")
    print("-" * 80)
    status = manager.get_status()
    print(f"Total submodules: {status['total_submodules']}")
    print(f"Properties extracted: {status['total_extracted']}")
    print(f"Total execution time: {status['total_time']:.3f}s\n")
    
    for submodule_status in status["submodules"]:
        status_icon = "✓" if submodule_status["extracted"] else "✗"
        print(f"  {status_icon} {submodule_status['property']}: {submodule_status['extraction_time']:.3f}s")
    
    # Display extracted data
    print("\n" + "=" * 80)
    print("Extracted CodeMeta Properties:")
    print("=" * 80)
    
    # Check keywords
    if 'keywords' in codemeta_data:
        keywords = codemeta_data['keywords']
        print(f"\n✓ Keywords ({len(keywords)} items):")
        for i, kw in enumerate(keywords[:3], 1):
            print(f"  {i}. {kw.get('name')} → {kw.get('url')}")
        if len(keywords) > 3:
            print(f"  ... and {len(keywords) - 3} more")
    else:
        print("\n✗ Keywords: NOT FOUND")
    
    # Check authors
    if 'author' in codemeta_data:
        authors = codemeta_data['author']
        print(f"\n✓ Authors ({len(authors)} items):")
        for i, author in enumerate(authors, 1):
            name = author.get('name', 'Unknown')
            orcid = author.get('@id', 'No ORCID')
            affiliation = author.get('affiliation', {}).get('name', 'Unknown')
            print(f"  {i}. {name}")
            print(f"     ORCID: {orcid}")
            print(f"     Affiliation: {affiliation}")
    else:
        print("\n✗ Authors: NOT FOUND")
    
    # Display full JSON
    print("\n" + "=" * 80)
    print("Full CodeMeta JSON Output:")
    print("=" * 80)
    
    full_codemeta = {
        "@context": "https://w3id.org/codemeta/3.1",
        "@type": "SoftwareSourceCode",
        "name": repo_data["data"]["name"],
        "description": repo_data["data"]["description"],
        "url": repo_url,
    }
    full_codemeta.update(codemeta_data)
    
    print(json.dumps(full_codemeta, indent=2))
    
    # Verification
    print("\n" + "=" * 80)
    print("Verification Results:")
    print("=" * 80)
    
    has_keywords = 'keywords' in codemeta_data and len(codemeta_data['keywords']) > 0
    has_authors = 'author' in codemeta_data and len(codemeta_data['author']) > 0
    
    print(f"✓ Keywords present: {has_keywords}")
    print(f"✓ Authors present: {has_authors}")
    print(f"✓ Integration successful: {has_keywords and has_authors}")
    
    return has_keywords and has_authors


if __name__ == "__main__":
    result1 = test_integration_amalgame()
    result2 = test_integration_osmenrich()
    
    print("\n\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"amalgame integration: {'✓ PASS' if result1 else '✗ FAIL'}")
    print(f"osmenrich integration: {'✓ PASS' if result2 else '✗ FAIL'}")
    print(f"Overall: {'✓ ALL TESTS PASSED' if result1 and result2 else '✗ SOME TESTS FAILED'}")
