"""Module 41: fileFormat - Extract supported file formats"""
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class FileFormatExtractor:
    def __init__(self, repo_data: Dict[str, Any]):
        self.repo_data = repo_data
        self.topics = repo_data.get("topics", []) or []
        self.description = repo_data.get("description", "")

    def extract(self) -> Optional[List[str]]:
        formats = []
        
        # Common file format keywords
        format_keywords = {
            "json": "application/json",
            "xml": "application/xml",
            "csv": "text/csv",
            "pdf": "application/pdf",
            "image": "image/*",
            "video": "video/*",
            "audio": "audio/*",
            "rdf": "application/rdf+xml",
            "turtle": "text/turtle",
            "jsonld": "application/ld+json",
        }
        
        text = (self.description + " " + " ".join(self.topics)).lower()
        for keyword, mime_type in format_keywords.items():
            if keyword in text:
                formats.append(mime_type)
        
        return list(set(formats)) if formats else None

def extract(repo_data: Dict[str, Any], repo_files: Dict[str, str] = None, **kwargs) -> Optional[List[str]]:
    try:
        extractor = FileFormatExtractor(repo_data)
        return extractor.extract()
    except Exception as e:
        logger.error(f"Error extracting file format: {str(e)}")
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
        return {"fileFormat": result} if result else {}
    except Exception as e:
        logger.error(f"Error in get function: {str(e)}")
        return {}
