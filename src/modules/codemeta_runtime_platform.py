"""Module 48: runtimePlatform - Extract runtime platform requirements"""
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class RuntimePlatformExtractor:
    def __init__(self, repo_data: Dict[str, Any]):
        self.repo_data = repo_data
        self.language = repo_data.get("language", "")

    def extract(self) -> Optional[List[str]]:
        platforms = []
        if self.language == "Python":
            platforms.append("Python 3.6+")
        elif self.language == "JavaScript":
            platforms.append("Node.js 12+")
        elif self.language == "Java":
            platforms.append("Java 8+")
        return platforms if platforms else None

def extract(repo_data: Dict[str, Any], repo_files: Dict[str, str] = None, **kwargs) -> Optional[List[str]]:
    try:
        return RuntimePlatformExtractor(repo_data).extract()
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return None

def get(repository_url: str) -> Dict[str, Optional[List[str]]]:
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
        return {"runtimePlatform": result} if result else {}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {}
