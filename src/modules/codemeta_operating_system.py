"""Module 45: operatingSystem - Extract operating system requirements"""
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class OperatingSystemExtractor:
    def __init__(self, repo_data: Dict[str, Any]):
        self.repo_data = repo_data
        self.topics = repo_data.get("topics", []) or []

    def extract(self) -> Optional[List[str]]:
        os_list = []
        os_keywords = {"windows": "Windows", "linux": "Linux", "macos": "macOS", "osx": "macOS"}
        for topic in self.topics:
            for key, value in os_keywords.items():
                if key in topic.lower():
                    if value not in os_list:
                        os_list.append(value)
        return os_list if os_list else None

def extract(repo_data: Dict[str, Any], repo_files: Dict[str, str] = None, **kwargs) -> Optional[List[str]]:
    try:
        return OperatingSystemExtractor(repo_data).extract()
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
        return {"operatingSystem": result} if result else {}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {}
