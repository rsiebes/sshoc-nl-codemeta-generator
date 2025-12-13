"""Module 43: inputMethod - Extract input method information"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class InputMethodExtractor:
    def __init__(self, repo_data: Dict[str, Any]):
        self.repo_data = repo_data
        self.topics = repo_data.get("topics", []) or []

    def extract(self) -> Optional[str]:
        input_methods = {"cli": "CLI", "gui": "GUI", "web": "Web", "api": "API"}
        for topic in self.topics:
            for key, value in input_methods.items():
                if key in topic.lower():
                    return value
        return None

def extract(repo_data: Dict[str, Any], repo_files: Dict[str, str] = None, **kwargs) -> Optional[str]:
    try:
        return InputMethodExtractor(repo_data).extract()
    except Exception as e:
        logger.error(f"Error: {str(e)}")
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
        return {"inputMethod": result} if result else {}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {}
