"""Module 42: funding - Extract funding information"""
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class FundingExtractor:
    def __init__(self, repo_data: Dict[str, Any]):
        self.repo_data = repo_data

    def extract(self) -> Optional[List[str]]:
        funding = []
        
        # Check for FUNDING.yml file reference
        if "funding_yml" in str(self.repo_data).lower():
            funding.append("GitHub Sponsors")
        
        return funding if funding else None

def extract(repo_data: Dict[str, Any], repo_files: Dict[str, str] = None, **kwargs) -> Optional[List[str]]:
    try:
        extractor = FundingExtractor(repo_data)
        return extractor.extract()
    except Exception as e:
        logger.error(f"Error extracting funding: {str(e)}")
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
        return {"funding": result} if result else {}
    except Exception as e:
        logger.error(f"Error in get function: {str(e)}")
        return {}
