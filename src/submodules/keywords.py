"""Submodule for extracting keywords from repository using Google Gemini API and enriching with Wikidata."""

from typing import Any, Dict, List, Optional

from src.core import get_logger
from src.helpers.gemini_extractor import extract_keywords
from src.helpers.wikidata_enricher import enrich_keywords_with_wikidata
from src.helpers.wikidata_matcher import match_keywords_to_wikidata_concepts
from src.submodules.base import BaseSubmodule

logger = get_logger(__name__)


class KeywordsSubmodule(BaseSubmodule):
    """Extract keywords from repository using Google Gemini API and enrich with Wikidata concepts."""

    PROPERTY_NAME = "keywords"
    CATEGORY = "ai_extraction"

    def extract(self) -> Optional[List[Dict[str, str]]]:
        """
        Extract keywords from repository using Gemini API and enrich with Wikidata concepts.

        Returns:
            List of DefinedTerm dictionaries with keyword name and Wikidata URL,
            or None if extraction fails

        Example:
            [
                {
                    "@type": "DefinedTerm",
                    "name": "Python",
                    "url": "https://www.wikidata.org/wiki/Q28865"
                },
                {
                    "@type": "DefinedTerm",
                    "name": "Data Science",
                    "url": "https://www.wikidata.org/wiki/Q2374463"
                }
            ]
        """
        try:
            # Get repository metadata
            repo_url = self.repo_data.get("data", {}).get("html_url")
            repo_name = self.repo_data.get("data", {}).get("name", "")
            repo_description = self.repo_data.get("data", {}).get("description", "")

            if not repo_url:
                logger.warning(
                    "Repository URL not found in repo_data, cannot extract keywords"
                )
                return None

            logger.info(f"KEYWORDS SUBMODULE: repo_url = {repo_url}")
            logger.debug(f"Extracting keywords for repository: {repo_url}")

            # Step 1: Extract keywords using Gemini
            keyword_objects = extract_keywords(repo_url)

            if not keyword_objects:
                logger.warning(f"No keywords extracted for {repo_url}")
                return None

            keyword_names = [keyword.name for keyword in keyword_objects]
            logger.info(f"Extracted {len(keyword_names)} keywords from Gemini")

            # Step 2: Enrich keywords with Wikidata
            logger.debug("Enriching keywords with Wikidata data...")
            keywords_with_wikidata = enrich_keywords_with_wikidata(keyword_names)

            # Step 3: Match keywords to Wikidata concepts using Gemini
            logger.debug("Matching keywords to Wikidata concepts...")
            concept_matches = match_keywords_to_wikidata_concepts(
                keywords_with_wikidata, repo_url, repo_description
            )

            # Step 4: Build DefinedTerm objects for Codemeta
            defined_terms = []

            for keyword_name, concept_match in concept_matches.items():
                if concept_match and concept_match.concept_uri:
                    # Convert Wikidata entity URI to wiki URL
                    # From: http://www.wikidata.org/entity/Q28865
                    # To: https://www.wikidata.org/wiki/Q28865
                    entity_id = concept_match.concept_uri.split("/")[-1]
                    wiki_url = f"https://www.wikidata.org/wiki/{entity_id}"

                    defined_term = {
                        "@type": "DefinedTerm",
                        "name": keyword_name,
                        "url": wiki_url,
                    }
                    defined_terms.append(defined_term)
                    logger.debug(
                        f"Added DefinedTerm: {keyword_name} → {wiki_url}"
                    )
                else:
                    logger.warning(
                        f"Could not match keyword '{keyword_name}' to Wikidata concept"
                    )

            if not defined_terms:
                logger.warning(f"No keywords could be enriched with Wikidata for {repo_url}")
                return None

            logger.info(
                f"Successfully created {len(defined_terms)} DefinedTerms for {repo_url}"
            )

            return defined_terms

        except Exception as e:
            self.error = str(e)
            logger.error(f"Error in KeywordsSubmodule.extract(): {self.error}")
            return None
