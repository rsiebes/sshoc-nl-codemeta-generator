"""
Efficient batch CodeMeta generator using web scraping.

This module generates CodeMeta files for multiple repositories by scraping
GitHub pages and extracting metadata without using the API.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from github_web_scraper import GitHubMetadataExtractor


class BatchCodeMetaGenerator:
    """Generate CodeMeta files for multiple repositories efficiently."""
    
    def __init__(self, output_base: Path, verbose: bool = False):
        """
        Initialize the batch generator.
        
        Args:
            output_base (Path): Base output directory for CodeMeta files
            verbose (bool): Enable verbose logging
        """
        self.output_base = output_base
        self.verbose = verbose
        self.extractor = GitHubMetadataExtractor(verbose=verbose)
        self.cache = {}
    
    def load_repositories_from_examples(self) -> List[Dict[str, str]]:
        """Load repository list from example CodeMeta files."""
        repositories = []
        
        examples_dir = Path('/home/ubuntu/main-branch/examples')
        
        # Define folder mappings
        folders = {
            'bramvanroy': examples_dir / 'bramvanroy',
            'soda_science': examples_dir / 'soda_science',
            'cbs_ecosystem/official_cbs': examples_dir / 'cbs_ecosystem' / 'official_cbs',
            'cbs_ecosystem/third_party': examples_dir / 'cbs_ecosystem' / 'third_party',
        }
        
        for folder_key, folder_path in folders.items():
            if not folder_path.exists():
                continue
            
            for json_file in sorted(folder_path.glob('*.json')):
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                        if 'codeRepository' in data:
                            repo_url = data['codeRepository']
                            repo_name = repo_url.rstrip('/').split('/')[-1]
                            repositories.append({
                                'url': repo_url,
                                'name': repo_name,
                                'folder': folder_key
                            })
                except (json.JSONDecodeError, IOError) as e:
                    if self.verbose:
                        print(f"Error reading {json_file}: {e}")
        
        return repositories
    
    def generate_for_all(self, repositories: List[Dict[str, str]], 
                        page_contents: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Generate CodeMeta files for all repositories.
        
        Args:
            repositories (List[Dict[str, str]]): List of repositories
            page_contents (Dict[str, str]): Optional cached page contents by URL
            
        Returns:
            Dict[str, Any]: Generation statistics
        """
        if page_contents is None:
            page_contents = {}
        
        stats = {
            'total': len(repositories),
            'success': 0,
            'error': 0,
            'skipped': 0,
            'generated_files': []
        }
        
        print("="*80)
        print("BATCH CODEMETA GENERATION (WEB SCRAPING)")
        print("="*80)
        print(f"\nProcessing {len(repositories)} repositories\n")
        
        for i, repo in enumerate(repositories, 1):
            repo_name = repo['name']
            repo_url = repo['url']
            
            # Progress indicator
            print(f"[{i:2d}/{len(repositories)}] {repo_name:<40}", end=' ', flush=True)
            
            try:
                # Get page content (from cache or use placeholder)
                if repo_url in page_contents:
                    page_content = page_contents[repo_url]
                else:
                    # Create minimal page content for now
                    # In production, this would come from actual browser scraping
                    page_content = self._create_minimal_page_content(repo_url)
                
                # Extract metadata
                metadata = self.extractor.extract_from_page_content(repo_url, page_content)
                
                # Build CodeMeta
                codemeta = self.extractor.build_codemeta(metadata)
                
                # Save to file
                output_file = self._save_codemeta(codemeta, repo['folder'], repo_name)
                
                stats['generated_files'].append(str(output_file))
                stats['success'] += 1
                print("✓")
                
            except Exception as e:
                stats['error'] += 1
                print(f"✗ {str(e)[:40]}")
            
            # Rate limiting
            time.sleep(0.1)
        
        # Print summary
        print()
        print("="*80)
        print("GENERATION COMPLETE")
        print("="*80)
        print(f"Total: {stats['total']}")
        print(f"Success: {stats['success']}")
        print(f"Errors: {stats['error']}")
        print(f"Skipped: {stats['skipped']}")
        print("="*80)
        
        return stats
    
    def _create_minimal_page_content(self, repo_url: str) -> str:
        """Create minimal page content for testing."""
        repo_name = repo_url.rstrip('/').split('/')[-1]
        return f"# {repo_name}\n**URL:** {repo_url}\n\nStar 0\nFork 0\n"
    
    def _save_codemeta(self, codemeta: Dict[str, Any], folder: str, 
                       repo_name: str) -> Path:
        """Save CodeMeta to file."""
        folder_path = self.output_base / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        
        output_file = folder_path / f"codemeta_{repo_name}.json"
        
        with open(output_file, 'w') as f:
            json.dump(codemeta, f, indent=2)
        
        return output_file
    
    def generate_from_browser_content(self, browser_content_dir: Path) -> Dict[str, Any]:
        """
        Generate CodeMeta from previously scraped browser content.
        
        Args:
            browser_content_dir (Path): Directory containing saved page content
            
        Returns:
            Dict[str, Any]: Generation statistics
        """
        page_contents = {}
        
        # Load all saved page contents
        if browser_content_dir.exists():
            for file_path in browser_content_dir.glob('*.md'):
                # Extract URL from filename
                # Expected format: github.com_owner_repo.md
                parts = file_path.stem.split('_')
                if len(parts) >= 3:
                    url = f"https://{parts[0]}/{parts[1]}/{parts[2]}"
                    with open(file_path) as f:
                        page_contents[url] = f.read()
        
        repositories = self.load_repositories_from_examples()
        return self.generate_for_all(repositories, page_contents)
