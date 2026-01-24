"""Caching system for storing API responses and parsed data."""

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

from .logger import get_logger

logger = get_logger(__name__)


class Cache:
    """File-based caching system for repository data."""

    CACHE_DIR = Path(".cache")
    CACHE_EXTENSION = ".json"

    def __init__(self, use_cache: bool = False, ttl: int = 3600):
        """
        Initialize the cache system.

        Args:
            use_cache: Whether to use caching (default: False)
            ttl: Time-to-live in seconds (default: 3600 = 1 hour)
        """
        self.use_cache = use_cache
        self.ttl = ttl
        self._ensure_cache_dir()

        logger.debug(
            f"Cache initialized: use_cache={use_cache}, ttl={ttl}s"
        )

    def _ensure_cache_dir(self) -> None:
        """Ensure the cache directory exists."""
        try:
            self.CACHE_DIR.mkdir(exist_ok=True)
            logger.debug(f"Cache directory ensured at {self.CACHE_DIR}")
        except OSError as e:
            logger.warning(f"Could not create cache directory: {e}")

    def _get_cache_path(self, owner: str, repo: str) -> Path:
        """
        Get the cache file path for a repository.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Path to the cache file
        """
        filename = f"{owner}_{repo}{self.CACHE_EXTENSION}"
        return self.CACHE_DIR / filename

    def get(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached data for a repository.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Cached data if valid and caching is enabled, None otherwise
        """
        if not self.use_cache:
            logger.debug("Cache is disabled, skipping retrieval")
            return None

        cache_path = self._get_cache_path(owner, repo)

        if not cache_path.exists():
            logger.debug(f"Cache file not found: {cache_path}")
            return None

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            # Check if cache is still valid
            if self._is_valid(cache_data):
                logger.info(f"Cache hit for {owner}/{repo}")
                return cache_data.get("data")
            else:
                logger.debug(f"Cache expired for {owner}/{repo}")
                return None

        except (IOError, json.JSONDecodeError) as e:
            logger.warning(f"Error reading cache file {cache_path}: {e}")
            return None

    def set(self, owner: str, repo: str, data: Dict[str, Any]) -> bool:
        """
        Store data in cache for a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            data: Data to cache (will be stored under 'data' key)

        Returns:
            True if successful, False otherwise
        """
        if not self.use_cache:
            logger.debug("Cache is disabled, skipping storage")
            return False

        cache_path = self._get_cache_path(owner, repo)

        cache_entry = {
            "repo": f"{owner}/{repo}",
            "timestamp": int(time.time()),
            "ttl": self.ttl,
            "data": data,
        }

        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_entry, f, indent=2, ensure_ascii=False)

            logger.debug(f"Cache stored for {owner}/{repo} at {cache_path}")
            return True

        except IOError as e:
            logger.warning(f"Error writing cache file {cache_path}: {e}")
            return False

    def _is_valid(self, cache_data: Dict[str, Any]) -> bool:
        """
        Check if cached data is still valid based on TTL.

        Args:
            cache_data: Cache entry to validate

        Returns:
            True if cache is valid, False if expired
        """
        if "timestamp" not in cache_data or "ttl" not in cache_data:
            logger.warning("Invalid cache entry: missing timestamp or ttl")
            return False

        cache_age = int(time.time()) - cache_data["timestamp"]
        is_valid = cache_age < cache_data["ttl"]

        logger.debug(
            f"Cache validity check: age={cache_age}s, ttl={cache_data['ttl']}s, valid={is_valid}"
        )

        return is_valid

    def clear(self, owner: Optional[str] = None, repo: Optional[str] = None) -> bool:
        """
        Clear cache entries.

        Args:
            owner: Repository owner (if None, clears all cache)
            repo: Repository name (required if owner is specified)

        Returns:
            True if successful, False otherwise
        """
        try:
            if owner and repo:
                # Clear specific repository cache
                cache_path = self._get_cache_path(owner, repo)
                if cache_path.exists():
                    cache_path.unlink()
                    logger.info(f"Cleared cache for {owner}/{repo}")
                    return True
            else:
                # Clear all cache
                import shutil
                if self.CACHE_DIR.exists():
                    shutil.rmtree(self.CACHE_DIR)
                    self._ensure_cache_dir()
                    logger.info("Cleared all cache")
                    return True

            return False

        except OSError as e:
            logger.warning(f"Error clearing cache: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """
        Get cache status information.

        Returns:
            Dictionary with cache status
        """
        cache_files = list(self.CACHE_DIR.glob(f"*{self.CACHE_EXTENSION}"))

        return {
            "use_cache": self.use_cache,
            "ttl": self.ttl,
            "cache_dir": str(self.CACHE_DIR),
            "cache_files": len(cache_files),
            "cache_files_list": [f.name for f in cache_files],
        }
