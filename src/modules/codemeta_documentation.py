"""Module 39: documentation - Extract documentation URLs"""
import logging
from typing import Dict, Any, Optional, Union, List

logger = logging.getLogger(__name__)

class DocumentationExtractor:
    def __init__(self, repo_data: Dict[str, Any]):
        self.repo_data = repo_data
        self.topics = repo_data.get("topics", []) or []
        self.homepage = repo_data.get("homepage", "")

    def extract(self) -> Optional[Union[str, List[str]]]:
        docs = []
        
        # Check for documentation URLs in homepage
        if self.homepage:
            if "docs" in self.homepage.lower() or "documentation" in self.homepage.lower():
                docs.append(self.homepage)
        
        # Check for common documentation patterns
        repo_url = self.repo_data.get("html_url", "")
        if repo_url:
            common_docs = [
                f"{repo_url}/wiki",
                f"{repo_url}/blob/main/docs",
                f"{repo_url}/blob/main/README.md",
            ]
            docs.extend(common_docs)
        
        return docs[0] if len(docs) == 1 else (docs if docs else None)

def extract(repo_data: Dict[str, Any], repo_files: Dict[str, str] = None, **kwargs) -> Optional[Union[str, List[str]]]:
    try:
        extractor = DocumentationExtractor(repo_data)
        return extractor.extract()
    except Exception as e:
        logger.error(f"Error extracting documentation: {str(e)}")
        return None

def get(repository_url: str) -> Dict[str, Optional[Union[str, List[str]]]]:
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
        return {"documentation": result} if result else {}
    except Exception as e:
        logger.error(f"Error in get function: {str(e)}")
        return {}
