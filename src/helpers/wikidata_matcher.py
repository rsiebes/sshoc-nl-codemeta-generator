"""Gemini-based Wikidata concept matching for keywords."""

import json
import os
from typing import Optional

from dotenv import load_dotenv
from google import genai

from src.core import get_logger
from src.helpers.wikidata_cache import cache_get, cache_set
from src.helpers.wikidata_matcher_schemas import ConceptMatch, ConceptMatchResult

logger = get_logger(__name__)

# Load environment variables from .env file
load_dotenv()


def match_keyword_to_wikidata_concept(
    keyword: str,
    wikidata_results: str,
    repo_url: str,
    repo_description: str = "",
) -> Optional[ConceptMatch]:
    """
    Use Gemini to match a keyword to the best Wikidata concept.

    This function analyzes the keyword, repository context, and available Wikidata
    results to select the single best matching concept URI. Results are cached
    to avoid redundant API calls. Cache is context-aware using repository URL.

    Args:
        keyword: The keyword to match
        wikidata_results: JSON string from Wikidata API containing search results
        repo_url: The repository URL for context
        repo_description: Optional repository description for additional context

    Returns:
        ConceptMatch object with the best matching Wikidata concept, or None if matching fails
    """
    try:
        # Check cache first (with repository context)
        cached_match = cache_get(keyword, repo_url)
        if cached_match:
            logger.debug(f"Using cached match for keyword: {keyword} (repo: {repo_url})")
            return ConceptMatch(**cached_match)

        # Parse Wikidata results
        try:
            wikidata_data = json.loads(wikidata_results)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in Wikidata results for keyword: {keyword}")
            return None

        # Check if there are any search results
        search_results = wikidata_data.get("search", [])
        if not search_results:
            logger.warning(f"No Wikidata results available for keyword: {keyword}")
            return None

        # Get API key from environment
        api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        if not api_key:
            logger.error("GOOGLE_GEMINI_API_KEY not found in environment variables")
            return None

        # Initialize Gemini client
        client = genai.Client(api_key=api_key)

        # Prepare the prompt for Gemini
        wikidata_options = json.dumps(search_results[:10], indent=2)  # Limit to top 10

        prompt = f"""Analyze the following information and select the SINGLE BEST matching Wikidata concept for the keyword.

Keyword: {keyword}
Repository URL: {repo_url}
Repository Description: {repo_description}

Available Wikidata Results:
{wikidata_options}

Your task:
1. Analyze each Wikidata result's label and description
2. Consider the repository context (URL and description)
3. Select the SINGLE BEST match that most accurately represents the keyword in this repository context
4. Provide the concept_uri, label, description, confidence level, and reasoning

Important:
- Return ONLY ONE match (the best one)
- The concept_uri should be in the format: http://www.wikidata.org/entity/Q[number]
- Confidence should be 'high', 'medium', or 'low'
- Consider the repository's domain when making the selection (e.g., if it's about ontologies, prefer semantic/knowledge-related concepts)

Return a JSON object with the structure:
{{
    "match": {{
        "keyword": "{keyword}",
        "concept_uri": "http://www.wikidata.org/entity/Q...",
        "label": "...",
        "description": "...",
        "confidence": "high|medium|low",
        "reasoning": "..."
    }}
}}"""

        logger.debug(f"Matching keyword '{keyword}' to Wikidata concept using Gemini (repo: {repo_url})")

        # Call Gemini API with structured output
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ConceptMatchResult,
            ),
        )

        # Parse the response
        if response and response.parsed:
            match = response.parsed.match
            logger.info(
                f"Successfully matched keyword '{keyword}' to Wikidata concept: {match.concept_uri} (repo: {repo_url})"
            )

            # Cache the result (with repository context)
            match_dict = {
                "keyword": match.keyword,
                "concept_uri": match.concept_uri,
                "label": match.label,
                "description": match.description,
                "confidence": match.confidence,
                "reasoning": match.reasoning,
            }
            cache_set(keyword, match_dict, repo_url)
            logger.debug(f"Cached match for keyword: {keyword} (repo: {repo_url})")

            return match
        else:
            logger.warning(f"No match returned from Gemini for keyword: {keyword}")
            return None

    except Exception as e:
        logger.error(f"Error matching keyword '{keyword}' to Wikidata concept: {str(e)}")
        return None


def match_keywords_to_wikidata_concepts(
    keywords_with_wikidata: dict,
    repo_url: str,
    repo_description: str = "",
) -> dict:
    """
    Match multiple keywords to their best Wikidata concepts.

    Args:
        keywords_with_wikidata: Dictionary mapping keywords to their Wikidata JSON results
        repo_url: The repository URL for context
        repo_description: Optional repository description for additional context

    Returns:
        Dictionary mapping keywords to their ConceptMatch objects

    Example:
        >>> keywords_with_wikidata = {
        ...     "Python": '{"search": [{"id": "Q28865", ...}]}',
        ...     "Machine Learning": '{"search": [{"id": "Q11019", ...}]}'
        ... }
        >>> matches = match_keywords_to_wikidata_concepts(
        ...     keywords_with_wikidata,
        ...     "https://github.com/example/repo",
        ...     "A Python ML library"
        ... )
        >>> for keyword, match in matches.items():
        ...     if match:
        ...         print(f"{keyword}: {match.concept_uri}")
    """
    matches = {}

    for keyword, wikidata_json in keywords_with_wikidata.items():
        if wikidata_json is None or wikidata_json == "":
            logger.debug(f"No Wikidata results for keyword: {keyword}")
            matches[keyword] = None
            continue

        match = match_keyword_to_wikidata_concept(
            keyword, wikidata_json, repo_url, repo_description
        )
        matches[keyword] = match

    return matches
