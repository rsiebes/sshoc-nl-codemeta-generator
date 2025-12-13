"""Module 47: readme - Extract README file URL"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ReadmeExtractor:
    def __init__(self, repo_data: Dict[str, Any]):
        self.repo_data = repo_data

    def extract(self) -> Optional[str]:
        repo_url = self.repo_data.get("html_url", "")
        if repo_url:
            return f"{repo_url}/blob/main/README.md"
        return None

def extract(repo_data: Dict[str, Any], repo_files: Dict[str, str] = None, **kwargs) -> Optional[str]:
    try:
        return ReadmeExtractor(repo_data).extract()
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
        return {"readme": result} if result else {}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {}
