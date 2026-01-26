"""Wikidata enrichment for keywords."""

import json
from typing import Optional

import requests

from src.core import get_logger

logger = get_logger(__name__)


def fetch_wikidata_for_keyword(keyword: str) -> Optional[str]:
    """
    Fetch Wikidata information for a keyword.

    This function searches Wikidata for entities matching the keyword and returns
    the full JSON response if results are found, or an empty string if not.

    Args:
        keyword: The keyword to search for in Wikidata

    Returns:
        JSON string with Wikidata results if found, empty string if no results,
        None if there was an error

    Example:
        >>> result = fetch_wikidata_for_keyword("Python")
        >>> if result:
        ...     data = json.loads(result)
        ...     print(data['search'])
    """
    try:
        # Construct the Wikidata API URL
        url = "https://www.wikidata.org/w/api.php"
        params = {
            "action": "wbsearchentities",
            "search": keyword,
            "language": "en",
            "format": "json",
        }

        logger.debug(f"Fetching Wikidata for keyword: {keyword}")

        # Make the request with User-Agent header
        headers = {
            "User-Agent": "SSHOC-CodeMeta-Generator/1.0 (+https://github.com/rsiebes/sshoc-nl-codemeta-generator)"
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        # Check if search results are empty
        if not data.get("search") or len(data.get("search", [])) == 0:
            logger.debug(f"No Wikidata results found for keyword: {keyword}")
            return ""

        # Return the full JSON string
        logger.info(f"Found {len(data['search'])} Wikidata results for keyword: {keyword}")
        return json.dumps(data)

    except requests.exceptions.Timeout:
        logger.warning(f"Timeout fetching Wikidata for keyword: {keyword}")
        return None
    except requests.exceptions.RequestException as e:
        logger.warning(f"Error fetching Wikidata for keyword {keyword}: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON response from Wikidata for keyword {keyword}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching Wikidata for keyword {keyword}: {str(e)}")
        return None


def enrich_keywords_with_wikidata(keywords: list) -> dict:
    """
    Enrich a list of keywords with Wikidata information.

    Args:
        keywords: List of keyword strings

    Returns:
        Dictionary mapping keywords to their Wikidata results

    Example:
        >>> keywords = ["Python", "Machine Learning", "Data Science"]
        >>> enriched = enrich_keywords_with_wikidata(keywords)
        >>> for keyword, wikidata in enriched.items():
        ...     if wikidata:
        ...         print(f"{keyword}: Found in Wikidata")
        ...     else:
        ...         print(f"{keyword}: Not found in Wikidata")
    """
    enriched = {}

    for keyword in keywords:
        result = fetch_wikidata_for_keyword(keyword)
        enriched[keyword] = result

    return enriched
