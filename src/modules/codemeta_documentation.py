"""
CodeMeta Documentation Module

This module extracts documentation information from a GitHub repository.
It detects documentation platforms, formats, and locations.
"""

from typing import Dict, Optional, List
from src.github_api import parse_repository_url, fetch_file_content
import re


def detect_documentation_platforms(owner: str, repo: str) -> List[str]:
    """
    Detect documentation platforms used in the repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected documentation platforms.
    """
    platforms = []
    
    # Check for Sphinx (Python documentation)
    try:
        sphinx_config = fetch_file_content(owner, repo, "docs/conf.py")
        if sphinx_config:
            platforms.append("Sphinx")
    except Exception:
        pass
    
    # Check for MkDocs
    try:
        mkdocs_config = fetch_file_content(owner, repo, "mkdocs.yml")
        if mkdocs_config:
            platforms.append("MkDocs")
    except Exception:
        pass
    
    # Check for Doxygen
    try:
        doxygen_config = fetch_file_content(owner, repo, "Doxyfile")
        if doxygen_config:
            platforms.append("Doxygen")
    except Exception:
        pass
    
    # Check for Javadoc (Java)
    try:
        pom_xml = fetch_file_content(owner, repo, "pom.xml")
        if pom_xml and "maven-javadoc-plugin" in pom_xml:
            platforms.append("Javadoc")
    except Exception:
        pass
    
    # Check for GitBook
    try:
        gitbook_config = fetch_file_content(owner, repo, "book.json")
        if gitbook_config:
            platforms.append("GitBook")
    except Exception:
        pass
    
    # Check for Docusaurus
    try:
        docusaurus_config = fetch_file_content(owner, repo, "docusaurus.config.js")
        if docusaurus_config:
            platforms.append("Docusaurus")
    except Exception:
        pass
    
    # Check for Hugo
    try:
        hugo_config = fetch_file_content(owner, repo, "config.toml")
        if hugo_config and "hugo" in hugo_config.lower():
            platforms.append("Hugo")
    except Exception:
        pass
    
    # Check for Jekyll
    try:
        jekyll_config = fetch_file_content(owner, repo, "_config.yml")
        if jekyll_config:
            platforms.append("Jekyll")
    except Exception:
        pass
    
    # Check for Rustdoc (Rust)
    try:
        cargo_toml = fetch_file_content(owner, repo, "Cargo.toml")
        if cargo_toml:
            platforms.append("Rustdoc")
    except Exception:
        pass
    
    # Check for Javadoc/Gradle
    try:
        build_gradle = fetch_file_content(owner, repo, "build.gradle")
        if build_gradle and "javadoc" in build_gradle.lower():
            platforms.append("Javadoc")
    except Exception:
        pass
    
    return list(set(platforms))


def detect_documentation_formats(owner: str, repo: str) -> List[str]:
    """
    Detect documentation formats used in the repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected documentation formats.
    """
    formats = []
    
    # Check for Markdown documentation
    try:
        readme = fetch_file_content(owner, repo, "README.md")
        if readme:
            formats.append("Markdown")
    except Exception:
        pass
    
    # Check for reStructuredText (Sphinx)
    try:
        sphinx_conf = fetch_file_content(owner, repo, "docs/conf.py")
        if sphinx_conf:
            formats.append("reStructuredText")
    except Exception:
        pass
    
    # Check for AsciiDoc
    try:
        asciidoc = fetch_file_content(owner, repo, "README.adoc")
        if asciidoc:
            formats.append("AsciiDoc")
    except Exception:
        pass
    
    # Check for HTML documentation
    try:
        html_docs = fetch_file_content(owner, repo, "docs/index.html")
        if html_docs:
            formats.append("HTML")
    except Exception:
        pass
    
    # Check for PDF documentation
    try:
        pdf_docs = fetch_file_content(owner, repo, "docs")
        if pdf_docs and ".pdf" in str(pdf_docs).lower():
            formats.append("PDF")
    except Exception:
        pass
    
    # Check for Org-mode (Emacs)
    try:
        org_docs = fetch_file_content(owner, repo, "README.org")
        if org_docs:
            formats.append("Org-mode")
    except Exception:
        pass
    
    # Check for plain text
    try:
        text_docs = fetch_file_content(owner, repo, "README.txt")
        if text_docs:
            formats.append("Plain Text")
    except Exception:
        pass
    
    # Check for RST (reStructuredText)
    try:
        rst_docs = fetch_file_content(owner, repo, "README.rst")
        if rst_docs:
            formats.append("reStructuredText")
    except Exception:
        pass
    
    return list(set(formats))


