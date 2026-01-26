"""Gemini API integration for keyword extraction."""

import os
from typing import List, Optional

from dotenv import load_dotenv
from google import genai

from src.core import get_logger
from src.helpers.gemini_schemas import Keyword, KeywordList

logger = get_logger(__name__)

# Load environment variables from .env file
load_dotenv()


def extract_keywords(repo_url: str) -> Optional[List[Keyword]]:
    """
    Extract keywords from a GitHub repository using Google Gemini API.

    Args:
        repo_url: The GitHub repository URL

    Returns:
        List of Keyword objects with name and context_clues, or None if extraction fails
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

        # Prepare the prompt for Gemini
        logger.info(f"GEMINI EXTRACTION: Processing repository URL: {repo_url}")
        prompt = f"""Analyze the GitHub repository at {repo_url} and extract exactly 10 meaningful keywords that describe the project.

For each keyword, provide:
1. The keyword itself (e.g., 'OpenStreetMap', 'Python', 'Data Analysis')
2. Context clues explaining why it's relevant to this repository

Return the results as a JSON object with the structure:
{{
    "keywords": [
        {{"name": "keyword1", "context_clues": "explanation"}},
        {{"name": "keyword2", "context_clues": "explanation"}},
        ...
    ]
}}

Focus on:
- Programming languages used
- Main libraries and frameworks
- Problem domains and use cases
- Technologies and tools
- Key concepts and methodologies

Ensure all 10 keywords are relevant and non-redundant."""

        # Call Gemini API with structured output
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=KeywordList,
            ),
        )

        # Parse the response
        if response and response.parsed:
            keywords = response.parsed.keywords
            logger.info(
                f"Successfully extracted {len(keywords)} keywords from {repo_url}"
            )
            return keywords
        else:
            logger.warning(f"No keywords extracted from {repo_url}")
            return None

    except Exception as e:
        logger.error(f"Error extracting keywords from {repo_url}: {str(e)}")
        return None
