"""Gemini API integration for author metadata extraction."""

import json
import os
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from google import genai

from src.core import get_logger

logger = get_logger(__name__)

# Load environment variables from .env file
load_dotenv()


def extract_authors(repo_url: str) -> Optional[Dict[str, Any]]:
    """
    Extract author metadata from a GitHub repository using Google Gemini API.

    Uses CodeMeta 3.1 standard with structured output schema.

    Args:
        repo_url: The GitHub repository URL

    Returns:
        Dictionary containing author metadata in CodeMeta 3.1 JSON-LD format, or None if extraction fails
    """
    try:
        # Get API key from environment
        api_key = os.getenv("GOOGLE_GEMINI_API_KEY")

        if not api_key:
            logger.error(
                "GOOGLE_GEMINI_API_KEY not found in environment variables"
            )
            return None

        # Initialize Gemini client
        client = genai.Client(api_key=api_key)

        logger.info(f"GEMINI AUTHOR EXTRACTION: Processing repository URL: {repo_url}")

        # Define the response schema for structured output
        response_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "author": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "givenName": {"type": "string"},
                            "familyName": {"type": "string"},
                            "@id": {"type": "string"},  # For ORCID
                            "email": {"type": "string"},
                            "affiliation": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "@id": {"type": "string"}  # For DBpedia
                                }
                            }
                        }
                    }
                }
            }
        }

        # Call Gemini API with system instruction and structured output
        response = client.models.generate_content(
            model="gemini-2.0-pro",
            contents=f"Extract metadata for: {repo_url}",
            config=genai.types.GenerateContentConfig(
                system_instruction="""You are a Metadata Librarian specialized in the CodeMeta 3.1 standard. Your goal is to extract author information from a provided GitHub repository.
Instructions:
Data Sources: Scan the README, CITATION.cff, codemeta.json, and any root-level metadata files to identify contributors.
Author Enrichment: For each author, use your training data to find their ORCID iD and official institutional email.
Semantic Affiliation: You MUST provide the official name of the institution and its corresponding DBpedia URI (e.g., http://dbpedia.org/resource/University_Name) as the @id of the affiliation.
Standard Compliance: Format the entire output as a valid JSON-LD object following the CodeMeta 3.1 schema.
Omission Rule: If a specific piece of information (ORCID, Email, or DBpedia URI) cannot be found with high confidence, do not guess; omit that specific field.""",
                response_mime_type="application/json",
                response_schema=response_schema,
            ),
        )

        # Parse the response
        if response and response.text:
            try:
                # Extract JSON from response
                author_data = json.loads(response.text)
                logger.info(
                    f"Successfully extracted author metadata from {repo_url}"
                )
                logger.debug(f"Author data: {json.dumps(author_data, indent=2)}")
                return author_data
            except json.JSONDecodeError as e:
                logger.warning(
                    f"Failed to parse JSON response from Gemini for {repo_url}: {str(e)}"
                )
                logger.debug(f"Response text: {response.text}")
                return None
        else:
            logger.warning(f"No author metadata extracted from {repo_url}")
            return None

    except Exception as e:
        logger.error(f"Error extracting author metadata from {repo_url}: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return None
