"""Gemini-based author enricher to add ORCID IDs and affiliations to author data."""

import json
import os
from typing import Optional

from dotenv import load_dotenv
from google import genai

from src.core import get_logger

logger = get_logger(__name__)

# Load environment variables
load_dotenv()


def enrich_authors_with_gemini(authors_json: str, repo_url: str) -> Optional[str]:
    """
    Enrich author information with ORCID IDs and affiliations using Gemini.

    Takes author data extracted from GitHub commits and uses Gemini to:
    1. Find ORCID IDs for each author
    2. Look up their ORCID profile to find current institutional affiliation
    3. Find DBpedia URIs for the institutions
    4. Return valid CodeMeta 3.1 JSON-LD representation

    Args:
        authors_json: JSON string containing author information from GitHub commits
        repo_url: The GitHub repository URL for additional context

    Returns:
        JSON-LD string in CodeMeta 3.1 format with enriched author data, or None on error

    Example:
        >>> authors_json = '''
        ... {
        ...   "authors": [
        ...     {"name": "John Doe", "email": "john@example.com", "login": "johndoe"}
        ...   ]
        ... }
        ... '''
        >>> enriched = enrich_authors_with_gemini(authors_json, "https://github.com/user/repo")
        >>> print(enriched)
        {
            "author": [
                {
                    "@type": "Person",
                    "name": "John Doe",
                    "email": "john@example.com",
                    "@id": "https://orcid.org/0000-0000-0000-0000",
                    "affiliation": {
                        "@type": "Organization",
                        "name": "Example University",
                        "@id": "http://dbpedia.org/resource/Example_University"
                    }
                }
            ]
        }
    """
    try:
        api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        if not api_key:
            logger.error("GOOGLE_GEMINI_API_KEY environment variable not set")
            return None

        client = genai.Client(api_key=api_key)

        logger.info(f"GEMINI AUTHOR ENRICHMENT: Processing authors for {repo_url}")

        # Build the prompt
        system_instruction = """You are a metadata enrichment expert specializing in CodeMeta 3.1 standard.
Your task is to enrich author information with ORCID IDs and institutional affiliations.

Guidelines:
1. For each author, find their ORCID iD if available
2. Look up the ORCID profile to find their current institutional affiliation
3. Use the affiliation information from the ORCID profile, not just the email domain
4. Provide the official DBpedia URI for the institution (e.g., http://dbpedia.org/resource/University_Name)
5. If information cannot be found with high confidence, omit that field rather than guessing
6. Return valid JSON-LD following the CodeMeta 3.1 schema

Output format must be a valid JSON object with an "author" array containing Person objects."""

        user_prompt = f"""Given the following author information extracted from GitHub commits for the repository {repo_url}:

{authors_json}

Please enrich this data by:
1. Finding ORCID iDs for each author (use @id field with format: https://orcid.org/XXXX-XXXX-XXXX-XXXX)
2. Looking up each author's ORCID profile to find their current institutional affiliation
3. Finding the official DBpedia URI for the institution based on the ORCID profile information
4. Return the result as valid CodeMeta 3.1 JSON-LD

IMPORTANT: The affiliation should be based on the ORCID profile information, not inferred from email domains.

The output should be a JSON object with an "author" array where each author has:
- @type: "Person"
- name: (from input)
- email: (from input, if available)
- @id: (ORCID URL, if found)
- affiliation: object with @type, name, and @id (DBpedia URI) - determined from ORCID profile

Only include fields where you have high confidence in the information."""

        logger.debug(f"Sending prompt to Gemini for author enrichment")

        # Call Gemini with structured output
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0,
            ),
            contents=user_prompt,
        )

        if not response or not response.text:
            logger.error("No response received from Gemini")
            return None

        # Parse and validate the response
        try:
            result = json.loads(response.text)
            logger.info(f"Successfully enriched authors with Gemini")
            logger.debug(f"Enriched authors: {json.dumps(result, indent=2)}")
            return json.dumps(result, indent=2)
        except json.JSONDecodeError as e:
            logger.error(f"Gemini returned invalid JSON: {str(e)}")
            logger.debug(f"Gemini response: {response.text}")
            return None

    except Exception as e:
        logger.error(f"Error enriching authors with Gemini: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return None
