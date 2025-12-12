"""
CodeMeta Runtime Platform Module

This module extracts runtime platform requirements from a GitHub repository.
It detects runtime environments like Python, Node.js, Java, Ruby, Go, etc.
"""

from typing import Dict, List, Optional, Set
from src.github_api import (
    parse_repository_url,
    fetch_file_content,
)
import re


# Runtime platform patterns with versions
RUNTIME_PATTERNS = {
    # Python
    "Python": [
        r"python\s*(?:3\.1[0-2]|3\.9|3\.8|3\.7|3\.6|2\.7)?",
        r"python\s*>=\s*(?:3\.\d+)",
        r"python_requires\s*=\s*['\"]>=\s*(?:3\.\d+)",
    ],
    # Node.js / JavaScript
    "Node.js": [
        r"node\.?js?\s*(?:18|17|16|14|12|10)?",
        r"node\s*(?:>=\s*)?(?:18|17|16|14|12|10)",
        r"\"node\"\s*:\s*\"(?:>=\s*)?(?:18|17|16|14|12)",
    ],
    # Java
    "Java": [
        r"java\s*(?:17|16|15|14|13|12|11|8)?",
        r"jdk\s*(?:17|16|15|14|13|12|11|8)?",
        r"<source>\s*(?:17|16|15|14|13|12|11|8)",
        r"maven\.compiler\.source",
        r"maven\.compiler\.target",
        r"sourcecompatibility",
        r"targetcompatibility",
    ],
    # Ruby
    "Ruby": [
        r"ruby\s*(?:3\.[0-2]|2\.7|2\.6|2\.5)?",
        r"ruby\s*>=\s*(?:2\.\d+)",
    ],
    # Go
    "Go": [
        r"go\s*(?:1\.2[0-1]|1\.19|1\.18|1\.17|1\.16|1\.15)?",
        r"go\s*>=\s*(?:1\.\d+)",
    ],
    # Rust
    "Rust": [
        r"rust\s*(?:1\.\d+)?",
        r"rustc\s*(?:1\.\d+)?",
        r"\[package\]",
        r"Cargo\.toml",
    ],
    # PHP
    "PHP": [
        r"php\s*(?:8\.[0-2]|7\.[4]|7\.[3]|7\.[2])?",
        r"php\s*>=\s*(?:\d+\.\d+)",
    ],
    # .NET / C#
    ".NET": [
        r"\.net\s*(?:6|5|framework)",
        r"dotnet\s*(?:6|5|framework)",
        r"csharp|c#",
    ],
    # Perl
    "Perl": [
        r"perl\s*(?:5\.\d+)?",
        r"perl\s*>=\s*(?:5\.\d+)",
    ],
    # R
    "R": [
        r"\br\s*(?:4\.\d+|3\.\d+)?",
        r"r-project",
    ],
    # Lua
    "Lua": [
        r"lua\s*(?:5\.[1-4])?",
    ],
    # Swift
    "Swift": [
        r"swift\s*(?:5\.\d+)?",
    ],
    # Kotlin
    "Kotlin": [
        r"kotlin\s*(?:1\.\d+)?",
    ],
    # TypeScript
    "TypeScript": [
        r"typescript",
        r"tsx?",
    ],
}


def extract_runtime_platforms(text: str) -> Set[str]:
    """
    Extract runtime platforms with versions from text.

    Args:
        text (str): Text to search for runtime platform information.

    Returns:
        Set[str]: Set of detected runtime platforms with versions.
    """
    detected_platforms = set()
    text_lower = text.lower()

    for platform_name, patterns in RUNTIME_PATTERNS.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                detected_platforms.add(platform_name)
                # Extract version if present
                matched_text = match.group(0)
                version_match = re.search(r'\d+\.?\d*', matched_text)
                if version_match:
                    version = version_match.group(0)
                    # Add platform with version if it's meaningful
                    if version and len(version) > 1:
                        platform_with_version = f"{platform_name} {version}"
                        detected_platforms.add(platform_with_version)
                break

    return detected_platforms


