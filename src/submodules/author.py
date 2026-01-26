"""Author submodule for extracting and enriching author information."""

import json
from typing import Any, Dict, Optional

from src.core import get_logger
from src.submodules.base import BaseSubmodule
from src.helpers import extract_unique_authors, enrich_authors_with_gemini

logger = get_logger(__name__)


class AuthorSubmodule(BaseSubmodule):
    """
    Submodule for extracting and enriching author information from GitHub repositories.

    Workflow:
    1. Extract unique authors from GitHub commit history
    2. Enrich with ORCID IDs and affiliations using Gemini
    3. Return author data in CodeMeta 3.1 format
    """

    PROPERTY_NAME = "author"
    CATEGORY = "AI Extraction"

    def extract(self) -> Optional[Dict[str, Any]]:
        """
        Extract and enrich author information.

        Returns:
            Dictionary with 'author' key containing list of Person objects in CodeMeta format

        Example:
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
            # Extract repository URL from repo_data
            repo_url = self.repo_data.get('url')
            if not repo_url:
                logger.warning("No repository URL found in repo_data")
                return None

            logger.info(f"AUTHOR SUBMODULE: Processing authors for {repo_url}")

            # Step 1: Extract unique authors from GitHub commits
            logger.debug("Step 1: Extracting authors from GitHub commits")
            authors_json = extract_unique_authors(repo_url)

            if not authors_json:
                logger.warning(f"No authors found in GitHub commits for {repo_url}")
                return None

            authors_data = json.loads(authors_json)
            num_authors = authors_data.get('total_unique_authors', 0)
            logger.info(f"Found {num_authors} unique authors from GitHub commits")

            # Step 2: Enrich with ORCID and affiliations using Gemini
            logger.debug("Step 2: Enriching authors with ORCID and affiliations")
            enriched_json = enrich_authors_with_gemini(authors_json, repo_url)

            if not enriched_json:
                logger.warning(f"Failed to enrich authors with Gemini for {repo_url}")
                # Return raw authors without enrichment
                return {"author": authors_data.get('authors', [])}

            enriched_data = json.loads(enriched_json)
            logger.info(f"Successfully enriched {num_authors} authors with ORCID and affiliations")

            # Return the enriched author data
            return enriched_data

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON during author extraction: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error in AuthorSubmodule.extract(): {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
