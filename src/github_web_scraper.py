"""
Efficient GitHub web scraper for extracting repository metadata without API.

This module provides optimized scraping of GitHub repositories using Selenium
to handle JavaScript-rendered content and extract all available metadata.
"""

import re
import json
from typing import Optional, Dict, List, Any
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


class GitHubMetadataExtractor:
    """Extract metadata from GitHub repositories using web scraping."""
    
    # CSS selectors for common GitHub elements
    SELECTORS = {
        'description': '[data-test-id="repo-header-description"]',
        'about_section': '[data-test-id="repo-about-description"]',
        'topics': '[data-test-id="repo-topics"]',
        'stars': '[href*="/stargazers"]',
        'forks': '[href*="/network/members"]',
        'language': '[itemprop="programmingLanguage"]',
        'license': '[data-test-id="repo-license-link"]',
        'commits': '[data-test-id="commit-count"]',
        'branches': '[data-test-id="branch-count"]',
        'releases': '[data-test-id="release-count"]',
        'readme': '[data-test-id="readme-blob"]',
    }
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the GitHub metadata extractor.
        
        Args:
            verbose (bool): Enable verbose logging
        """
        self.verbose = verbose
        self.session_cache = {}
    
    def extract_from_page_content(self, repo_url: str, page_content: str) -> Dict[str, Any]:
        """
        Extract metadata from GitHub page content (markdown).
        
        Args:
            repo_url (str): The GitHub repository URL
            page_content (str): The page content as markdown
            
        Returns:
            Dict[str, Any]: Extracted metadata
        """
        metadata = {
            'url': repo_url,
            'codeRepository': repo_url,
        }
        
        # Extract repository info from URL
        parts = repo_url.rstrip('/').split('/')
        if len(parts) >= 2:
            metadata['name'] = parts[-1]
            metadata['owner'] = parts[-2]
        
        # Extract description
        description = self._extract_description(page_content)
        if description:
            metadata['description'] = description
        
        # Extract programming languages
        languages = self._extract_languages(page_content)
        if languages:
            metadata['programmingLanguage'] = languages
        
        # Extract license
        license_info = self._extract_license(page_content)
        if license_info:
            metadata['license'] = license_info
        
        # Extract topics/keywords
        topics = self._extract_topics(page_content)
        if topics:
            metadata['keywords'] = topics
        
        # Extract repository statistics
        stats = self._extract_stats(page_content)
        metadata.update(stats)
        
        # Extract dates
        dates = self._extract_dates(page_content)
        metadata.update(dates)
        
        # Extract authors/contributors
        authors = self._extract_authors(page_content)
        if authors:
            metadata['authors'] = authors
        
        return metadata
    
    def _extract_description(self, content: str) -> Optional[str]:
        """Extract repository description."""
        # Try multiple patterns for description
        patterns = [
            # Pattern 1: First paragraph after title
            r'^# .+?\n\n(.+?)(?:\n\n```|\n\n#|\n\n##)',
            # Pattern 2: About section
            r'## About\n\n(.+?)(?:\n\n##|\Z)',
            # Pattern 3: Description in quotes
            r'> (.+?)(?:\n\n|\Z)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if match:
                desc = match.group(1).strip()
                # Clean up and limit length
                desc = ' '.join(desc.split())  # Normalize whitespace
                if len(desc) > 20 and not desc.startswith('No description'):
                    return desc[:500]
        
        return None
    
    def _extract_languages(self, content: str) -> Optional[List[str]]:
        """Extract programming languages."""
        languages = set()
        
        # Pattern 1: Language percentages
        lang_pattern = r'\*?\s*\[?([A-Za-z#\+]+)\s+[\d.]+%\]?'
        matches = re.findall(lang_pattern, content)
        if matches:
            languages.update(matches)
        
        # Pattern 2: Language mentions in text
        common_langs = ['Python', 'JavaScript', 'Java', 'C\\+\\+', 'C#', 'Go', 'Rust', 
                       'PHP', 'Ruby', 'Swift', 'Kotlin', 'TypeScript', 'R', 'Scala',
                       'Prolog', 'Shell', 'Makefile', 'Dockerfile', 'HTML', 'CSS']
        
        for lang in common_langs:
            if re.search(rf'\b{lang}\b', content, re.IGNORECASE):
                # Extract the actual case from content
                match = re.search(rf'\b({lang})\b', content, re.IGNORECASE)
                if match:
                    languages.add(match.group(1))
        
        return list(languages) if languages else None
    
    def _extract_license(self, content: str) -> Optional[Dict[str, str]]:
        """Extract license information."""
        licenses = {
            'MIT': ('MIT License', 'https://opensource.org/licenses/MIT'),
            'Apache': ('Apache License 2.0', 'https://opensource.org/licenses/Apache-2.0'),
            'GPL': ('GNU General Public License', 'https://www.gnu.org/licenses/'),
            'BSD': ('BSD License', 'https://opensource.org/licenses/BSD-3-Clause'),
            'ISC': ('ISC License', 'https://opensource.org/licenses/ISC'),
            'LGPL': ('GNU Lesser General Public License', 'https://www.gnu.org/licenses/lgpl-3.0.html'),
            'MPL': ('Mozilla Public License 2.0', 'https://opensource.org/licenses/MPL-2.0'),
            'AGPL': ('GNU Affero General Public License', 'https://www.gnu.org/licenses/agpl-3.0.html'),
        }
        
        for key, (name, url) in licenses.items():
            if re.search(rf'\b{key}\b', content, re.IGNORECASE):
                return {'name': name, 'url': url}
        
        return None
    
    def _extract_topics(self, content: str) -> Optional[List[str]]:
        """Extract topics/keywords."""
        topics = []
        
        # Pattern 1: Topics section
        topics_match = re.search(r'Topics?\n\n(.+?)(?:\n\n|##|\Z)', content, re.DOTALL)
        if topics_match:
            topics_text = topics_match.group(1)
            # Extract from links
            topic_links = re.findall(r'\[([a-z0-9\-_]+)\]', topics_text, re.IGNORECASE)
            topics.extend(topic_links)
        
        # Pattern 2: Extract from content keywords
        keyword_patterns = {
            'machine-learning': r'(machine learning|deep learning|neural network)',
            'web-framework': r'(web framework|web application)',
            'data-science': r'(data science|data analysis)',
            'api': r'\bAPI\b',
            'database': r'(database|SQL|NoSQL)',
            'testing': r'(testing|test framework)',
            'documentation': r'(documentation|docs)',
            'cli': r'(command line|CLI)',
            'rest': r'REST',
            'graphql': r'GraphQL',
            'docker': r'Docker',
            'kubernetes': r'Kubernetes',
            'devops': r'DevOps',
            'security': r'(security|encryption)',
            'authentication': r'(authentication|auth)',
            'visualization': r'(visualization|charts|graphs)',
        }
        
        for keyword, pattern in keyword_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                topics.append(keyword)
        
        return list(set(topics)) if topics else None
    
    def _extract_stats(self, content: str) -> Dict[str, Any]:
        """Extract repository statistics."""
        stats = {}
        
        # Extract numbers with context
        patterns = {
            'stars': r'Star\s+(\d+)',
            'forks': r'Fork\s+(\d+)',
            'commits': r'(\d+)\s+Commits?',
            'branches': r'(\d+)\s+Branches?',
            'releases': r'(\d+)\s+releases?',
            'tags': r'(\d+)\s+Tags?',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    stats[key] = int(match.group(1))
                except (ValueError, IndexError):
                    pass
        
        return stats
    
    def _extract_dates(self, content: str) -> Dict[str, str]:
        """Extract important dates."""
        dates = {}
        
        # Pattern for dates like "Created on Jan 1, 2020" or "Last updated 2 weeks ago"
        date_patterns = {
            'created': r'Created\s+(?:on\s+)?(\w+\s+\d+,?\s+\d{4})',
            'updated': r'(?:Last\s+)?[Uu]pdated\s+(?:on\s+)?(\w+\s+\d+,?\s+\d{4})',
            'pushed': r'[Pp]ushed\s+(?:on\s+)?(\w+\s+\d+,?\s+\d{4})',
        }
        
        for key, pattern in date_patterns.items():
            match = re.search(pattern, content)
            if match:
                dates[key] = match.group(1)
        
        return dates
    
    def _extract_authors(self, content: str) -> Optional[List[str]]:
        """Extract author/contributor information."""
        authors = []
        
        # Pattern 1: Author mentions
        author_pattern = r'(?:Author|Created by|Maintained by):\s*([^\n]+)'
        matches = re.findall(author_pattern, content, re.IGNORECASE)
        authors.extend(matches)
        
        # Pattern 2: Contributors section
        contrib_match = re.search(r'## Contributors?\n\n(.+?)(?:\n\n##|\Z)', content, re.DOTALL)
        if contrib_match:
            contrib_text = contrib_match.group(1)
            # Extract names from links
            names = re.findall(r'\[([^\]]+)\]', contrib_text)
            authors.extend(names)
        
        return list(set(authors)) if authors else None
    
    def build_codemeta(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Build CodeMeta structure from extracted metadata."""
        codemeta = {
            "@context": "https://codemeta.github.io/terms/",
            "@type": "SoftwareSourceCode",
        }
        
        # Map metadata to CodeMeta properties
        if 'name' in metadata:
            codemeta['name'] = metadata['name']
        
        if 'url' in metadata:
            codemeta['url'] = metadata['url']
        
        if 'codeRepository' in metadata:
            codemeta['codeRepository'] = metadata['codeRepository']
        
        if 'description' in metadata and metadata['description']:
            codemeta['description'] = metadata['description']
            # Also add as abstract
            codemeta['abstract'] = metadata['description'][:200]
        
        if 'programmingLanguage' in metadata and metadata['programmingLanguage']:
            codemeta['programmingLanguage'] = metadata['programmingLanguage']
        
        if 'license' in metadata and metadata['license']:
            codemeta['license'] = metadata['license']
        
        if 'keywords' in metadata and metadata['keywords']:
            codemeta['keywords'] = metadata['keywords']
        
        # Add aggregate rating based on stars
        stars = metadata.get('stars', 0)
        rating_value = self._calculate_rating(stars)
        codemeta['aggregateRating'] = {
            "@type": "AggregateRating",
            "ratingValue": rating_value,
            "bestRating": 5,
            "worstRating": 0,
            "ratingCount": stars,
            "name": f"GitHub Stars ({stars})"
        }
        
        # Add repository statistics
        if 'commits' in metadata:
            codemeta['softwareVersion'] = f"Commits: {metadata['commits']}"
        
        # Add dates
        if 'created' in metadata:
            codemeta['dateCreated'] = metadata['created']
        
        if 'updated' in metadata:
            codemeta['dateModified'] = metadata['updated']
        
        if 'pushed' in metadata:
            codemeta['datePublished'] = metadata['pushed']
        
        # Add author information
        if 'authors' in metadata and metadata['authors']:
            codemeta['author'] = [{'name': author} for author in metadata['authors']]
        
        return codemeta
    
    def _calculate_rating(self, stars: int) -> float:
        """Calculate rating from star count."""
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