def detect_from_package_files(owner: str, repo: str) -> List[str]:
    """
    Detect runtime platforms from package files.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected runtime platforms.
    """
    try:
        detected_platforms = set()

        # Check package.json (Node.js)
        package_json = fetch_file_content(owner, repo, "package.json")
        if package_json:
            detected_platforms.update(extract_runtime_platforms(package_json))

        # Check setup.py (Python)
        setup_py = fetch_file_content(owner, repo, "setup.py")
        if setup_py:
            detected_platforms.update(extract_runtime_platforms(setup_py))

        # Check pyproject.toml (Python)
        pyproject_toml = fetch_file_content(owner, repo, "pyproject.toml")
        if pyproject_toml:
            detected_platforms.update(extract_runtime_platforms(pyproject_toml))

        # Check requirements.txt (Python)
        requirements_txt = fetch_file_content(owner, repo, "requirements.txt")
        if requirements_txt:
            detected_platforms.update(extract_runtime_platforms(requirements_txt))

        # Check pom.xml (Java/Maven)
        pom_xml = fetch_file_content(owner, repo, "pom.xml")
        if pom_xml:
            detected_platforms.update(extract_runtime_platforms(pom_xml))

        # Check build.gradle (Java/Gradle)
        build_gradle = fetch_file_content(owner, repo, "build.gradle")
        if build_gradle:
            detected_platforms.update(extract_runtime_platforms(build_gradle))

        # Check Gemfile (Ruby)
        gemfile = fetch_file_content(owner, repo, "Gemfile")
        if gemfile:
            detected_platforms.update(extract_runtime_platforms(gemfile))

        # Check go.mod (Go)
        go_mod = fetch_file_content(owner, repo, "go.mod")
        if go_mod:
            detected_platforms.update(extract_runtime_platforms(go_mod))

        # Check Cargo.toml (Rust)
        cargo_toml = fetch_file_content(owner, repo, "Cargo.toml")
        if cargo_toml:
            detected_platforms.update(extract_runtime_platforms(cargo_toml))

        return sorted(list(detected_platforms))

    except Exception:
        return []


def detect_from_readme(owner: str, repo: str) -> List[str]:
    """
    Detect runtime platforms from README.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected runtime platforms.
    """
    try:
        readme_content = fetch_file_content(owner, repo, "README.md")
        if not readme_content:
            return []

        detected_platforms = extract_runtime_platforms(readme_content)
        return sorted(list(detected_platforms))

    except Exception:
        return []


def detect_from_ci_config(owner: str, repo: str) -> List[str]:
    """
    Detect runtime platforms from CI/CD configuration.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected runtime platforms.
    """
    try:
        detected_platforms = set()

        # Check GitHub Actions workflow
        workflow_content = fetch_file_content(owner, repo, ".github/workflows/main.yml")
        if not workflow_content:
            workflow_content = fetch_file_content(owner, repo, ".github/workflows/ci.yml")

        if workflow_content:
            detected_platforms.update(extract_runtime_platforms(workflow_content))

        # Check Travis CI config
        travis_content = fetch_file_content(owner, repo, ".travis.yml")
        if travis_content:
            detected_platforms.update(extract_runtime_platforms(travis_content))

        # Check Circle CI config
        circleci_content = fetch_file_content(owner, repo, ".circleci/config.yml")
        if circleci_content:
            detected_platforms.update(extract_runtime_platforms(circleci_content))

        return sorted(list(detected_platforms))

    except Exception:
        return []


def get(repository_url: str) -> Dict:
    """
    Extract runtime platform requirements from a GitHub repository.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'runtimePlatform' key if runtime info is found, empty dict otherwise.
    """
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    # Detect runtime platforms from multiple sources
    platforms_set = set()

    # Try package files detection
    package_platforms = detect_from_package_files(owner, repo)
    platforms_set.update(package_platforms)

    # Try README detection
    readme_platforms = detect_from_readme(owner, repo)
    platforms_set.update(readme_platforms)

    # Try CI/CD config detection
    ci_platforms = detect_from_ci_config(owner, repo)
    platforms_set.update(ci_platforms)

    if not platforms_set:
        return {}

    return {
        "runtimePlatform": sorted(list(platforms_set))
    }
