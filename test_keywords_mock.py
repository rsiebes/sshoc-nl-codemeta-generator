#!/usr/bin/env python3
"""
Mock test for keywords extraction - demonstrates output without API quota limits.

This test shows what the keywords submodule produces with sample data.
"""

from src.submodules.keywords import KeywordsSubmodule
from src.core import get_logger
from src.helpers.gemini_schemas import Keyword

logger = get_logger(__name__)

# Mock keywords data for demonstration
MOCK_KEYWORDS = {
    "https://github.com/jrvosse/amalgame": [
        Keyword(name="Ontology Alignment", context_clues="Core functionality for aligning ontologies and vocabularies"),
        Keyword(name="Semantic Web", context_clues="Uses RDF and semantic web technologies"),
        Keyword(name="SPARQL", context_clues="Queries semantic data using SPARQL endpoints"),
        Keyword(name="Linked Data", context_clues="Works with linked data vocabularies"),
        Keyword(name="Python", context_clues="Primary implementation language"),
        Keyword(name="Web Interface", context_clues="Provides web-based UI for alignment tasks"),
        Keyword(name="Vocabulary Mapping", context_clues="Maps between different vocabularies"),
        Keyword(name="Data Integration", context_clues="Integrates data from multiple sources"),
        Keyword(name="Knowledge Graphs", context_clues="Manages and aligns knowledge graphs"),
        Keyword(name="Interoperability", context_clues="Enables semantic interoperability between systems"),
    ],
    "https://github.com/sodascience/osmenrich": [
        Keyword(name="OpenStreetMap", context_clues="Primary data source for enrichment"),
        Keyword(name="Geospatial Data", context_clues="Works with geographic and spatial data"),
        Keyword(name="Data Enrichment", context_clues="Enriches datasets with OSM features"),
        Keyword(name="Python", context_clues="Implementation language"),
        Keyword(name="GIS", context_clues="Geographic Information Systems support"),
        Keyword(name="Spatial Analysis", context_clues="Performs spatial analysis operations"),
        Keyword(name="Data Processing", context_clues="Processes and transforms spatial data"),
        Keyword(name="API Integration", context_clues="Integrates with OSM APIs"),
        Keyword(name="Location Data", context_clues="Handles location-based information"),
        Keyword(name="Data Science", context_clues="Used in data science workflows"),
    ],
    "https://github.com/sodascience/metasyn": [
        Keyword(name="Synthetic Data", context_clues="Generates synthetic datasets"),
        Keyword(name="Privacy Preservation", context_clues="Protects privacy through data synthesis"),
        Keyword(name="Data Generation", context_clues="Creates realistic synthetic data"),
        Keyword(name="Python", context_clues="Primary implementation language"),
        Keyword(name="Machine Learning", context_clues="Uses ML techniques for data synthesis"),
        Keyword(name="Statistical Methods", context_clues="Applies statistical approaches"),
        Keyword(name="Data Anonymization", context_clues="Anonymizes sensitive information"),
        Keyword(name="Research Data", context_clues="Designed for research data protection"),
        Keyword(name="Data Science", context_clues="Supports data science research"),
        Keyword(name="Differential Privacy", context_clues="Implements differential privacy concepts"),
    ],
}


def test_keywords_extraction_mock():
    """Test keywords extraction with mock data."""

    print("\n" + "=" * 80)
    print("Keywords Extraction Test - Mock Data Demonstration")
    print("=" * 80 + "\n")

    test_repos = [
        {
            "name": "amalgame",
            "url": "https://github.com/jrvosse/amalgame",
            "description": "Alignment tool for ontologies/vocabularies",
        },
        {
            "name": "osmenrich",
            "url": "https://github.com/sodascience/osmenrich",
            "description": "Enriches spatial data with OpenStreetMap features",
        },
        {
            "name": "metasyn",
            "url": "https://github.com/sodascience/metasyn",
            "description": "Generates synthetic data for privacy-preserving research",
        },
    ]

    total_keywords = 0
    successful_extractions = 0

    for repo in test_repos:
        print(f"Repository: {repo['name']}")
        print(f"URL: {repo['url']}")
        print(f"Description: {repo['description']}")
        print("-" * 80)

        # Create repo_data structure
        repo_data = {
            "data": {
                "name": repo["name"],
                "html_url": repo["url"],
            }
        }

        # Get mock keywords
        keywords_objects = MOCK_KEYWORDS.get(repo["url"], [])

        if keywords_objects:
            # Extract only keyword names (as the submodule would do)
            keywords = [kw.name for kw in keywords_objects]

            print(f"✓ Successfully extracted {len(keywords)} keywords:")
            print()

            for i, keyword in enumerate(keywords, 1):
                # Get the context clues from the mock data
                context = next(
                    (kw.context_clues for kw in keywords_objects if kw.name == keyword),
                    "",
                )
                print(f"  {i:2d}. {keyword:25s} | {context}")

            total_keywords += len(keywords)
            successful_extractions += 1
        else:
            print(f"✗ No keywords found for {repo['name']}")

        print()

    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Total repositories tested: {len(test_repos)}")
    print(f"Successful extractions: {successful_extractions}")
    print(f"Total keywords extracted: {total_keywords}")
    print(f"Average keywords per repository: {total_keywords / len(test_repos):.1f}")
    print()

    # Show Codemeta output format
    print("=" * 80)
    print("Codemeta JSON Output Format")
    print("=" * 80)
    print()

    import json

    codemeta_example = {
        "name": "amalgame",
        "description": "Alignment tool for ontologies/vocabularies",
        "url": "https://github.com/jrvosse/amalgame",
        "keywords": [kw.name for kw in MOCK_KEYWORDS["https://github.com/jrvosse/amalgame"]],
    }

    print(json.dumps(codemeta_example, indent=2))
    print()


if __name__ == "__main__":
    test_keywords_extraction_mock()
