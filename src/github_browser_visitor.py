"""
Browser-based GitHub repository visitor for scraping metadata.

This module uses Selenium to visit GitHub repositories and extract metadata
from the rendered HTML pages, avoiding API rate limits.
"""

import time
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

import re


class GitHubBrowserVisitor:
    """Visit GitHub repositories and extract metadata using browser automation."""
    
    def __init__(self, headless: bool = True, timeout: int = 10, verbose: bool = False):
        """
        Initialize the GitHub browser visitor.
        
        Args:
            headless (bool): Run browser in headless mode
            timeout (int): Page load timeout in seconds
            verbose (bool): Enable verbose logging
        """
        self.headless = headless
        self.timeout = timeout
        self.verbose = verbose
        self.driver = None
        self.logger = self._setup_logger()
        
        if not SELENIUM_AVAILABLE:
            self.logger.warning("Selenium not available, using fallback mode")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging."""
        logger = logging.getLogger(__name__)
        if self.verbose:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.WARNING)
        return logger
    
    def initialize_driver(self) -> bool:
        """Initialize the Selenium WebDriver."""
        if not SELENIUM_AVAILABLE:
            self.logger.warning("Selenium not available")
            return False
        
        try:
            options = Options()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            self.driver = webdriver.Chrome(options=options)
            self.logger.info("WebDriver initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            return False
    
    def visit_repository(self, repo_url: str) -> Optional[str]:
        """
        Visit a GitHub repository and extract page content.
        
        Args:
            repo_url (str): The GitHub repository URL
            
        Returns:
            Optional[str]: The page content as text, or None if failed
        """
        if not self.driver:
            self.logger.warning("Driver not initialized")
            return None
        
        try:
            self.logger.info(f"Visiting {repo_url}")
            self.driver.get(repo_url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Get page content
            page_content = self.driver.page_source
            
            self.logger.info(f"Successfully retrieved {repo_url}")
            return page_content
        
        except Exception as e:
            self.logger.error(f"Failed to visit {repo_url}: {e}")
            return None
    
    def extract_metadata_from_page(self, repo_url: str) -> Optional[Dict[str, Any]]:
        """
        Visit a repository and extract metadata from the page.
        
        Args:
            repo_url (str): The GitHub repository URL
            
        Returns:
            Optional[Dict[str, Any]]: Extracted metadata or None
        """
        if not self.driver:
            if not self.initialize_driver():
                return None
        
        page_content = self.visit_repository(repo_url)
        if not page_content:
            return None
        
        return self._parse_page_content(page_content, repo_url)
    
    def _parse_page_content(self, html_content: str, repo_url: str) -> Dict[str, Any]:
        """Parse HTML content and extract metadata."""
        metadata = {
            'url': repo_url,
            'codeRepository': repo_url,
        }
        
        # Extract repository name from URL
        parts = repo_url.rstrip('/').split('/')
        if len(parts) >= 2:
            metadata['name'] = parts[-1]
            metadata['owner'] = parts[-2]
        
        # Extract description
        desc = self._extract_from_html(html_content, r'<p[^>]*data-test-id="repo-header-description"[^>]*>([^<]+)</p>')
        if desc:
            metadata['description'] = desc
        
        # Extract stars
        stars_match = self._extract_from_html(html_content, r'(\d+)\s+Stars?')
        if stars_match:
            try:
                metadata['stars'] = int(stars_match.replace(',', ''))
            except ValueError:
                pass
        
        # Extract forks
        forks_match = self._extract_from_html(html_content, r'(\d+)\s+Forks?')
        if forks_match:
            try:
                metadata['forks'] = int(forks_match.replace(',', ''))
            except ValueError:
                pass
        
        # Extract language
        lang_match = self._extract_from_html(html_content, r'<span[^>]*itemprop="programmingLanguage"[^>]*>([^<]+)</span>')
        if lang_match:
            metadata['programmingLanguage'] = [lang_match.strip()]
        
        # Extract license
        license_match = self._extract_from_html(html_content, r'<a[^>]*href="/[^/]+/[^/]+/blob/[^/]+/LICENSE[^"]*"[^>]*>([^<]+)</a>')
        if license_match:
            metadata['license'] = {'name': license_match.strip()}
        
        # Extract topics
        topics = self._extract_topics_from_html(html_content)
        if topics:
            metadata['keywords'] = topics
        
        return metadata
    
    def _extract_from_html(self, html: str, pattern: str) -> Optional[str]:
        """Extract text from HTML using regex."""
        match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return None
    
    def _extract_topics_from_html(self, html: str) -> Optional[list]:
        """Extract topics from HTML."""
        topics = []
        
        # Look for topic links
        topic_pattern = r'<a[^>]*href="/topics/([^"]+)"[^>]*>([^<]+)</a>'
        matches = re.findall(topic_pattern, html)
        
        for topic_id, topic_name in matches:
            topics.append(topic_name.strip())
        
        return topics if topics else None
    
    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            self.logger.info("WebDriver closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class BatchGitHubScraper:
    """Scrape metadata for multiple GitHub repositories efficiently."""
    
    def __init__(self, verbose: bool = False, delay: float = 1.0):
        """
        Initialize the batch scraper.
        
        Args:
            verbose (bool): Enable verbose logging
            delay (float): Delay between requests in seconds
        """
        self.verbose = verbose
        self.delay = delay
        self.cache = {}
        self.logger = logging.getLogger(__name__)
    
    def scrape_repositories(self, repo_urls: list) -> Dict[str, Dict[str, Any]]:
        """
        Scrape metadata for multiple repositories.
        
        Args:
            repo_urls (list): List of repository URLs
            
        Returns:
            Dict[str, Dict[str, Any]]: Metadata by repository URL
        """
        results = {}
        
        if not SELENIUM_AVAILABLE:
            self.logger.warning("Selenium not available, using fallback")
            return results
        
        with GitHubBrowserVisitor(headless=True, verbose=self.verbose) as visitor:
            for i, repo_url in enumerate(repo_urls, 1):
                print(f"[{i}/{len(repo_urls)}] Scraping {repo_url.split('/')[-1]:<30}", end=' ', flush=True)
                
                try:
                    metadata = visitor.extract_metadata_from_page(repo_url)
                    if metadata:
                        results[repo_url] = metadata
                        print("✓")
                    else:
                        print("✗ No metadata")
                except Exception as e:
                    print(f"✗ Error: {str(e)[:30]}")
                
                # Rate limiting
                time.sleep(self.delay)
        
        return results
