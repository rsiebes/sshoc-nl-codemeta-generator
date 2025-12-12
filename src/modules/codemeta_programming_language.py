"""
CodeMeta Programming Language Property Module

Extracts the primary programming languages used in a GitHub repository.
Supports multiple strategies including GitHub API, file analysis, and configuration files.

CodeMeta Property: programmingLanguage
Type: Text or array of Text
Description: The primary programming language(s) used to develop the software.
"""

import os
import re
from typing import Dict, List, Optional
from src.github_api import fetch_file_content, fetch_repository_languages, parse_repository_url


def normalize_language(language: str) -> str:
    """
    Normalize a programming language name to standard format.

    Args:
        language (str): The language name to normalize.

    Returns:
        str: The normalized language name.
    """
    if not language:
        return ""

    # Remove extra whitespace
    language = language.strip()

    # Common language name mappings
    language_mappings = {
        "python": "Python",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "java": "Java",
        "c++": "C++",
        "c#": "C#",
        "c": "C",
        "rust": "Rust",
        "go": "Go",
        "golang": "Go",
        "ruby": "Ruby",
        "php": "PHP",
        "swift": "Swift",
        "kotlin": "Kotlin",
        "scala": "Scala",
        "r": "R",
        "matlab": "MATLAB",
        "julia": "Julia",
        "perl": "Perl",
        "lua": "Lua",
        "groovy": "Groovy",
        "haskell": "Haskell",
        "clojure": "Clojure",
        "elixir": "Elixir",
        "erlang": "Erlang",
        "objective-c": "Objective-C",
        "objective-c++": "Objective-C++",
        "vb.net": "VB.NET",
        "visual basic": "VB.NET",
        "f#": "F#",
        "fsharp": "F#",
        "dart": "Dart",
        "coffeescript": "CoffeeScript",
        "shell": "Shell",
        "bash": "Bash",
        "zsh": "Zsh",
        "powershell": "PowerShell",
        "html": "HTML",
        "css": "CSS",
        "scss": "SCSS",
        "sass": "Sass",
        "less": "Less",
        "sql": "SQL",
        "plsql": "PL/SQL",
        "tsql": "T-SQL",
        "xml": "XML",
        "json": "JSON",
        "yaml": "YAML",
        "toml": "TOML",
        "markdown": "Markdown",
        "tex": "TeX",
        "latex": "LaTeX",
        "dockerfile": "Dockerfile",
        "makefile": "Makefile",
        "cmake": "CMake",
        "gradle": "Gradle",
        "maven": "Maven",
        "npm": "npm",
        "yarn": "Yarn",
        "pip": "pip",
    }

    # Check if language is in mappings (case-insensitive)
    lower_lang = language.lower()
    if lower_lang in language_mappings:
        return language_mappings[lower_lang]

    # Return original language with proper capitalization
    return language.capitalize()


def extract_from_github_api(repository_url: str) -> List[str]:
    """
    Extract programming languages from GitHub API.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        List[str]: List of programming languages.
    """
    try:
        owner, repo = parse_repository_url(repository_url)
        if owner and repo:
            languages_dict = fetch_repository_languages(owner, repo)
            if languages_dict:
                languages = list(languages_dict.keys())
                return [normalize_language(lang) for lang in languages if lang]
    except Exception:
        pass

    return []


def extract_from_package_json(repository_url: str) -> List[str]:
    """
    Extract programming languages from package.json.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        List[str]: List of programming languages.
    """
    try:
        owner, repo = parse_repository_url(repository_url)
        if owner and repo:
            content = fetch_file_content(owner, repo, "package.json")
        if content:
            import json
            data = json.loads(content)

            languages = []

            # Check for engines field
            if "engines" in data:
                if "node" in data["engines"]:
                    languages.append("JavaScript")

            # Check for keywords
            if "keywords" in data:
                keywords = data.get("keywords", [])
                if isinstance(keywords, list):
                    for keyword in keywords:
                        if keyword and keyword.lower() in ["typescript", "coffeescript"]:
                            languages.append(normalize_language(keyword))

            return list(set(languages))  # Remove duplicates
    except Exception:
        pass

    return []


def extract_from_setup_py(repository_url: str) -> List[str]:
    """
    Extract programming languages from setup.py.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        List[str]: List of programming languages.
    """
    try:
        owner, repo = parse_repository_url(repository_url)
        if owner and repo:
            content = fetch_file_content(owner, repo, "setup.py")
        if content:
            # Always Python if setup.py exists
            return ["Python"]
    except Exception:
        pass

    return []


def extract_from_pyproject_toml(repository_url: str) -> List[str]:
    """
    Extract programming languages from pyproject.toml.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        List[str]: List of programming languages.
    """
    try:
        owner, repo = parse_repository_url(repository_url)
        if owner and repo:
            content = fetch_file_content(owner, repo, "pyproject.toml")
        if content:
            # Check for Python version specification
            if "python" in content.lower():
                return ["Python"]
    except Exception:
        pass

    return []


