"""
NLP Utilities for Keyword Extraction

This module provides natural language processing utilities for extracting
meaningful keywords from repository content using NLTK and TF-IDF.
"""

import re
from typing import List, Dict, Set
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer


class KeywordExtractor:
    """Extract meaningful keywords from text using NLP techniques."""
    
    def __init__(self):
        """Initialize the keyword extractor."""
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Add common programming and technical stop words
        self.technical_stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
            'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
            'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also',
            'file', 'files', 'code', 'project', 'repository', 'repo', 'github',
            'readme', 'license', 'documentation', 'doc', 'docs', 'example',
            'examples', 'test', 'tests', 'src', 'source', 'main', 'index'
        }
        
        self.stop_words.update(self.technical_stop_words)
    
    def extract_keywords(self, texts: List[str], max_keywords: int = 10) -> List[str]:
        """
        Extract keywords from a list of texts using TF-IDF.
        
        Args:
            texts: List of text strings to analyze
            max_keywords: Maximum number of keywords to return
            
        Returns:
            List of extracted keywords
        """
        if not texts or all(not text for text in texts):
            return []
        
        # Clean and filter texts
        cleaned_texts = [self._clean_text(text) for text in texts if text]
        if not cleaned_texts:
            return []
        
        # Combine all texts for analysis
        combined_text = ' '.join(cleaned_texts)
        
        # Extract using multiple methods and combine
        tfidf_keywords = self._extract_tfidf_keywords(cleaned_texts, max_keywords * 2)
        frequency_keywords = self._extract_frequency_keywords(combined_text, max_keywords * 2)
        
        # Combine and rank keywords
        all_keywords = list(set(tfidf_keywords + frequency_keywords))
        
        # Score keywords based on multiple factors
        scored_keywords = self._score_keywords(all_keywords, combined_text)
        
        # Sort by score and return top keywords
        sorted_keywords = sorted(scored_keywords.items(), key=lambda x: x[1], reverse=True)
        
        return [kw for kw, score in sorted_keywords[:max_keywords]]
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text string
            
        Returns:
            Cleaned text string
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove code blocks (markdown)
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`[^`]+`', '', text)
        
        # Remove special characters but keep hyphens and underscores
        text = re.sub(r'[^a-z0-9\s\-_]', ' ', text)
        
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_tfidf_keywords(self, texts: List[str], max_keywords: int) -> List[str]:
        """
        Extract keywords using TF-IDF with support for technical compound terms.
        
        Preserves hyphenated and underscore terms like:
        - "spatial-analysis", "neighbor-search", "balltree"
        - "machine_learning", "data_science"
        
        Args:
            texts: List of cleaned text strings
            max_keywords: Maximum number of keywords
            
        Returns:
            List of keywords (including preserved compound terms)
        """
        try:
            # Custom token pattern that preserves hyphenated and underscore terms
            # Matches: word, word-word, word_word, word-word-word, etc.
            token_pattern = r'\b[a-z]+(?:[-_][a-z]+)*\b'
            
            # Use TF-IDF to find important terms
            vectorizer = TfidfVectorizer(
                max_features=max_keywords * 3,
                ngram_range=(1, 3),  # Unigrams, bigrams, and trigrams
                stop_words=list(self.stop_words),
                min_df=1,
                max_df=0.8,
                token_pattern=token_pattern,  # Preserve hyphenated/underscore terms
                lowercase=True
            )
            
            tfidf_matrix = vectorizer.fit_transform(texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get average TF-IDF scores across all documents
            avg_scores = tfidf_matrix.mean(axis=0).A1
            keywords_scores = list(zip(feature_names, avg_scores))
            keywords_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Return top keywords (normalize underscores to hyphens for consistency)
            keywords = [kw.replace('_', '-') for kw, score in keywords_scores[:max_keywords] if score > 0]
            return keywords
        except Exception as e:
            print(f"TF-IDF extraction error: {e}")
            sys.stdout.flush()
            return []
    
    def _extract_frequency_keywords(self, text: str, max_keywords: int) -> List[str]:
        """
        Extract keywords based on frequency.
        
        Args:
            text: Cleaned text string
            max_keywords: Maximum number of keywords
            
        Returns:
            List of keywords
        """
        # Tokenize
        tokens = word_tokenize(text)
        
        # Filter tokens - allow hyphens and underscores for compound keywords
        filtered_tokens = [
            token for token in tokens
            if token not in self.stop_words
            and len(token) > 2
            and (token.isalnum() or '-' in token or '_' in token)
        ]
        
        # Count frequencies
        freq_dist = Counter(filtered_tokens)
        
        # Get most common
        common_words = [word for word, count in freq_dist.most_common(max_keywords)]
        
        return common_words
    
    def _score_keywords(self, keywords: List[str], text: str) -> Dict[str, float]:
        """
        Score keywords based on multiple factors.
        
        Args:
            keywords: List of candidate keywords
            text: Full text for context
            
        Returns:
            Dictionary mapping keywords to scores
        """
        scored = {}
        text_lower = text.lower()
        
        for keyword in keywords:
            score = 0.0
            
            # Frequency score
            frequency = text_lower.count(keyword)
            score += min(frequency / 10.0, 1.0) * 0.4
            
            # Length score (prefer medium-length keywords)
            length = len(keyword)
            if 4 <= length <= 15:
                score += 0.3
            elif length > 15:
                score += 0.1
            
            # Hyphenation score (technical terms often have hyphens)
            if '-' in keyword or '_' in keyword:
                score += 0.2
            
            # Position score (keywords appearing early are often more important)
            first_occurrence = text_lower.find(keyword)
            if first_occurrence != -1:
                position_score = 1.0 - (first_occurrence / len(text_lower))
                score += position_score * 0.1
            
            scored[keyword] = score
        
        return scored
    
    def extract_from_repository_data(self, repo_data: Dict) -> List[str]:
        """
        Extract keywords from repository data.
        
        Args:
            repo_data: Dictionary containing repository information
            
        Returns:
            List of extracted keywords
        """
        texts = []
        
        # Extract description (high weight)
        description = repo_data.get('description') or repo_data.get('repo_description', '')
        if description:
            texts.extend([description] * 3)  # Give more weight to description
        
        # Extract README content (high weight)
        readme = repo_data.get('readme', '')
        if readme:
            # Take first 2000 characters of README
            readme_excerpt = readme[:2000]
            texts.extend([readme_excerpt] * 2)  # Give weight to README
        
        # Extract existing topics/keywords (medium weight)
        topics = repo_data.get('topics', [])
        if topics:
            if isinstance(topics, list):
                texts.append(' '.join(topics))
            elif isinstance(topics, str):
                texts.append(topics)
        
        # Extract from repository name (low weight)
        name = repo_data.get('name') or repo_data.get('repo_name', '')
        if name:
            # Split camelCase and snake_case
            name_words = re.sub(r'([A-Z])', r' \1', name).replace('_', ' ').replace('-', ' ')
            texts.append(name_words)
        
        # Extract keywords
        keywords = self.extract_keywords(texts, max_keywords=10)
        
        # Add existing topics if they're not already included
        if topics and isinstance(topics, list):
            for topic in topics[:5]:  # Limit to first 5 topics
                if topic and topic not in keywords:
                    keywords.append(topic)
        
        return keywords[:15]  # Return max 15 keywords
