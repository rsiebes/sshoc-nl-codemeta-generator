"""
Vocabulary Cache Manager

This module provides local caching of vocabulary lookups (Wikidata, etc.)
to avoid repeated API calls and improve performance.
"""

import json
import os
from typing import Optional, Dict, Any
from pathlib import Path


class VocabularyCache:
    """Manages local caching of vocabulary lookups."""

    def __init__(self, cache_dir: str = None):
        """
        Initialize the vocabulary cache.

        Args:
            cache_dir: Directory to store cache files. Defaults to ~/.codemeta_cache
        """
        if cache_dir is None:
            cache_dir = os.path.expanduser('~/.codemeta_cache')

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Cache files for different vocabularies
        self.wikidata_cache_file = self.cache_dir / 'wikidata_cache.json'
        self.category_cache_file = self.cache_dir / 'category_cache.json'

        # Load existing caches
        self.wikidata_cache = self._load_cache(self.wikidata_cache_file)
        self.category_cache = self._load_cache(self.category_cache_file)

    def _load_cache(self, cache_file: Path) -> Dict[str, Any]:
        """
        Load cache from file.

        Args:
            cache_file: Path to cache file

        Returns:
            Dictionary of cached data
        """
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load cache from {cache_file}: {e}")
                return {}
        return {}

    def _save_cache(self, cache_file: Path, cache_data: Dict[str, Any]) -> None:
        """
        Save cache to file.

        Args:
            cache_file: Path to cache file
            cache_data: Dictionary of cache data
        """
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save cache to {cache_file}: {e}")

    def get_wikidata_entity(self, search_term: str) -> Optional[Dict[str, Any]]:
        """
        Get cached Wikidata entity data.

        Args:
            search_term: Search term to look up

        Returns:
            Cached entity data, or None if not in cache
        """
        cache_key = search_term.lower()
        return self.wikidata_cache.get(cache_key)

    def set_wikidata_entity(self, search_term: str, entity_data: Dict[str, Any]) -> None:
        """
        Cache Wikidata entity data.

        Args:
            search_term: Search term
            entity_data: Entity data to cache
        """
        cache_key = search_term.lower()
        self.wikidata_cache[cache_key] = entity_data
        self._save_cache(self.wikidata_cache_file, self.wikidata_cache)

    def get_category(self, repo_name: str) -> Optional[str]:
        """
        Get cached applicationCategory.

        Args:
            repo_name: Repository name

        Returns:
            Cached category, or None if not in cache
        """
        cache_key = repo_name.lower()
        return self.category_cache.get(cache_key)

    def set_category(self, repo_name: str, category: str) -> None:
        """
        Cache applicationCategory.

        Args:
            repo_name: Repository name
            category: Category to cache
        """
        cache_key = repo_name.lower()
        self.category_cache[cache_key] = category
        self._save_cache(self.category_cache_file, self.category_cache)

    def clear_wikidata_cache(self) -> None:
        """Clear the Wikidata cache."""
        self.wikidata_cache = {}
        self._save_cache(self.wikidata_cache_file, self.wikidata_cache)

    def clear_category_cache(self) -> None:
        """Clear the category cache."""
        self.category_cache = {}
        self._save_cache(self.category_cache_file, self.category_cache)

    def clear_all_caches(self) -> None:
        """Clear all caches."""
        self.clear_wikidata_cache()
        self.clear_category_cache()

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache sizes
        """
        return {
            'wikidata_cache_size': len(self.wikidata_cache),
            'category_cache_size': len(self.category_cache),
            'total_cached_items': len(self.wikidata_cache) + len(self.category_cache),
        }


# Global cache instance
_global_cache = None


def get_vocabulary_cache(cache_dir: str = None) -> VocabularyCache:
    """
    Get or create the global vocabulary cache instance.

    Args:
        cache_dir: Optional cache directory

    Returns:
        VocabularyCache instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = VocabularyCache(cache_dir)
    return _global_cache
