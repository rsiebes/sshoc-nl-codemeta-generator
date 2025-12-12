"""
CodeMeta Build Instructions Module

This module extracts build and compilation instructions from a GitHub repository.
It searches for build scripts, Makefiles, CI/CD configurations, and documentation.
"""

from typing import Dict, Optional
from src.github_api import parse_repository_url, fetch_file_content
import re


def extract_from_makefile(owner: str, repo: str) -> Optional[str]:
    """
    Extract build instructions from Makefile.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: Build instructions if found.
    """
    try:
        makefile = fetch_file_content(owner, repo, "Makefile")
        if not makefile:
            return None

        # Look for common build targets
        build_targets = []
        for line in makefile.split('\n'):
            # Match target definitions (lines starting with non-whitespace followed by colon)
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_-]*:', line):
                target = line.split(':')[0].strip()
                if target and target not in ['.PHONY', '.DEFAULT']:
                    build_targets.append(target)

        if build_targets:
            # Prioritize common build targets
            priority_targets = ['build', 'install', 'compile', 'all', 'test']
            for target in priority_targets:
                if target in build_targets:
                    return f"make {target}"
            
            # Return first build target if no priority match
            return f"make {build_targets[0]}"

        return None

    except Exception:
        return None


def extract_from_setup_py(owner: str, repo: str) -> Optional[str]:
    """
    Extract build instructions from setup.py.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: Build instructions if found.
    """
    try:
        setup_py = fetch_file_content(owner, repo, "setup.py")
        if not setup_py:
            return None

        # Check if it's a setuptools project
        if 'setup(' in setup_py or 'setuptools' in setup_py:
            return "python setup.py build"

        return None

    except Exception:
        return None


def extract_from_pyproject_toml(owner: str, repo: str) -> Optional[str]:
    """
    Extract build instructions from pyproject.toml.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: Build instructions if found.
    """
    try:
        pyproject = fetch_file_content(owner, repo, "pyproject.toml")
        if not pyproject:
            return None

        # Check for build system
        if 'build-backend' in pyproject or '[build-system]' in pyproject:
            # Check for specific build tools
            if 'poetry' in pyproject:
                return "poetry build"
            elif 'flit' in pyproject:
                return "flit build"
            elif 'hatchling' in pyproject:
                return "hatch build"
            else:
                return "python -m build"

        return None

    except Exception:
        return None


def extract_from_package_json(owner: str, repo: str) -> Optional[str]:
    """
    Extract build instructions from package.json.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: Build instructions if found.
    """
    try:
        package_json = fetch_file_content(owner, repo, "package.json")
        if not package_json:
            return None

        # Look for build script
        build_match = re.search(r'"build"\s*:\s*"([^"]+)"', package_json)
        if build_match:
            script = build_match.group(1)
            return f"npm run build  # {script}"

        # Look for scripts section
        if '"scripts"' in package_json:
            return "npm run build"

        return None

    except Exception:
        return None


def extract_from_cargo_toml(owner: str, repo: str) -> Optional[str]:
    """
    Extract build instructions from Cargo.toml (Rust).

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: Build instructions if found.
    """
    try:
        cargo_toml = fetch_file_content(owner, repo, "Cargo.toml")
        if not cargo_toml:
            return None

        if '[package]' in cargo_toml:
            return "cargo build --release"

        return None

    except Exception:
        return None


def extract_from_build_gradle(owner: str, repo: str) -> Optional[str]:
    """
    Extract build instructions from build.gradle (Java/Gradle).

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: Build instructions if found.
    """
    try:
        build_gradle = fetch_file_content(owner, repo, "build.gradle")
        if not build_gradle:
            return None

        if 'plugins' in build_gradle or 'apply plugin' in build_gradle:
            return "./gradlew build"

        return None

    except Exception:
        return None


def extract_from_pom_xml(owner: str, repo: str) -> Optional[str]:
    """
    Extract build instructions from pom.xml (Java/Maven).

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: Build instructions if found.
    """
    try:
        pom_xml = fetch_file_content(owner, repo, "pom.xml")
        if not pom_xml:
            return None

        if '<project' in pom_xml:
            return "mvn clean install"

        return None

    except Exception:
        return None