def extract_from_cargo_toml(repository_url: str) -> List[str]:
    """
    Extract programming languages from Cargo.toml.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        List[str]: List of programming languages.
    """
    try:
        owner, repo = parse_repository_url(repository_url)
        if owner and repo:
            content = fetch_file_content(owner, repo, "Cargo.toml")
        if content:
            # Cargo.toml indicates Rust project
            return ["Rust"]
    except Exception:
        pass

    return []


def extract_from_gemfile(repository_url: str) -> List[str]:
    """
    Extract programming languages from Gemfile.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        List[str]: List of programming languages.
    """
    try:
        owner, repo = parse_repository_url(repository_url)
        if owner and repo:
            content = fetch_file_content(owner, repo, "Gemfile")
        if content:
            # Gemfile indicates Ruby project
            return ["Ruby"]
    except Exception:
        pass

    return []


def extract_from_composer_json(repository_url: str) -> List[str]:
    """
    Extract programming languages from composer.json.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        List[str]: List of programming languages.
    """
    try:
        owner, repo = parse_repository_url(repository_url)
        if owner and repo:
            content = fetch_file_content(owner, repo, "composer.json")
        if content:
            # composer.json indicates PHP project
            return ["PHP"]
    except Exception:
        pass

    return []


def extract_from_pom_xml(repository_url: str) -> List[str]:
    """
    Extract programming languages from pom.xml.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        List[str]: List of programming languages.
    """
    try:
        owner, repo = parse_repository_url(repository_url)
        if owner and repo:
            content = fetch_file_content(owner, repo, "pom.xml")
        if content:
            # pom.xml indicates Java/Maven project
            return ["Java"]
    except Exception:
        pass

    return []


def extract_from_build_gradle(repository_url: str) -> List[str]:
    """
    Extract programming languages from build.gradle.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        List[str]: List of programming languages.
    """
    try:
        owner, repo = parse_repository_url(repository_url)
        if owner and repo:
            content = fetch_file_content(owner, repo, "build.gradle")
        if content:
            # build.gradle indicates Java/Gradle project
            return ["Java"]
    except Exception:
        pass

    return []


def extract_from_go_mod(repository_url: str) -> List[str]:
    """
    Extract programming languages from go.mod.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        List[str]: List of programming languages.
    """
    try:
        owner, repo = parse_repository_url(repository_url)
        if owner and repo:
            content = fetch_file_content(owner, repo, "go.mod")
        if content:
            # go.mod indicates Go project
            return ["Go"]
    except Exception:
        pass

    return []


def get(repository_url: str) -> Dict:
    """
    Extract programming language(s) from a GitHub repository.

    Uses a prioritized multi-strategy approach:
    1. GitHub API (most reliable)
    2. Configuration files (setup.py, package.json, Cargo.toml, etc.)

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'programmingLanguage' key containing language(s).
              Returns empty dict if no languages found.
    """
    languages = []

    # Strategy 1: GitHub API (highest priority)
    api_languages = extract_from_github_api(repository_url)
    if api_languages:
        languages.extend(api_languages)

    # Strategy 2: Configuration files (if no API results)
    if not languages:
        # Try Python projects
        py_langs = extract_from_setup_py(repository_url)
        if py_langs:
            languages.extend(py_langs)

        py_langs = extract_from_pyproject_toml(repository_url)
        if py_langs:
            languages.extend(py_langs)

        # Try JavaScript/Node.js projects
        js_langs = extract_from_package_json(repository_url)
        if js_langs:
            languages.extend(js_langs)

        # Try Rust projects
        rust_langs = extract_from_cargo_toml(repository_url)
        if rust_langs:
            languages.extend(rust_langs)

        # Try Ruby projects
        ruby_langs = extract_from_gemfile(repository_url)
        if ruby_langs:
            languages.extend(ruby_langs)

        # Try PHP projects
        php_langs = extract_from_composer_json(repository_url)
        if php_langs:
            languages.extend(php_langs)

        # Try Java projects
        java_langs = extract_from_pom_xml(repository_url)
        if java_langs:
            languages.extend(java_langs)

        java_langs = extract_from_build_gradle(repository_url)
        if java_langs:
            languages.extend(java_langs)

        # Try Go projects
        go_langs = extract_from_go_mod(repository_url)
        if go_langs:
            languages.extend(go_langs)

    # Remove duplicates while preserving order
    seen = set()
    unique_languages = []
    for lang in languages:
        if lang and lang not in seen:
            seen.add(lang)
            unique_languages.append(lang)

    # Return result
    if unique_languages:
        # Return as single string if only one language, array if multiple
        if len(unique_languages) == 1:
            return {"programmingLanguage": unique_languages[0]}
        else:
            return {"programmingLanguage": unique_languages}

    return {}
