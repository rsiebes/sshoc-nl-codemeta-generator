"""Simple Gemini helper to extract author names from GitHub repositories."""

import os
from typing import Optional, List

from dotenv import load_dotenv
from google import genai

from src.core import get_logger

logger = get_logger(__name__)

# Load environment variables from .env file
load_dotenv()


def get_author_names(repo_url: str) -> Optional[List[str]]:
    """
    Get a list of author names from a GitHub repository using Gemini with multi-turn conversation.

    Uses follow-up prompts to check:
    - Contributors tab
    - AUTHORS file
    - Commit history
    - README
    - LICENSE file

    Args:
        repo_url: The GitHub repository URL

    Returns:
        List of author names, or None if extraction fails
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

        logger.info(f"GEMINI SIMPLE AUTHOR EXTRACTION: Processing repository URL: {repo_url}")

        # Start a chat session for multi-turn conversation
        chat = client.chats.create(
            model="gemini-2.0-flash",
        )

        # First prompt: Initial question about authors
        first_prompt = f"Who are the authors of this github repository: {repo_url}"
        
        logger.debug(f"First prompt: {first_prompt}")
        response1 = chat.send_message(first_prompt)
        
        if not response1 or not response1.text:
            logger.warning(f"No response from first prompt for {repo_url}")
            return None
        
        logger.debug(f"First response: {response1.text}")

        # Second prompt: Follow-up to check multiple sources
        follow_up_prompt = """Based on your previous response, please provide a comprehensive list of authors by checking:
1. The Contributors tab on the GitHub page
2. The AUTHORS or CONTRIBUTORS file in the repository root
3. The commit history (who made the most significant commits)
4. The README file (often mentions authors/maintainers)
5. The LICENSE file (sometimes includes author information)

Please provide a clear, comma-separated list of author names you can identify from these sources. If you cannot find definitive author information, please state that clearly."""

        logger.debug(f"Follow-up prompt: {follow_up_prompt}")
        response2 = chat.send_message(follow_up_prompt)
        
        if not response2 or not response2.text:
            logger.warning(f"No response from follow-up prompt for {repo_url}")
            return response1.text
        
        logger.info(f"Successfully extracted author names from {repo_url}")
        logger.debug(f"Follow-up response: {response2.text}")
        
        return response2.text

    except Exception as e:
        logger.error(f"Error extracting author names from {repo_url}: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return None
