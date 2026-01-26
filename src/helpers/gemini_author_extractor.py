"""Gemini API integration for author metadata extraction."""

import json
import os
import time
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from google import genai

from src.core import get_logger

logger = get_logger(__name__)

# Load environment variables from .env file
load_dotenv()

# System instructions for Gemini
SYSTEM_INSTRUCTIONS = """You are a metadata extraction assistant specialized in the CodeMeta 3.1 standard. Your task is to analyze GitHub repository URLs and extract key software metadata.
Guidelines:
Use the repository's README, CITATION.cff, and package.json (if they exist) to identify authors.
Search for ORCID iDs and official academic emails.
For affiliations, find the official institution name and its corresponding DBpedia URI (e.g., http://dbpedia.org/resource/University_Name).
If information is missing, do not hallucinate; omit the field or use a null value.
Output must strictly follow the CodeMeta 3.1 JSON-LD format."""


def extract_authors(repo_url: str) -> Optional[Dict[str, Any]]:
    """
    Extract author metadata from a GitHub repository using Google Gemini API.

    Uses CodeMeta 3.1 standard with system instructions for consistent output.

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

        # Create a unique request ID to bypass Gemini's caching
        request_id = int(time.time() * 1000)

        # Prepare the full prompt with system instructions included
        prompt = f"""[Request ID: {request_id}]

{SYSTEM_INSTRUCTIONS}

Enlist the authors and find the ORCID ids, institution (with DBpedia URI), and email for this GitHub repository: {repo_url}.
Return the result strictly in CodeMeta 3.1 JSON format. Ensure the '@id' for the affiliation is the DBpedia resource link."""

        logger.info(f"GEMINI AUTHOR EXTRACTION: Processing repository URL: {repo_url}")
        logger.debug(f"Request ID: {request_id}")

        # Call Gemini API
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
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
        return None
