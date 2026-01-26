"""Map organization names to DBpedia URIs."""

import os
from typing import Optional, Dict
from difflib import SequenceMatcher

from src.core import get_logger

logger = get_logger(__name__)

# Comprehensive mapping of organization names to DBpedia URIs
ORGANIZATION_MAPPINGS = {
    # Dutch Universities
    'Vrije Universiteit Amsterdam': 'http://dbpedia.org/resource/Vrije_Universiteit_Amsterdam',
    'VU': 'http://dbpedia.org/resource/Vrije_Universiteit_Amsterdam',
    'VU Amsterdam': 'http://dbpedia.org/resource/Vrije_Universiteit_Amsterdam',
    'University of Amsterdam': 'http://dbpedia.org/resource/University_of_Amsterdam',
    'UvA': 'http://dbpedia.org/resource/University_of_Amsterdam',
    'Utrecht University': 'http://dbpedia.org/resource/Utrecht_University',
    'UU': 'http://dbpedia.org/resource/Utrecht_University',
    'Delft University of Technology': 'http://dbpedia.org/resource/Delft_University_of_Technology',
    'TU Delft': 'http://dbpedia.org/resource/Delft_University_of_Technology',
    'University of Twente': 'http://dbpedia.org/resource/University_of_Twente',
    'University of Groningen': 'http://dbpedia.org/resource/University_of_Groningen',
    'RUG': 'http://dbpedia.org/resource/University_of_Groningen',
    'Leiden University': 'http://dbpedia.org/resource/Leiden_University',
    'Erasmus University Rotterdam': 'http://dbpedia.org/resource/Erasmus_University_Rotterdam',
    'Radboud University': 'http://dbpedia.org/resource/Radboud_University',
    'University of Maastricht': 'http://dbpedia.org/resource/Maastricht_University',
    'Wageningen University': 'http://dbpedia.org/resource/Wageningen_University',
    
    # Research Institutes
    'Netherlands eScience Center': 'http://dbpedia.org/resource/Netherlands_eScience_Center',
    'NLeSC': 'http://dbpedia.org/resource/Netherlands_eScience_Center',
    'CWI': 'http://dbpedia.org/resource/Centrum_Wiskunde_%26_Informatica',
    'Centrum Wiskunde & Informatica': 'http://dbpedia.org/resource/Centrum_Wiskunde_%26_Informatica',
    
    # International Organizations
    'University of Toronto': 'http://dbpedia.org/resource/University_of_Toronto',
    'Stanford University': 'http://dbpedia.org/resource/Stanford_University',
    'MIT': 'http://dbpedia.org/resource/Massachusetts_Institute_of_Technology',
    'Massachusetts Institute of Technology': 'http://dbpedia.org/resource/Massachusetts_Institute_of_Technology',
    'Harvard University': 'http://dbpedia.org/resource/Harvard_University',
    'Oxford University': 'http://dbpedia.org/resource/University_of_Oxford',
    'Cambridge University': 'http://dbpedia.org/resource/University_of_Cambridge',
    
    # German Organizations
    'Verbundzentrale des GBV (VZG)': 'http://dbpedia.org/resource/Verbundzentrale_des_GBV',
    'VZG': 'http://dbpedia.org/resource/Verbundzentrale_des_GBV',
    
    # Companies
    'motherduckdb': 'http://dbpedia.org/resource/DuckDB',
    'DuckDB': 'http://dbpedia.org/resource/DuckDB',
}


def find_best_match(org_name: str, threshold: float = 0.6) -> Optional[str]:
    """
    Find the best matching DBpedia URI for an organization name using fuzzy matching.

    Args:
        org_name: Organization name to match
        threshold: Minimum similarity score (0-1) for a match

    Returns:
        DBpedia URI if found, None otherwise
    """
    if not org_name:
        return None

    org_name_lower = org_name.lower().strip()

    # First, try exact match (case-insensitive)
    for key, uri in ORGANIZATION_MAPPINGS.items():
        if key.lower() == org_name_lower:
            logger.debug(f"Exact match found for '{org_name}': {uri}")
            return uri

    # Then, try fuzzy matching
    best_match = None
    best_score = threshold

    for key, uri in ORGANIZATION_MAPPINGS.items():
        score = SequenceMatcher(None, org_name_lower, key.lower()).ratio()
        if score > best_score:
            best_score = score
            best_match = uri

    if best_match:
        logger.debug(f"Fuzzy match found for '{org_name}' (score: {best_score:.2f}): {best_match}")
        return best_match

    logger.debug(f"No match found for organization '{org_name}'")
    return None


def map_organization_to_dbpedia(org_name: str) -> Optional[str]:
    """
    Map an organization name to a DBpedia URI.

    Args:
        org_name: Organization name (e.g., "Utrecht University")

    Returns:
        DBpedia URI (e.g., "http://dbpedia.org/resource/Utrecht_University"), or None if not found
    """
    try:
        if not org_name or not org_name.strip():
            return None

        # Try to find a match
        uri = find_best_match(org_name)
        return uri

    except Exception as e:
        logger.error(f"Error mapping organization '{org_name}' to DBpedia: {str(e)}")
        return None


def map_organizations_to_dbpedia(org_names: list) -> Dict[str, Optional[str]]:
    """
    Map multiple organization names to DBpedia URIs.

    Args:
        org_names: List of organization names

    Returns:
        Dictionary mapping organization names to DBpedia URIs
    """
    results = {}
    for org_name in org_names:
        if org_name:
            uri = map_organization_to_dbpedia(org_name)
            results[org_name] = uri
    return results


if __name__ == '__main__':
    # Test the function
    import sys
    sys.path.insert(0, '.')

    print("Testing DBpedia URI mapping...\n")

    test_orgs = [
        "Vrije Universiteit Amsterdam",
        "Utrecht University",
        "Delft University of Technology",
        "University of Twente",
        "Netherlands eScience Center",
        "Verbundzentrale des GBV (VZG)",
        "University of Toronto",
        "motherduckdb",
    ]

    for org in test_orgs:
        print(f"Organization: {org}")
        uri = map_organization_to_dbpedia(org)
        if uri:
            print(f"  DBpedia URI: {uri}")
        else:
            print(f"  Could not map to DBpedia")
        print()
