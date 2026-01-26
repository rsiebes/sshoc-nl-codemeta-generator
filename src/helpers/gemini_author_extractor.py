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


def extract_authors(repo_url: str) -> Optional[Dict[str, Any]]:
    """
    Extract author metadata from a GitHub repository using Google Gemini API.

    Uses CodeMeta 3.1 standard for output format.

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

        # Prepare the prompt
        prompt = f"""Enlist the authors and find the ORCID ids, institution, email, if available for this github repository: {repo_url}. The output should be in codemeta 3.1. Also try to find the affiliation name and the dbpedia uri as an id for the affiliation"""

        logger.info(f"GEMINI AUTHOR EXTRACTION: Processing repository URL: {repo_url}")
        logger.debug(f"Request ID: {request_id}")
        logger.debug(f"Prompt: {prompt}")

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
