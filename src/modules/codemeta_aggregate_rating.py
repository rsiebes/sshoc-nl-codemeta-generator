"""
CodeMeta aggregateRating Module

Extracts aggregate rating information according to CodeMeta 3.1 standard.
The aggregateRating property describes the average rating or score of the software
based on user reviews, GitHub stars, or other metrics.

This module extracts rating information from:
1. GitHub stars (normalized to 0-5 scale)
2. GitHub watchers (normalized to 0-5 scale)
3. Repository popularity metrics

Returns:
    dict: Rating object with ratingValue and ratingCount
    None: If no rating data can be determined
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AggregateRatingExtractor:
    """Extracts aggregate rating from GitHub repository metadata."""

    def __init__(self, repo_data: Dict[str, Any]):
        """
        Initialize the AggregateRatingExtractor.

        Args:
            repo_data: Dictionary containing repository metadata from GitHub API
        """
        self.repo_data = repo_data
        self.stars = repo_data.get("stargazers_count", 0) or 0
        self.watchers = repo_data.get("watchers_count", 0) or 0
        self.forks = repo_data.get("forks_count", 0) or 0

    def extract(self) -> Optional[Dict[str, Any]]:
        """
        Extract aggregate rating from repository metrics.

        Returns:
            dict: Rating object with ratingValue, ratingCount, and bestRating
            None: If no rating data can be determined
        """
        # Use GitHub stars as primary rating metric
        # Normalize to 0-5 scale based on popularity
        
        if self.stars == 0:
            logger.debug("No stars found - cannot determine rating")
            return None

        # Calculate rating based on star count
        # This is a heuristic approach:
        # - 0-10 stars: 1 star
        # - 11-100 stars: 2 stars
        # - 101-500 stars: 3 stars
        # - 501-2000 stars: 4 stars
        # - 2000+ stars: 5 stars
        
        if self.stars <= 10:
            rating_value = 1.0
        elif self.stars <= 100:
            rating_value = 2.0
        elif self.stars <= 500:
            rating_value = 3.0
        elif self.stars <= 2000:
            rating_value = 4.0
        else:
            rating_value = 5.0

        # Create rating object
        rating_object = {
            "@type": "AggregateRating",
            "ratingValue": rating_value,
            "bestRating": 5,
            "worstRating": 1,
            "ratingCount": self.stars,
            "name": f"GitHub Stars ({self.stars})"
        }

        logger.info(f"Extracted aggregate rating: {rating_value} stars based on {self.stars} GitHub stars")
        return rating_object

    def _normalize_stars_to_rating(self, stars: int) -> float:
        """
        Normalize GitHub star count to a 0-5 rating scale.

        Args:
            stars: Number of GitHub stars

        Returns:
            float: Rating value between 0 and 5
        """
        if stars == 0:
            return 0.0
        elif stars <= 10:
            return 1.0
        elif stars <= 100:
            return 2.0
        elif stars <= 500:
            return 3.0
        elif stars <= 2000:
            return 4.0
        else:
            return 5.0


def extract(repo_data: Dict[str, Any], repo_files: Dict[str, str] = None, **kwargs) -> Optional[Dict[str, Any]]:
    """
    Extract aggregate rating from repository metadata.

    Args:
        repo_data: Dictionary containing repository metadata from GitHub API
        repo_files: Dictionary containing repository file contents (optional)
        **kwargs: Additional arguments (ignored)

    Returns:
        dict: Rating object with ratingValue and ratingCount
        None: If no rating data can be determined
    """
    try:
        extractor = AggregateRatingExtractor(repo_data)
        result = extractor.extract()

        if result:
            logger.info(f"Extracted aggregate rating")
            return result
        else:
            logger.debug("No aggregate rating found")
            return None

    except Exception as e:
        logger.error(f"Error extracting aggregate rating: {str(e)}")
        return None


def get(repository_url: str) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Extract aggregate rating from a GitHub repository.

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'aggregateRating' property and its value.
              Returns an empty dict if no rating can be extracted.
    """
    try:
        from src.github_api import parse_repository_url, fetch_repository_info
        from src.utils import normalize_url

        repository_url = normalize_url(repository_url)
        owner, repo = parse_repository_url(repository_url)
        if not owner or not repo:
            return {}

        repo_data = fetch_repository_info(owner, repo)
        if not repo_data:
            return {}

        result = extract(repo_data)

        if result:
            return {"aggregateRating": result}
        else:
            return {}

    except Exception as e:
        logger.error(f"Error in get function: {str(e)}")
        return {}