def detect_documentation_locations(owner: str, repo: str) -> List[str]:
    """
    Detect documentation locations in the repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected documentation locations.
    """
    locations = []
    
    # Check for docs directory
    try:
        docs_dir = fetch_file_content(owner, repo, "docs")
        if docs_dir:
            locations.append("docs/")
    except Exception:
        pass
    
    # Check for doc directory
    try:
        doc_dir = fetch_file_content(owner, repo, "doc")
        if doc_dir:
            locations.append("doc/")
    except Exception:
        pass
    
    # Check for documentation directory
    try:
        documentation_dir = fetch_file_content(owner, repo, "documentation")
        if documentation_dir:
            locations.append("documentation/")
    except Exception:
        pass
    
    # Check for website directory
    try:
        website_dir = fetch_file_content(owner, repo, "website")
        if website_dir:
            locations.append("website/")
    except Exception:
        pass
    
    # Check for README files
    try:
        readme = fetch_file_content(owner, repo, "README.md")
        if readme:
            locations.append("README.md")
    except Exception:
        pass
    
    # Check for CONTRIBUTING
    try:
        contributing = fetch_file_content(owner, repo, "CONTRIBUTING.md")
        if contributing:
            locations.append("CONTRIBUTING.md")
    except Exception:
        pass
    
    # Check for CHANGELOG
    try:
        changelog = fetch_file_content(owner, repo, "CHANGELOG.md")
        if changelog:
            locations.append("CHANGELOG.md")
    except Exception:
        pass
    
    # Check for wiki
    try:
        wiki = fetch_file_content(owner, repo, "wiki")
        if wiki:
            locations.append("wiki/")
    except Exception:
        pass
    
    return list(set(locations))


def detect_external_documentation(owner: str, repo: str) -> List[str]:
    """
    Detect external documentation platforms.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected external documentation platforms.
    """
    platforms = []
    
    # Check for ReadTheDocs configuration
    try:
        rtd_config = fetch_file_content(owner, repo, ".readthedocs.yml")
        if rtd_config:
            platforms.append("ReadTheDocs")
    except Exception:
        pass
    
    # Check for GitHub Pages
    try:
        github_pages = fetch_file_content(owner, repo, ".github/workflows")
        if github_pages:
            platforms.append("GitHub Pages")
    except Exception:
        pass
    
    # Check for Netlify
    try:
        netlify_config = fetch_file_content(owner, repo, "netlify.toml")
        if netlify_config:
            platforms.append("Netlify")
    except Exception:
        pass
    
    # Check for Vercel
    try:
        vercel_config = fetch_file_content(owner, repo, "vercel.json")
        if vercel_config:
            platforms.append("Vercel")
    except Exception:
        pass
    
    return list(set(platforms))


def extract_documentation_info(owner: str, repo: str) -> Dict:
    """
    Extract comprehensive documentation information.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Dict: Dictionary with documentation information.
    """
    doc_info = {
        "platforms": detect_documentation_platforms(owner, repo),
        "formats": detect_documentation_formats(owner, repo),
        "locations": detect_documentation_locations(owner, repo),
        "externalPlatforms": detect_external_documentation(owner, repo)
    }
    
    return doc_info


def format_documentation_info(doc_info: Dict) -> str:
    """
    Format documentation information as a human-readable string.

    Args:
        doc_info (Dict): Documentation information dictionary.

    Returns:
        str: Formatted documentation information.
    """
    parts = []
    
    if doc_info.get("platforms"):
        parts.append(f"Platforms: {', '.join(doc_info['platforms'])}")
    
    if doc_info.get("formats"):
        parts.append(f"Formats: {', '.join(doc_info['formats'])}")
    
    if doc_info.get("locations"):
        parts.append(f"Locations: {', '.join(doc_info['locations'])}")
    
    if doc_info.get("externalPlatforms"):
        parts.append(f"External: {', '.join(doc_info['externalPlatforms'])}")
    
    return " | ".join(parts) if parts else None


def get(repository_url: str) -> Dict:
    """
    Extract documentation information from a GitHub repository.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'documentation' key if documentation info found.
    """
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}
    
    doc_info = extract_documentation_info(owner, repo)
    
    # Only return if we found something
    if (doc_info.get("platforms") or doc_info.get("formats") or 
        doc_info.get("locations") or doc_info.get("externalPlatforms")):
        return {"documentation": doc_info}
    
    return {}
