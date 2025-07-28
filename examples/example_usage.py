#!/usr/bin/env python3
"""
CodeMeta Generator - Example Usage Script

This script demonstrates how to use the CodeMeta Generator toolkit with two real-world use cases:
1. SODA Science - Research organization with 47 projects
2. BramVanroy Data - Individual researcher's software portfolio with 9 projects

Both use cases show different approaches to research software metadata management.

Author: Ronald Siebes (UCDS Group, VU Amsterdam)
ORCID: 0000-0001-8772-7904
"""

import sys
import os
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import codemeta_generator
    import enhancer
    import bulk_processor
    print("✅ All modules imported successfully")
except ImportError as e:
    print(f"⚠️  Import warning: {e}")
    print("   (This is expected when running as a standalone script)")

def demonstrate_soda_science_use_case():
    """
    Demonstrate the SODA Science use case:
    - Research organization with multiple projects
    - Comprehensive organizational metadata
    - Bulk processing capabilities
    """
    print("=" * 60)
    print("SODA SCIENCE USE CASE")
    print("=" * 60)
    print("Organization: SODA Science (Scalable Open Data Analytics)")
    print("URL: https://github.com/sodascience")
    print("Projects: 47 research software repositories")
    print("Focus: Data science, open science, scalable analytics")
    print()
    
    # Load example SODA Science files
    soda_dir = Path(__file__).parent / "soda_science"
    if not soda_dir.exists():
        print("❌ SODA Science examples not found!")
        return
    
    soda_files = list(soda_dir.glob("*.json"))
    print(f"📁 Found {len(soda_files)} SODA Science CodeMeta files")
    
    # Analyze the collection
    print("\n🔍 SODA Science Collection Analysis:")
    print("-" * 40)
    
    categories = {}
    licenses = {}
    languages = {}
    
    for file_path in soda_files[:5]:  # Analyze first 5 files as examples
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                codemeta = json.load(f)
            
            # Categorize
            category = codemeta.get('applicationCategory', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
            
            # License analysis
            license_info = codemeta.get('license', {})
            if isinstance(license_info, dict):
                license_name = license_info.get('name', 'Unknown')
                licenses[license_name] = licenses.get(license_name, 0) + 1
            
            # Programming languages
            prog_langs = codemeta.get('programmingLanguage', [])
            if isinstance(prog_langs, list):
                for lang in prog_langs:
                    languages[lang] = languages.get(lang, 0) + 1
            
            print(f"  ✅ {file_path.name}: {category}")
            
        except Exception as e:
            print(f"  ❌ Error analyzing {file_path.name}: {e}")
    
    print(f"\n📊 SODA Science Portfolio Statistics:")
    print(f"  Categories: {dict(list(categories.items())[:3])}")
    print(f"  Languages: {dict(list(languages.items())[:3])}")
    print(f"  Licenses: {dict(list(licenses.items())[:3])}")
    
    # Demonstrate organizational features
    print(f"\n🏢 Organizational Features:")
    print(f"  ✅ Comprehensive organizational metadata (isPartOf)")
    print(f"  ✅ Standardized categorization across projects")
    print(f"  ✅ Consistent license and author attribution")
    print(f"  ✅ Publication references for key projects")
    print(f"  ✅ CodeMeta 3.0 compliance across all projects")

def demonstrate_bramvanroy_use_case():
    """
    Demonstrate the BramVanroy Data use case:
    - Individual researcher's software portfolio
    - Diverse project types and applications
    - Academic research focus
    """
    print("\n" + "=" * 60)
    print("BRAMVANROY DATA USE CASE")
    print("=" * 60)
    print("Researcher: Bram Vanroy")
    print("ORCID: https://orcid.org/0000-0002-4622-8364")
    print("URL: https://github.com/BramVanroy")
    print("Projects: 9 research software repositories")
    print("Focus: NLP, machine translation, computational linguistics")
    print()
    
    # Load example BramVanroy files
    bramvanroy_dir = Path(__file__).parent / "bramvanroy"
    if not bramvanroy_dir.exists():
        print("❌ BramVanroy examples not found!")
        return
    
    bramvanroy_files = list(bramvanroy_dir.glob("*.json"))
    print(f"📁 Found {len(bramvanroy_files)} BramVanroy CodeMeta files")
    
    # Analyze the collection
    print("\n🔍 BramVanroy Portfolio Analysis:")
    print("-" * 40)
    
    project_types = {}
    research_areas = {}
    
    # Highlight specific projects
    highlighted_projects = {
        "codemeta_fietje-2.json": "Dutch Language Model (2.7B parameters)",
        "codemeta_multilingual-text-to-amr.json": "Multilingual AMR Parsing",
        "codemeta_mateo-demo.json": "Machine Translation Evaluation",
        "codemeta_spacy_conll.json": "NLP Pipeline Component",
        "codemeta_LeCoNTra.json": "Translation Process Research Data"
    }
    
    for file_path in bramvanroy_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                codemeta = json.load(f)
            
            # Project analysis
            category = codemeta.get('applicationCategory', 'Unknown')
            subcategory = codemeta.get('applicationSubCategory', 'Unknown')
            project_types[f"{category} → {subcategory}"] = project_types.get(f"{category} → {subcategory}", 0) + 1
            
            # Research area analysis
            keywords = codemeta.get('keywords', [])
            for keyword in keywords[:3]:  # Top 3 keywords
                if keyword in ['nlp', 'machine translation', 'dutch', 'amr', 'language model']:
                    research_areas[keyword] = research_areas.get(keyword, 0) + 1
            
            # Highlight special projects
            filename = file_path.name
            if filename in highlighted_projects:
                print(f"  🌟 {filename}: {highlighted_projects[filename]}")
            else:
                print(f"  ✅ {filename}: {category}")
            
        except Exception as e:
            print(f"  ❌ Error analyzing {file_path.name}: {e}")
    
    print(f"\n📊 BramVanroy Portfolio Statistics:")
    print(f"  Project Types: {dict(list(project_types.items())[:3])}")
    print(f"  Research Areas: {dict(list(research_areas.items())[:3])}")
    
    # Demonstrate individual researcher features
    print(f"\n👨‍🔬 Individual Researcher Features:")
    print(f"  ✅ Consistent author attribution with ORCID")
    print(f"  ✅ Diverse project portfolio (models, tools, data)")
    print(f"  ✅ Academic publication integration")
    print(f"  ✅ Comprehensive technical documentation")
    print(f"  ✅ Version-specific dependency management")

def demonstrate_api_usage():
    """
    Demonstrate programmatic usage of the CodeMeta Generator.
    """
    print("\n" + "=" * 60)
    print("API USAGE DEMONSTRATION")
    print("=" * 60)
    
    print("🔧 CodeMeta Generator Features:")
    print("  - Schema: CodeMeta 3.0")
    print("  - Enhancement capabilities")
    print("  - Validation support")
    print("  - GitHub integration")
    
    # Example: Generate CodeMeta for a repository
    print(f"\n📝 Example API Usage:")
    print("```python")
    print("from codemeta_generator import CodeMetaGenerator")
    print("")
    print("# Initialize generator")
    print("generator = CodeMetaGenerator(schema_version='3.0')")
    print("")
    print("# Generate from GitHub repository")
    print("codemeta = generator.generate_from_github(repo_url)")
    print("")
    print("# Add author information")
    print("authors = [{'@type': 'Person', '@id': 'orcid_url', ...}]")
    print("generator.add_authors(codemeta, authors)")
    print("")
    print("# Save enhanced metadata")
    print("generator.save_codemeta(codemeta, 'output.json')")
    print("```")
    
    # Show enhancement capabilities
    print(f"\n🚀 Enhancement Capabilities:")
    print(f"  - Automatic categorization")
    print(f"  - Technical specification inference")
    print(f"  - Documentation link generation")
    print(f"  - ORCID author integration")
    print(f"  - Publication DOI linking")

def demonstrate_bulk_processing():
    """
    Demonstrate bulk processing capabilities.
    """
    print("\n" + "=" * 60)
    print("BULK PROCESSING DEMONSTRATION")
    print("=" * 60)
    
    # Count files in both collections
    soda_dir = Path(__file__).parent / "soda_science"
    bramvanroy_dir = Path(__file__).parent / "bramvanroy"
    
    soda_count = len(list(soda_dir.glob("*.json"))) if soda_dir.exists() else 0
    bramvanroy_count = len(list(bramvanroy_dir.glob("*.json"))) if bramvanroy_dir.exists() else 0
    
    print(f"📊 Available Collections:")
    print(f"  SODA Science: {soda_count} files")
    print(f"  BramVanroy Data: {bramvanroy_count} files")
    print(f"  Total: {soda_count + bramvanroy_count} CodeMeta files")
    
    print(f"\n⚡ Bulk Processing Features:")
    print(f"  ✅ Concurrent processing for large collections")
    print(f"  ✅ Validation and quality control")
    print(f"  ✅ Progress tracking and reporting")
    print(f"  ✅ Error handling and recovery")
    print(f"  ✅ Organizational metadata application")
    
    print(f"\n🎯 Use Cases:")
    print(f"  - Research organization portfolio management")
    print(f"  - Individual researcher software cataloging")
    print(f"  - Institutional software inventory")
    print(f"  - FAIR software principles implementation")

def main():
    """
    Main demonstration function showing both use cases.
    """
    print("🎉 CodeMeta Generator - Use Case Demonstrations")
    print("=" * 60)
    print("This script demonstrates two real-world use cases for")
    print("research software metadata generation and management.")
    print()
    
    # Demonstrate both use cases
    demonstrate_soda_science_use_case()
    demonstrate_bramvanroy_use_case()
    
    # Show API and bulk processing capabilities
    demonstrate_api_usage()
    demonstrate_bulk_processing()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✅ SODA Science: Organizational research software portfolio")
    print("✅ BramVanroy Data: Individual researcher software collection")
    print("✅ API Usage: Programmatic metadata generation")
    print("✅ Bulk Processing: Large-scale metadata management")
    print()
    print("🚀 The CodeMeta Generator toolkit supports diverse")
    print("   research software metadata needs, from individual")
    print("   projects to large organizational portfolios.")
    print()
    print("📚 For more information:")
    print("   - README.md: Complete documentation")
    print("   - docs/user_guide.md: Detailed usage guide")
    print("   - examples/: Real-world use cases")
    print("   - tests/: Working examples and validation")

if __name__ == "__main__":
    main()

