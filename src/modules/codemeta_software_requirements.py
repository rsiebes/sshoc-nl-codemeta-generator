"""
CodeMeta Software Requirements Module

This module extracts software dependencies and requirements from a GitHub repository.
It detects required libraries, packages, and external software dependencies.
"""

from typing import Dict, List, Optional, Set
from src.github_api import (
    parse_repository_url,
    fetch_file_content,
)
import re


def extract_python_requirements(owner: str, repo: str) -> List[str]:
    """
    Extract Python package requirements.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of Python package requirements.
    """
    try:
        requirements = set()

        # Check requirements.txt
        requirements_txt = fetch_file_content(owner, repo, "requirements.txt")
        if requirements_txt:
            for line in requirements_txt.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (before version specifier)
                    package_name = re.split(r'[<>=!]', line)[0].strip()
                    if package_name:
                        requirements.add(f"Python package: {package_name}")

        # Check setup.py
        setup_py = fetch_file_content(owner, repo, "setup.py")
        if setup_py:
            # Look for install_requires
            install_requires_match = re.search(r'install_requires\s*=\s*\[(.*?)\]', setup_py, re.DOTALL)
            if install_requires_match:
                deps_str = install_requires_match.group(1)
                for dep in re.findall(r"['\"]([^'\"]+)['\"]", deps_str):
                    package_name = re.split(r'[<>=!]', dep)[0].strip()
                    if package_name:
                        requirements.add(f"Python package: {package_name}")

        # Check pyproject.toml
        pyproject_toml = fetch_file_content(owner, repo, "pyproject.toml")
        if pyproject_toml:
            # Look for dependencies
            deps_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', pyproject_toml, re.DOTALL)
            if deps_match:
                deps_str = deps_match.group(1)
                for dep in re.findall(r"['\"]([^'\"]+)['\"]", deps_str):
                    package_name = re.split(r'[<>=!]', dep)[0].strip()
                    if package_name:
                        requirements.add(f"Python package: {package_name}")

        return sorted(list(requirements))

    except Exception:
        return []


def extract_nodejs_requirements(owner: str, repo: str) -> List[str]:
    """
    Extract Node.js package requirements.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of Node.js package requirements.
    """
    try:
        requirements = set()

        # Check package.json
        package_json = fetch_file_content(owner, repo, "package.json")
        if package_json:
            # Extract dependencies
            deps_match = re.search(r'"dependencies"\s*:\s*\{(.*?)\}', package_json, re.DOTALL)
            if deps_match:
                deps_str = deps_match.group(1)
                for dep in re.findall(r'"([^"]+)"\s*:', deps_str):
                    if dep and not dep.startswith('@'):
                        requirements.add(f"Node.js package: {dep}")

            # Extract devDependencies
            dev_deps_match = re.search(r'"devDependencies"\s*:\s*\{(.*?)\}', package_json, re.DOTALL)
            if dev_deps_match:
                dev_deps_str = dev_deps_match.group(1)
                for dep in re.findall(r'"([^"]+)"\s*:', dev_deps_str):
                    if dep and not dep.startswith('@'):
                        requirements.add(f"Node.js dev package: {dep}")

        return sorted(list(requirements))

    except Exception:
        return []


def extract_java_requirements(owner: str, repo: str) -> List[str]:
    """
    Extract Java package requirements.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of Java package requirements.
    """
    try:
        requirements = set()

        # Check pom.xml
        pom_xml = fetch_file_content(owner, repo, "pom.xml")
        if pom_xml:
            # Extract dependencies
            for dep in re.findall(r'<artifactId>([^<]+)</artifactId>', pom_xml):
                if dep:
                    requirements.add(f"Java library: {dep}")

        # Check build.gradle
        build_gradle = fetch_file_content(owner, repo, "build.gradle")
        if build_gradle:
            # Extract dependencies
            for dep in re.findall(r"['\"]([^'\"]+:[^'\"]+:[^'\"]+)['\"]", build_gradle):
                if dep:
                    requirements.add(f"Java library: {dep}")

        return sorted(list(requirements))

    except Exception:
        return []


