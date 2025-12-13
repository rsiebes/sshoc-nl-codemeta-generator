"""
CodeMeta citation Module

Extracts citation information according to CodeMeta 3.1 standard.
The citation property describes academic or technical publications that cite
or describe the software.

This module extracts citation information from:
1. CITATION.cff file (Citation File Format)
2. README file mentions of papers/publications
3. GitHub release notes
4. Repository topics related to papers

Returns:
    str: Single citation string
    list: Multiple citations if applicable
    None: If no citation data can be determined
"""

import logging
import re
from typing import Dict, Any, Optional, Union, List

logger = logging.getLogger(__name__)


class CitationExtractor:
    """Extracts citation information from GitHub repository metadata."""

    def __init__(self, repo_data: Dict[str, Any], repo_files: Dict[str, str] = None):
        """
        Initialize the CitationExtractor.

        Args:
            repo_data: Dictionary containing repository metadata from GitHub API
            repo_files: Dictionary containing repository file contents
        """
        self.repo_data = repo_data
        self.repo_files = repo_files or {}
        self.description = repo_data.get("description", "")

    def extract(self) -> Optional[Union[str, List[str]]]:
        """
        Extract citation information from repository metadata.

        Returns:
            str: Single citation
            list: Multiple citations if applicable
            None: If no citation data can be determined
        """
        citations = []

        # Check for CITATION.cff file
        citation_cff = self._extract_from_citation_cff()
        if citation_cff:
            citations.extend(citation_cff if isinstance(citation_cff, list) else [citation_cff])

        # Check for citation information in README
        citation_readme = self._extract_from_readme()
        if citation_readme:
            citations.extend(citation_readme if isinstance(citation_readme, list) else [citation_readme])

        # Check for DOI or arXiv references in description
        citation_desc = self._extract_from_description()
        if citation_desc:
            citations.extend(citation_desc if isinstance(citation_desc, list) else [citation_desc])

        # Remove duplicates while preserving order
        seen = set()
        unique_citations = []
        for citation in citations:
            if citation not in seen:
                seen.add(citation)
                unique_citations.append(citation)

        if len(unique_citations) == 0:
            logger.debug("No citations found")
            return None
        elif len(unique_citations) == 1:
            return unique_citations[0]
        else:
            return unique_citations

    def _extract_from_citation_cff(self) -> Optional[Union[str, List[str]]]:
        """
        Extract citation from CITATION.cff file.

        Returns:
            str or list: Citation information from CITATION.cff
            None: If no CITATION.cff file found
        """
        if "CITATION.cff" not in self.repo_files:
            return None

        cff_content = self.repo_files.get("CITATION.cff", "")
        if not cff_content:
            return None

        # Extract title from CITATION.cff
        title_match = re.search(r'title:\s*["\']?([^"\'\n]+)["\']?', cff_content)
        if title_match:
            title = title_match.group(1).strip()
            logger.info(f"Found citation in CITATION.cff: {title}")
            return title

        return None

    def _extract_from_readme(self) -> Optional[Union[str, List[str]]]:
        """
        Extract citation information from README file.

        Returns:
            str or list: Citation information from README
            None: If no citation found in README
        """
        readme_content = self.repo_files.get("README.md", "") or self.repo_files.get("README", "")
        if not readme_content:
            return None

        citations = []

        # Look for DOI references
        doi_pattern = r'(?:doi|DOI):\s*(?:https?://)?(?:dx\.)?(?:doi\.org/)?([0-9.]+/[^\s\)]+)'
        doi_matches = re.findall(doi_pattern, readme_content)
        for doi in doi_matches:
            citations.append(f"https://doi.org/{doi}")

        # Look for arXiv references
        arxiv_pattern = r'(?:arxiv|arXiv):\s*([0-9.]+)'
        arxiv_matches = re.findall(arxiv_pattern, readme_content)
        for arxiv in arxiv_matches:
            citations.append(f"https://arxiv.org/abs/{arxiv}")

        # Look for "Cite as" or "Citation" sections
        cite_pattern = r'(?:cite|citation)[\s\w]*:?\s*([^\n]+)'
        cite_matches = re.findall(cite_pattern, readme_content, re.IGNORECASE)
        for cite in cite_matches[:2]:  # Limit to first 2
            cite_text = cite.strip()
            if len(cite_text) > 10 and len(cite_text) < 500:
                citations.append(cite_text)

        if citations:
            logger.info(f"Found {len(citations)} citations in README")
            return citations if len(citations) > 1 else citations[0]

        return None

    def _extract_from_description(self) -> Optional[Union[str, List[str]]]:
        """
        Extract citation information from repository description.

        Returns:
            str or list: Citation information from description
            None: If no citation found in description
        """
        if not self.description:
            return None

        citations = []

        # Look for DOI references
        doi_pattern = r'(?:doi|DOI):\s*(?:https?://)?(?:dx\.)?(?:doi\.org/)?([0-9.]+/[^\s\)]+)'
        doi_matches = re.findall(doi_pattern, self.description)
        for doi in doi_matches:
            citations.append(f"https://doi.org/{doi}")

        # Look for arXiv references
        arxiv_pattern = r'(?:arxiv|arXiv):\s*([0-9.]+)'
        arxiv_matches = re.findall(arxiv_pattern, self.description)
        for arxiv in arxiv_matches:
            citations.append(f"https://arxiv.org/abs/{arxiv}")

        if citations:
            logger.info(f"Found {len(citations)} citations in description")
            return citations if len(citations) > 1 else citations[0]

        return None


def extract(repo_data: Dict[str, Any], repo_files: Dict[str, str] = None, **kwargs) -> Optional[Union[str, List[str]]]:
    """
    Extract citation information from repository metadata.

    Args:
        repo_data: Dictionary containing repository metadata from GitHub API
        repo_files: Dictionary containing repository file contents (optional)
        **kwargs: Additional arguments (ignored)

    Returns:
        str: Single citation
        list: Multiple citations if applicable
        None: If no citation data can be determined
    """
    try:
        extractor = CitationExtractor(repo_data, repo_files)
        result = extractor.extract()

        if result:
            logger.info(f"Extracted citation(s)")
            return result
        else:
            logger.debug("No citations found")
            return None

    except Exception as e:
        logger.error(f"Error extracting citation: {str(e)}")
        return None


def get(repository_url: str) -> Dict[str, Optional[Union[str, List[str]]]]:
    """
    Extract citation from a GitHub repository.

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'citation' property and its value.
              Returns an empty dict if no citation can be extracted.
    """
    try:
        from src.github_api import parse_repository_url, fetch_repository_info, fetch_file_content
        from src.utils import normalize_url

        repository_url = normalize_url(repository_url)
        owner, repo = parse_repository_url(repository_url)
        if not owner or not repo:
            return {}

        repo_data = fetch_repository_info(owner, repo)
        if not repo_data:
            return {}

        # Try to fetch CITATION.cff and README files
        repo_files = {}
        try:
            citation_cff = fetch_file_content(owner, repo, "CITATION.cff")
            if citation_cff:
                repo_files["CITATION.cff"] = citation_cff
        except:
            pass

        try:
            readme = fetch_file_content(owner, repo, "README.md")
            if readme:
                repo_files["README.md"] = readme
        except:
            pass

        result = extract(repo_data, repo_files)

        if result:
            return {"citation": result}
        else:
            return {}

    except Exception as e:
        logger.error(f"Error in get function: {str(e)}")
        return {}
