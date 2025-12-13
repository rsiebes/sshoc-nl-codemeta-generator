"""Module 40: executable - Extract executable/binary information"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ExecutableExtractor:
    def __init__(self, repo_data: Dict[str, Any]):
        self.repo_data = repo_data
        self.topics = repo_data.get("topics", []) or []
        self.language = repo_data.get("language", "")

    def extract(self) -> Optional[str]:
        # Check for executable-related topics
        executable_keywords = ["executable", "binary", "cli", "command-line", "tool"]
        for topic in self.topics:
            if any(kw in topic.lower() for kw in executable_keywords):
                return "true"
        
        # Check language for compiled languages
        if self.language in ["Go", "Rust", "C", "C++"]:
            return "true"
        
        return None

def extract(repo_data: Dict[str, Any], repo_files: Dict[str, str] = None, **kwargs) -> Optional[str]:
    try:
        extractor = ExecutableExtractor(repo_data)
        return extractor.extract()
    except Exception as e:
        logger.error(f"Error extracting executable: {str(e)}")
        return None

def get(repository_url: str) -> Dict[str, Optional[str]]:
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
        return {"executable": result} if result else {}
    except Exception as e:
        logger.error(f"Error in get function: {str(e)}")
        return {}
