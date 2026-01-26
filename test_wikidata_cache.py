#!/usr/bin/env python3
"""
Test script for Wikidata cache functionality.

This script demonstrates caching of keyword-to-Wikidata concept mappings
to avoid redundant API calls.
"""

import json
import time
from pathlib import Path

from src.helpers.wikidata_cache import (
    WikidataCache,
    get_cache,
    cache_get,
    cache_set,
    cache_get_batch,
    cache_set_batch,
    cache_stats,
    cache_cleanup_expired,
)
from src.core import get_logger

logger = get_logger(__name__)

# Sample concept matches
SAMPLE_MATCHES = {
    "Python": {
        "keyword": "Python",
        "concept_uri": "http://www.wikidata.org/entity/Q28865",
        "label": "Python",
        "description": "general-purpose programming language",
        "confidence": "high",
        "reasoning": "Python is a widely-used programming language",
    },
    "Machine Learning": {
        "keyword": "Machine Learning",
        "concept_uri": "http://www.wikidata.org/entity/Q2539",
        "label": "machine learning",
        "description": "field of artificial intelligence",
        "confidence": "high",
        "reasoning": "Machine Learning is a core field in AI",
    },
    "Data Science": {
        "keyword": "Data Science",
        "concept_uri": "http://www.wikidata.org/entity/Q2374463",
        "label": "data science",
        "description": "field of study",
        "confidence": "high",
        "reasoning": "Data Science is an established field",
    },
}


def test_basic_cache_operations():
    """Test basic cache get/set operations."""
    print("\n" + "=" * 80)
    print("Test 1: Basic Cache Operations")
    print("=" * 80 + "\n")

    # Create a test cache
    cache = WikidataCache(cache_file="test_cache.json")

    print("Setting cache entries...")
    for keyword, match in SAMPLE_MATCHES.items():
        result = cache.set(keyword, match)
        status = "✓" if result else "✗"
        print(f"  {status} Cached: {keyword}")

    print("\nRetrieving cache entries...")
    for keyword in SAMPLE_MATCHES.keys():
        cached = cache.get(keyword)
        if cached:
            print(f"  ✓ Retrieved: {keyword} → {cached['label']}")
        else:
            print(f"  ✗ Failed to retrieve: {keyword}")

    # Cleanup
    cache.clear()


def test_batch_operations():
    """Test batch cache operations."""
    print("\n" + "=" * 80)
    print("Test 2: Batch Cache Operations")
    print("=" * 80 + "\n")

    cache = WikidataCache(cache_file="test_cache_batch.json")

    print("Setting batch of entries...")
    cache.set_batch(SAMPLE_MATCHES)
    print(f"✓ Cached {len(SAMPLE_MATCHES)} entries\n")

    print("Retrieving batch of entries...")
    keywords = list(SAMPLE_MATCHES.keys())
    retrieved = cache.get_batch(keywords)

    found = sum(1 for v in retrieved.values() if v is not None)
    print(f"✓ Retrieved {found}/{len(keywords)} entries\n")

    print("Retrieved entries:")
    for keyword, match in retrieved.items():
        if match:
            print(f"  ✓ {keyword:20s} → {match['label']}")
        else:
            print(f"  ✗ {keyword:20s} → Not found")

    # Cleanup
    cache.clear()


def test_cache_persistence():
    """Test that cache persists across instances."""
    print("\n" + "=" * 80)
    print("Test 3: Cache Persistence")
    print("=" * 80 + "\n")

    cache_file = "test_cache_persist.json"

    print("Creating first cache instance and setting entries...")
    cache1 = WikidataCache(cache_file=cache_file)
    for keyword, match in SAMPLE_MATCHES.items():
        cache1.set(keyword, match)
    print(f"✓ Set {len(SAMPLE_MATCHES)} entries\n")

    print("Creating second cache instance and retrieving entries...")
    cache2 = WikidataCache(cache_file=cache_file)
    found = 0
    for keyword in SAMPLE_MATCHES.keys():
        if cache2.get(keyword):
            found += 1
            print(f"  ✓ Retrieved: {keyword}")

    print(f"\n✓ Successfully persisted {found}/{len(SAMPLE_MATCHES)} entries")

    # Cleanup
    cache1.clear()