def extract_from_readme(owner: str, repo: str) -> Optional[str]:
    """
    Extract build instructions from README.md.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: Build instructions if found.
    """
    try:
        readme = fetch_file_content(owner, repo, "README.md")
        if not readme:
            return None

        # Look for build/installation section
        build_section = re.search(
            r'#+\s*(?:Build|Installation|Getting Started|Setup|Compile|Compilation)\s*\n(.*?)(?:\n#+|\Z)',
            readme,
            re.IGNORECASE | re.DOTALL
        )

        if build_section:
            section_text = build_section.group(1)
            
            # Look for code blocks with build commands
            code_blocks = re.findall(r'```(?:bash|shell|sh|zsh)?\n(.*?)\n```', section_text, re.DOTALL)
            if code_blocks:
                # Return first code block as build instructions
                instructions = code_blocks[0].strip()
                # Limit to first line or first command
                first_line = instructions.split('\n')[0]
                if first_line:
                    return first_line

        return None

    except Exception:
        return None


def extract_from_contributing(owner: str, repo: str) -> Optional[str]:
    """
    Extract build instructions from CONTRIBUTING.md.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: Build instructions if found.
    """
    try:
        contributing = fetch_file_content(owner, repo, "CONTRIBUTING.md")
        if not contributing:
            contributing = fetch_file_content(owner, repo, ".github/CONTRIBUTING.md")
        
        if not contributing:
            return None

        # Look for build/setup section
        build_section = re.search(
            r'#+\s*(?:Build|Setup|Development|Getting Started|Local Setup)\s*\n(.*?)(?:\n#+|\Z)',
            contributing,
            re.IGNORECASE | re.DOTALL
        )

        if build_section:
            section_text = build_section.group(1)
            
            # Look for code blocks
            code_blocks = re.findall(r'```(?:bash|shell|sh|zsh)?\n(.*?)\n```', section_text, re.DOTALL)
            if code_blocks:
                instructions = code_blocks[0].strip()
                first_line = instructions.split('\n')[0]
                if first_line:
                    return first_line

        return None

    except Exception:
        return None


def get(repository_url: str) -> Dict:
    """
    Extract build instructions from a GitHub repository.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'buildInstructions' key if found.
    """
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    # Try to extract build instructions from various sources
    # Priority order: Makefile, setup.py, pyproject.toml, package.json, Cargo.toml, build.gradle, pom.xml, README, CONTRIBUTING
    
    build_instructions = None
    
    # Try Makefile
    build_instructions = extract_from_makefile(owner, repo)
    if build_instructions:
        return {"buildInstructions": build_instructions}
    
    # Try setup.py
    build_instructions = extract_from_setup_py(owner, repo)
    if build_instructions:
        return {"buildInstructions": build_instructions}
    
    # Try pyproject.toml
    build_instructions = extract_from_pyproject_toml(owner, repo)
    if build_instructions:
        return {"buildInstructions": build_instructions}
    
    # Try package.json
    build_instructions = extract_from_package_json(owner, repo)
    if build_instructions:
        return {"buildInstructions": build_instructions}
    
    # Try Cargo.toml
    build_instructions = extract_from_cargo_toml(owner, repo)
    if build_instructions:
        return {"buildInstructions": build_instructions}
    
    # Try build.gradle
    build_instructions = extract_from_build_gradle(owner, repo)
    if build_instructions:
        return {"buildInstructions": build_instructions}
    
    # Try pom.xml
    build_instructions = extract_from_pom_xml(owner, repo)
    if build_instructions:
        return {"buildInstructions": build_instructions}
    
    # Try README
    build_instructions = extract_from_readme(owner, repo)
    if build_instructions:
        return {"buildInstructions": build_instructions}
    
    # Try CONTRIBUTING
    build_instructions = extract_from_contributing(owner, repo)
    if build_instructions:
        return {"buildInstructions": build_instructions}
    
    return {}
