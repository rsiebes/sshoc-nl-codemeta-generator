"""Persistent cache for keyword-to-Wikidata mappings."""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

from src.core import get_logger

logger = get_logger(__name__)


class WikidataCache:
    """Persistent cache for keyword-to-Wikidata concept mappings."""

    DEFAULT_CACHE_DIR = Path.home() / ".cache" / "sshoc-codemeta"
    DEFAULT_CACHE_FILE = "wikidata_keywords.json"
    DEFAULT_TTL_DAYS = 30  # Cache validity in days

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        cache_file: str = DEFAULT_CACHE_FILE,
        ttl_days: int = DEFAULT_TTL_DAYS,
    ):
        """
        Initialize the Wikidata cache.

        Args:
            cache_dir: Directory to store cache files (default: ~/.cache/sshoc-codemeta)
            cache_file: Name of the cache file (default: wikidata_keywords.json)
            ttl_days: Time-to-live for cache entries in days (default: 30)
        """
        self.cache_dir = cache_dir or self.DEFAULT_CACHE_DIR
        self.cache_file = self.cache_dir / cache_file
        self.ttl_days = ttl_days
        self.ttl_seconds = ttl_days * 24 * 3600

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load existing cache
        self._cache = self._load_cache()

        logger.debug(
            f"WikidataCache initialized at {self.cache_file} with TTL of {ttl_days} days"
        )

    def _load_cache(self) -> Dict:
        """Load cache from disk."""
        if not self.cache_file.exists():
            logger.debug(f"Cache file does not exist: {self.cache_file}")
            return {}

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                cache = json.load(f)
            logger.debug(f"Loaded cache with {len(cache)} entries")
            return cache
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in cache file: {self.cache_file}")
            return {}
        except Exception as e:
            logger.warning(f"Error loading cache: {str(e)}")
            return {}

    def _save_cache(self) -> bool:
        """Save cache to disk."""
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2)
            logger.debug(f"Cache saved to {self.cache_file}")
            return True
        except Exception as e:
            logger.warning(f"Error saving cache: {str(e)}")
            return False

    def _is_expired(self, timestamp: float) -> bool:
        """Check if a cache entry has expired."""
        current_time = datetime.now().timestamp()
        return (current_time - timestamp) > self.ttl_seconds

    def get(self, keyword: str) -> Optional[Dict]:
        """
        Get a cached concept match for a keyword.

        Args:
            keyword: The keyword to look up

        Returns:
            Cached concept match dictionary, or None if not found or expired
        """
        cache_key = keyword.lower()

        if cache_key not in self._cache:
            logger.debug(f"Cache miss for keyword: {keyword}")
            return None

        entry = self._cache[cache_key]

        # Check if entry has expired
        if self._is_expired(entry.get("timestamp", 0)):
            logger.debug(f"Cache entry expired for keyword: {keyword}")
            del self._cache[cache_key]
            self._save_cache()
            return None

        logger.debug(f"Cache hit for keyword: {keyword}")
        return entry.get("data")

    def set(self, keyword: str, concept_match: Dict) -> bool:
        """
        Cache a concept match for a keyword.

        Args:
            keyword: The keyword to cache
            concept_match: The concept match data to cache

        Returns:
            True if successfully cached, False otherwise
        """
        cache_key = keyword.lower()

        self._cache[cache_key] = {
            "data": concept_match,
            "timestamp": datetime.now().timestamp(),
            "keyword": keyword,  # Store original case
        }

        logger.debug(f"Cached concept match for keyword: {keyword}")
        return self._save_cache()

    def get_batch(self, keywords: list) -> Dict[str, Optional[Dict]]:
        """
        Get cached concept matches for multiple keywords.

        Args:
            keywords: List of keywords to look up

        Returns:
            Dictionary mapping keywords to their cached matches (None if not cached)
        """
        results = {}
        for keyword in keywords:
            results[keyword] = self.get(keyword)
        return results

    def set_batch(self, keyword_matches: Dict[str, Dict]) -> bool:
        """
        Cache multiple keyword-to-concept matches.

        Args:
            keyword_matches: Dictionary mapping keywords to concept matches

        Returns:
            True if all entries were cached successfully
        """
        for keyword, concept_match in keyword_matches.items():
            self.set(keyword, concept_match)
        return True

    def clear(self) -> bool:
        """
        Clear all cache entries.

        Returns:
            True if successfully cleared
        """
        self._cache = {}
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.warning(f"Error clearing cache: {str(e)}")
            return False

    def get_stats(self) -> Dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_entries = len(self._cache)
        expired_entries = 0
        current_time = datetime.now().timestamp()

        for entry in self._cache.values():
            if self._is_expired(entry.get("timestamp", 0)):
                expired_entries += 1

        cache_size = self.cache_file.stat().st_size if self.cache_file.exists() else 0

        return {
            "total_entries": total_entries,
            "expired_entries": expired_entries,
            "valid_entries": total_entries - expired_entries,
            "cache_file": str(self.cache_file),
            "cache_size_bytes": cache_size,
            "ttl_days": self.ttl_days,
        }

    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.

        Returns:
            Number of entries removed
        """
        expired_keys = []

        for key, entry in self._cache.items():
            if self._is_expired(entry.get("timestamp", 0)):
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            self._save_cache()
            logger.info(f"Removed {len(expired_keys)} expired cache entries")

        return len(expired_keys)


# Global cache instance
_cache_instance: Optional[WikidataCache] = None


def get_cache() -> WikidataCache:
    """Get or create the global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = WikidataCache()
    return _cache_instance


def cache_get(keyword: str) -> Optional[Dict]:
    """Get a cached concept match (convenience function)."""
    return get_cache().get(keyword)


def cache_set(keyword: str, concept_match: Dict) -> bool:
    """Cache a concept match (convenience function)."""
    return get_cache().set(keyword, concept_match)


def cache_get_batch(keywords: list) -> Dict[str, Optional[Dict]]:
    """Get cached matches for multiple keywords (convenience function)."""
    return get_cache().get_batch(keywords)


def cache_set_batch(keyword_matches: Dict[str, Dict]) -> bool:
    """Cache multiple matches (convenience function)."""
    return get_cache().set_batch(keyword_matches)


def cache_clear() -> bool:
    """Clear all cache (convenience function)."""
    return get_cache().clear()


def cache_stats() -> Dict:
    """Get cache statistics (convenience function)."""
    return get_cache().get_stats()


def cache_cleanup_expired() -> int:
    """Clean up expired entries (convenience function)."""
    return get_cache().cleanup_expired()