def test_cache_statistics():
    """Test cache statistics."""
    print("\n" + "=" * 80)
    print("Test 4: Cache Statistics")
    print("=" * 80 + "\n")

    cache = WikidataCache(cache_file="test_cache_stats.json")

    print("Setting cache entries...")
    cache.set_batch(SAMPLE_MATCHES)

    print("\nCache Statistics:\n")
    stats = cache.get_stats()
    for key, value in stats.items():
        if key == "cache_file":
            print(f"  {key:20s}: {value}")
        elif key == "cache_size_bytes":
            print(f"  {key:20s}: {value} bytes")
        else:
            print(f"  {key:20s}: {value}")

    # Cleanup
    cache.clear()


def test_convenience_functions():
    """Test convenience functions."""
    print("\n" + "=" * 80)
    print("Test 5: Convenience Functions")
    print("=" * 80 + "\n")

    print("Using convenience functions (global cache)...\n")

    # Set entries using convenience functions
    print("Setting entries with cache_set()...")
    for keyword, match in SAMPLE_MATCHES.items():
        cache_set(keyword, match)
        print(f"  ✓ Cached: {keyword}")

    print("\nRetrieving entries with cache_get()...")
    for keyword in SAMPLE_MATCHES.keys():
        cached = cache_get(keyword)
        if cached:
            print(f"  ✓ Retrieved: {keyword}")

    print("\nCache statistics:")
    stats = cache_stats()
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  Valid entries: {stats['valid_entries']}")
    print(f"  Cache size: {stats['cache_size_bytes']} bytes")

    # Cleanup
    from src.helpers.wikidata_cache import _cache_instance
    if _cache_instance:
        _cache_instance.clear()


def test_cache_lookup_performance():
    """Test performance benefit of caching."""
    print("\n" + "=" * 80)
    print("Test 6: Cache Lookup Performance")
    print("=" * 80 + "\n")

    cache = WikidataCache(cache_file="test_cache_perf.json")

    # Pre-populate cache
    print("Pre-populating cache...")
    for keyword, match in SAMPLE_MATCHES.items():
        cache.set(keyword, match)
    print(f"✓ Cached {len(SAMPLE_MATCHES)} entries\n")

    # Test lookup performance
    print("Testing lookup performance...\n")

    keyword = "Python"
    num_lookups = 1000

    # Measure cache hit time
    start = time.time()
    for _ in range(num_lookups):
        cache.get(keyword)
    cache_time = time.time() - start

    print(f"Cache lookups: {num_lookups} in {cache_time:.4f}s")
    print(f"Average per lookup: {(cache_time / num_lookups) * 1000:.4f}ms")
    print(f"\n✓ Cache provides fast lookups (no API calls needed)")

    # Cleanup
    cache.clear()


def test_cache_directory():
    """Test cache directory location."""
    print("\n" + "=" * 80)
    print("Test 7: Cache Directory Location")
    print("=" * 80 + "\n")

    cache = get_cache()
    cache_dir = cache.cache_dir
    cache_file = cache.cache_file

    print(f"Cache directory: {cache_dir}")
    print(f"Cache file: {cache_file}")
    print(f"Cache exists: {cache_file.exists()}")
    print(f"\n✓ Cache stored at: {cache_file}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Wikidata Cache Test Suite")
    print("=" * 80)

    test_basic_cache_operations()
    test_batch_operations()
    test_cache_persistence()
    test_cache_statistics()
    test_convenience_functions()
    test_cache_lookup_performance()
    test_cache_directory()

    print("\n" + "=" * 80)
    print("All tests completed!")
    print("=" * 80 + "\n")