def extract_ruby_requirements(owner: str, repo: str) -> List[str]:
    """
    Extract Ruby gem requirements.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of Ruby gem requirements.
    """
    try:
        requirements = set()

        # Check Gemfile
        gemfile = fetch_file_content(owner, repo, "Gemfile")
        if gemfile:
            # Extract gems
            for gem in re.findall(r"gem\s+['\"]([^'\"]+)['\"]", gemfile):
                if gem:
                    requirements.add(f"Ruby gem: {gem}")

        return sorted(list(requirements))

    except Exception:
        return []


def extract_go_requirements(owner: str, repo: str) -> List[str]:
    """
    Extract Go module requirements.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of Go module requirements.
    """
    try:
        requirements = set()

        # Check go.mod
        go_mod = fetch_file_content(owner, repo, "go.mod")
        if go_mod:
            # Extract require block
            require_block = re.search(r'require\s*\(([^)]+)\)', go_mod, re.DOTALL)
            if require_block:
                block_content = require_block.group(1)
                for line in block_content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('//'):
                        parts = line.split()
                        if parts and '/' in parts[0]:
                            requirements.add(f"Go module: {parts[0]}")
            
            # Also check for single-line requires
            for match in re.finditer(r'require\s+([\w\./\-]+)\s+([\w\./\-]+)', go_mod):
                module = match.group(1)
                if module and '/' in module:
                    requirements.add(f"Go module: {module}")

        return sorted(list(requirements))

    except Exception:
        return []


def extract_rust_requirements(owner: str, repo: str) -> List[str]:
    """
    Extract Rust crate requirements.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of Rust crate requirements.
    """
    try:
        requirements = set()

        # Check Cargo.toml
        cargo_toml = fetch_file_content(owner, repo, "Cargo.toml")
        if cargo_toml:
            # Extract dependencies
            for dep in re.findall(r'(\w+)\s*=\s*["\{]', cargo_toml):
                if dep and dep not in ['package', 'dependencies', 'dev-dependencies', 'build-dependencies']:
                    requirements.add(f"Rust crate: {dep}")

        return sorted(list(requirements))

    except Exception:
        return []


def extract_system_requirements(owner: str, repo: str) -> List[str]:
    """
    Extract system-level requirements from README and documentation.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of system requirements.
    """
    try:
        requirements = set()

        # Check README
        readme = fetch_file_content(owner, repo, "README.md")
        if readme:
            # Look for common system requirements patterns
            patterns = [
                r'requires?\s+([A-Za-z0-9\.\-_]+)\s+(?:version|>=|>|==)',
                r'(?:needs?|requires?)\s+([A-Za-z0-9\.\-_]+)',
                r'(?:install|setup)\s+([A-Za-z0-9\.\-_]+)',
            ]
            for pattern in patterns:
                for match in re.finditer(pattern, readme, re.IGNORECASE):
                    req = match.group(1).strip()
                    if req and len(req) > 2:
                        requirements.add(f"System requirement: {req}")

        return sorted(list(requirements))

    except Exception:
        return []


def get(repository_url: str) -> Dict:
    """
    Extract software requirements from a GitHub repository.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'softwareRequirements' key if requirements are found, empty dict otherwise.
    """
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    # Extract requirements from multiple sources
    all_requirements = set()

    # Extract Python requirements
    python_reqs = extract_python_requirements(owner, repo)
    all_requirements.update(python_reqs)

    # Extract Node.js requirements
    nodejs_reqs = extract_nodejs_requirements(owner, repo)
    all_requirements.update(nodejs_reqs)

    # Extract Java requirements
    java_reqs = extract_java_requirements(owner, repo)
    all_requirements.update(java_reqs)

    # Extract Ruby requirements
    ruby_reqs = extract_ruby_requirements(owner, repo)
    all_requirements.update(ruby_reqs)

    # Extract Go requirements
    go_reqs = extract_go_requirements(owner, repo)
    all_requirements.update(go_reqs)

    # Extract Rust requirements
    rust_reqs = extract_rust_requirements(owner, repo)
    all_requirements.update(rust_reqs)

    # Extract system requirements
    system_reqs = extract_system_requirements(owner, repo)
    all_requirements.update(system_reqs)

    if not all_requirements:
        return {}

    return {
        "softwareRequirements": sorted(list(all_requirements))
    }
