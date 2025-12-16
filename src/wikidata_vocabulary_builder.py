"""
Wikidata Vocabulary Builder

This module downloads and builds a comprehensive vocabulary of software categories
from Wikidata, storing it locally for efficient lookup without repeated API calls.

Each vocabulary entry includes:
- Label: Human-readable name
- Description: Brief description
- URL: Wikidata entity URL
- QID: Wikidata entity ID

The vocabulary is built on-demand and cached locally, but NOT committed to git.
GitHub allows files up to 10MB, so we use a generous limit for rich vocabulary.
"""

import json
import requests
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import os
import re


class WikidataVocabularyBuilder:
    """Downloads and builds a comprehensive Wikidata software vocabulary."""

    # Increased limits to use full 10MB GitHub file size limit
    # This provides a much richer vocabulary for better matching
    MAX_FILE_SIZE_MB = 10
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

    def __init__(self, cache_dir: str = None):
        """
        Initialize the vocabulary builder.

        Args:
            cache_dir: Directory to store vocabulary files. Defaults to ~/.codemeta_cache
        """
        if cache_dir is None:
            cache_dir = os.path.expanduser('~/.codemeta_cache')

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.vocabulary_file = self.cache_dir / 'wikidata_software_vocabulary.json'
        self.metadata_file = self.cache_dir / 'vocabulary_metadata.json'
        self.sparql_endpoint = "https://query.wikidata.org/sparql"

        # Load existing vocabulary
        self.vocabulary = self._load_vocabulary()
        self.metadata = self._load_metadata()

    def _load_vocabulary(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Load vocabulary from file.

        Returns:
            Dictionary mapping software types to list of entities with metadata
        """
        if self.vocabulary_file.exists():
            try:
                with open(self.vocabulary_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load vocabulary: {e}")
                return {}
        return {}

    def _load_metadata(self) -> Dict[str, any]:
        """Load vocabulary metadata (version, timestamp, etc.)."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load metadata: {e}")
                return {}
        return {}

    def _save_vocabulary(self) -> None:
        """Save vocabulary to file."""
        try:
            with open(self.vocabulary_file, 'w') as f:
                json.dump(self.vocabulary, f, indent=2)
            
            # Update metadata
            self.metadata['last_updated'] = str(Path(self.vocabulary_file).stat().st_mtime)
            self.metadata['file_size_bytes'] = self.vocabulary_file.stat().st_size
            
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            
            file_size_mb = self.vocabulary_file.stat().st_size / (1024 * 1024)
            print(f"✓ Vocabulary saved ({file_size_mb:.2f} MB)")
        except Exception as e:
            print(f"Warning: Failed to save vocabulary: {e}")

    def download_software_categories(self, limit: int = 1000) -> Dict[str, Dict[str, str]]:
        """
        Download software categories from Wikidata using SPARQL.
        Includes QID, label, description, and URL.

        Args:
            limit: Maximum number of results to fetch (increased for richer vocabulary)

        Returns:
            Dictionary mapping software names to metadata (label, description, url, qid)
        """
        print(f"Downloading software categories (limit: {limit})...")

        # Optimized SPARQL query that fetches QID and description
        sparql_query = f"""
        SELECT ?item ?itemLabel ?description
        WHERE {{
            ?item wdt:P31 wd:Q7397 .  # Software
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
            OPTIONAL {{ ?item schema:description ?description . FILTER (LANG(?description) = "en") }}
        }}
        LIMIT {limit}
        """

        try:
            response = requests.get(
                self.sparql_endpoint,
                params={'query': sparql_query, 'format': 'json'},
                timeout=60
            )
            response.raise_for_status()
            data = response.json()

            software_vocab = {}
            for result in data.get('results', {}).get('bindings', []):
                item_url = result.get('item', {}).get('value', '')
                item_label = result.get('itemLabel', {}).get('value', '').strip()
                description = result.get('description', {}).get('value', '').strip()

                # Extract QID from URL (e.g., http://www.wikidata.org/entity/Q123 -> Q123)
                qid_match = re.search(r'(Q\d+)$', item_url)
                qid = qid_match.group(1) if qid_match else None

                # Only store if we have a label and QID
                if item_label and len(item_label) > 2 and qid:
                    # Keep descriptions but truncate very long ones
                    if description and len(description) > 200:
                        description = description[:200] + '...'
                    
                    software_vocab[item_label] = {
                        'label': item_label,
                        'description': description or '',
                        'url': f'https://www.wikidata.org/wiki/{qid}',
                        'qid': qid
                    }

            print(f"✓ Downloaded {len(software_vocab)} software categories")
            return software_vocab

        except Exception as e:
            print(f"Warning: Failed to download software categories: {e}")
            return {}

    def download_programming_languages(self, limit: int = 800) -> Dict[str, Dict[str, str]]:
        """
        Download programming languages from Wikidata.

        Args:
            limit: Maximum number of results to fetch (increased for richer vocabulary)

        Returns:
            Dictionary mapping language names to metadata
        """
        print(f"Downloading programming languages (limit: {limit})...")

        sparql_query = f"""
        SELECT ?item ?itemLabel ?description
        WHERE {{
            ?item wdt:P31 wd:Q9143 .  # Programming language
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
            OPTIONAL {{ ?item schema:description ?description . FILTER (LANG(?description) = "en") }}
        }}
        LIMIT {limit}
        """

        try:
            response = requests.get(
                self.sparql_endpoint,
                params={'query': sparql_query, 'format': 'json'},
                timeout=60
            )
            response.raise_for_status()
            data = response.json()

            lang_vocab = {}
            for result in data.get('results', {}).get('bindings', []):
                item_url = result.get('item', {}).get('value', '')
                item_label = result.get('itemLabel', {}).get('value', '').strip()
                description = result.get('description', {}).get('value', '').strip()

                qid_match = re.search(r'(Q\d+)$', item_url)
                qid = qid_match.group(1) if qid_match else None

                if item_label and len(item_label) > 2 and qid:
                    if description and len(description) > 200:
                        description = description[:200] + '...'
                    
                    lang_vocab[item_label] = {
                        'label': item_label,
                        'description': description or '',
                        'url': f'https://www.wikidata.org/wiki/{qid}',
                        'qid': qid
                    }

            print(f"✓ Downloaded {len(lang_vocab)} programming languages")
            return lang_vocab

        except Exception as e:
            print(f"Warning: Failed to download programming languages: {e}")
            return {}

    def download_software_frameworks(self, limit: int = 800) -> Dict[str, Dict[str, str]]:
        """
        Download software frameworks from Wikidata.

        Args:
            limit: Maximum number of results to fetch (increased for richer vocabulary)

        Returns:
            Dictionary mapping framework names to metadata
        """
        print(f"Downloading software frameworks (limit: {limit})...")

        sparql_query = f"""
        SELECT ?item ?itemLabel ?description
        WHERE {{
            ?item wdt:P31 wd:Q3886371 .  # Software framework
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
            OPTIONAL {{ ?item schema:description ?description . FILTER (LANG(?description) = "en") }}
        }}
        LIMIT {limit}
        """

        try:
            response = requests.get(
                self.sparql_endpoint,
                params={'query': sparql_query, 'format': 'json'},
                timeout=60
            )
            response.raise_for_status()
            data = response.json()

            framework_vocab = {}
            for result in data.get('results', {}).get('bindings', []):
                item_url = result.get('item', {}).get('value', '')
                item_label = result.get('itemLabel', {}).get('value', '').strip()
                description = result.get('description', {}).get('value', '').strip()

                qid_match = re.search(r'(Q\d+)$', item_url)
                qid = qid_match.group(1) if qid_match else None

                if item_label and len(item_label) > 2 and qid:
                    if description and len(description) > 200:
                        description = description[:200] + '...'
                    
                    framework_vocab[item_label] = {
                        'label': item_label,
                        'description': description or '',
                        'url': f'https://www.wikidata.org/wiki/{qid}',
                        'qid': qid
                    }

            print(f"✓ Downloaded {len(framework_vocab)} software frameworks")
            return framework_vocab

        except Exception as e:
            print(f"Warning: Failed to download software frameworks: {e}")
            return {}

    def download_libraries_and_tools(self, limit: int = 500) -> Dict[str, Dict[str, str]]:
        """
        Download software libraries and tools from Wikidata.

        Args:
            limit: Maximum number of results to fetch

        Returns:
            Dictionary mapping library/tool names to metadata
        """
        print(f"Downloading libraries and tools (limit: {limit})...")

        # Search for software libraries and tools
        sparql_query = f"""
        SELECT ?item ?itemLabel ?description
        WHERE {{
            ?item wdt:P31 wd:Q1234567 .  # Software library or tool
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
            OPTIONAL {{ ?item schema:description ?description . FILTER (LANG(?description) = "en") }}
        }}
        LIMIT {limit}
        """

        try:
            response = requests.get(
                self.sparql_endpoint,
                params={'query': sparql_query, 'format': 'json'},
                timeout=60
            )
            response.raise_for_status()
            data = response.json()

            lib_vocab = {}
            for result in data.get('results', {}).get('bindings', []):
                item_url = result.get('item', {}).get('value', '')
                item_label = result.get('itemLabel', {}).get('value', '').strip()
                description = result.get('description', {}).get('value', '').strip()

                qid_match = re.search(r'(Q\d+)$', item_url)
                qid = qid_match.group(1) if qid_match else None

                if item_label and len(item_label) > 2 and qid:
                    if description and len(description) > 200:
                        description = description[:200] + '...'
                    
                    lib_vocab[item_label] = {
                        'label': item_label,
                        'description': description or '',
                        'url': f'https://www.wikidata.org/wiki/{qid}',
                        'qid': qid
                    }

            print(f"✓ Downloaded {len(lib_vocab)} libraries and tools")
            return lib_vocab

        except Exception as e:
            print(f"Warning: Failed to download libraries and tools: {e}")
            return {}

    def build_complete_vocabulary(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """
        Build a complete software vocabulary by downloading from Wikidata.
        Uses increased limits (up to 10MB) for a rich vocabulary.

        Returns:
            Dictionary with all software-related vocabulary
        """
        print("\n" + "=" * 70)
        print("Building Complete Wikidata Software Vocabulary")
        print(f"Maximum file size: {self.MAX_FILE_SIZE_MB}MB")
        print("=" * 70 + "\n")

        complete_vocab = {
            'software': self.download_software_categories(limit=1000),
            'programming_languages': self.download_programming_languages(limit=800),
            'frameworks': self.download_software_frameworks(limit=800),
            'libraries_and_tools': self.download_libraries_and_tools(limit=500),
        }

        # Store in the vocabulary
        self.vocabulary = complete_vocab
        self._save_vocabulary()

        # Print summary
        print("\n" + "=" * 70)
        print("Vocabulary Summary")
        print("=" * 70)
        total_items = 0
        for category, items in complete_vocab.items():
            count = len(items)
            total_items += count
            print(f"  {category}: {count} items")

        file_size_mb = self.vocabulary_file.stat().st_size / (1024 * 1024)
        print(f"\nTotal vocabulary items: {total_items}")
        print(f"File size: {file_size_mb:.2f} MB (limit: {self.MAX_FILE_SIZE_MB}MB)")
        
        if file_size_mb > self.MAX_FILE_SIZE_MB:
            print(f"⚠️  Warning: Vocabulary exceeds {self.MAX_FILE_SIZE_MB}MB limit!")
        else:
            print(f"✓ Within GitHub file size limit")
        
        print("=" * 70 + "\n")

        return complete_vocab

    def find_matching_category(self, search_term: str) -> Optional[Dict[str, str]]:
        """
        Find a matching category from the vocabulary using fuzzy matching.

        Args:
            search_term: Term to search for

        Returns:
            Matching category metadata (label, description, url, qid), or None if not found
        """
        if not self.vocabulary:
            return None

        search_term_lower = search_term.lower()
        best_match = None
        best_match_score = 0

        # Search in all vocabulary categories
        for category_type, items in self.vocabulary.items():
            if isinstance(items, dict):
                for name, metadata in items.items():
                    if isinstance(metadata, dict):
                        name_lower = name.lower()
                        
                        # Exact match (highest priority)
                        if search_term_lower == name_lower:
                            return metadata
                        
                        # Partial match scoring
                        if search_term_lower in name_lower:
                            score = len(search_term) / len(name)
                            if score > best_match_score:
                                best_match_score = score
                                best_match = metadata

        return best_match

    def get_vocabulary_stats(self) -> Dict[str, any]:
        """
        Get vocabulary statistics.

        Returns:
            Dictionary with vocabulary sizes and metadata
        """
        stats = {
            'categories': {},
            'total_items': 0,
            'file_size_mb': 0,
            'max_file_size_mb': self.MAX_FILE_SIZE_MB,
            'last_updated': self.metadata.get('last_updated', 'Unknown'),
        }
        
        for category, items in self.vocabulary.items():
            if isinstance(items, dict):
                count = len(items)
                stats['categories'][category] = count
                stats['total_items'] += count
        
        if self.vocabulary_file.exists():
            stats['file_size_mb'] = round(self.vocabulary_file.stat().st_size / (1024 * 1024), 2)
        
        return stats

    def is_vocabulary_outdated(self, max_age_days: int = 30) -> bool:
        """
        Check if vocabulary is outdated and needs refreshing.

        Args:
            max_age_days: Maximum age of vocabulary in days

        Returns:
            True if vocabulary is outdated, False otherwise
        """
        if not self.vocabulary_file.exists():
            return True
        
        import time
        file_mtime = self.vocabulary_file.stat().st_mtime
        age_days = (time.time() - file_mtime) / (24 * 3600)
        
        return age_days > max_age_days


# Command-line interface for building vocabulary
if __name__ == '__main__':
    import sys

    builder = WikidataVocabularyBuilder()

    if len(sys.argv) > 1 and sys.argv[1] == 'build':
        builder.build_complete_vocabulary()
    elif len(sys.argv) > 1 and sys.argv[1] == 'stats':
        stats = builder.get_vocabulary_stats()
        print("\nVocabulary Statistics:")
        print("=" * 50)
        for key, value in stats.items():
            if key == 'categories':
                print(f"\nCategories:")
                for cat, count in value.items():
                    print(f"  {cat}: {count} items")
            else:
                print(f"{key}: {value}")
    else:
        # Print current vocabulary stats
        stats = builder.get_vocabulary_stats()
        if stats['total_items'] > 0:
            print("\nCurrent Vocabulary Statistics:")
            print("=" * 50)
            for cat, count in stats['categories'].items():
                print(f"  {cat}: {count} items")
            print(f"\nTotal items: {stats['total_items']}")
            print(f"File size: {stats['file_size_mb']} MB / {stats['max_file_size_mb']}MB")
            print(f"Last updated: {stats['last_updated']}")
        else:
            print("\nNo vocabulary loaded.")
            print("Usage: python3 src/wikidata_vocabulary_builder.py build")
            print("       python3 src/wikidata_vocabulary_builder.py stats")
