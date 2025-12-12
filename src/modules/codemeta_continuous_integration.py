"""
CodeMeta Continuous Integration Module

This module extracts continuous integration and testing information from a GitHub repository.
It detects CI/CD platforms, testing frameworks, and test coverage tools.
"""

from typing import Dict, Optional, List
from src.github_api import parse_repository_url, fetch_file_content
import re
import json


def detect_ci_platforms(owner: str, repo: str) -> List[str]:
    """
    Detect continuous integration platforms used in the repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected CI platforms.
    """
    platforms = []
    
    # Check for GitHub Actions
    try:
        workflows = fetch_file_content(owner, repo, ".github/workflows")
        if workflows:
            platforms.append("GitHub Actions")
    except Exception:
        pass
    
    # Check for Travis CI
    try:
        travis = fetch_file_content(owner, repo, ".travis.yml")
        if travis:
            platforms.append("Travis CI")
    except Exception:
        pass
    
    # Check for Circle CI
    try:
        circle = fetch_file_content(owner, repo, ".circleci/config.yml")
        if circle:
            platforms.append("Circle CI")
    except Exception:
        pass
    
    # Check for GitLab CI
    try:
        gitlab = fetch_file_content(owner, repo, ".gitlab-ci.yml")
        if gitlab:
            platforms.append("GitLab CI")
    except Exception:
        pass
    
    # Check for AppVeyor
    try:
        appveyor = fetch_file_content(owner, repo, "appveyor.yml")
        if appveyor:
            platforms.append("AppVeyor")
    except Exception:
        pass
    
    # Check for Jenkins
    try:
        jenkins = fetch_file_content(owner, repo, "Jenkinsfile")
        if jenkins:
            platforms.append("Jenkins")
    except Exception:
        pass
    
    # Check for Azure Pipelines
    try:
        azure = fetch_file_content(owner, repo, "azure-pipelines.yml")
        if azure:
            platforms.append("Azure Pipelines")
    except Exception:
        pass
    
    # Check for Drone CI
    try:
        drone = fetch_file_content(owner, repo, ".drone.yml")
        if drone:
            platforms.append("Drone CI")
    except Exception:
        pass
    
    return platforms


def detect_testing_frameworks(owner: str, repo: str) -> List[str]:
    """
    Detect testing frameworks used in the repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected testing frameworks.
    """
    frameworks = []
    
    # Check package files for test dependencies
    try:
        # Python
        requirements = fetch_file_content(owner, repo, "requirements-dev.txt")
        if requirements:
            if 'pytest' in requirements:
                frameworks.append("pytest")
            if 'unittest' in requirements:
                frameworks.append("unittest")
            if 'nose' in requirements:
                frameworks.append("nose")
            if 'tox' in requirements:
                frameworks.append("tox")
    except Exception:
        pass
    
    try:
        setup_py = fetch_file_content(owner, repo, "setup.py")
        if setup_py:
            if 'pytest' in setup_py:
                frameworks.append("pytest")
            if 'unittest' in setup_py:
                frameworks.append("unittest")
            if 'nose' in setup_py:
                frameworks.append("nose")
    except Exception:
        pass
    
    try:
        pyproject = fetch_file_content(owner, repo, "pyproject.toml")
        if pyproject:
            if 'pytest' in pyproject:
                frameworks.append("pytest")
            if 'tox' in pyproject:
                frameworks.append("tox")
    except Exception:
        pass
    
    # JavaScript/Node.js
    try:
        package_json = fetch_file_content(owner, repo, "package.json")
        if package_json:
            if 'jest' in package_json:
                frameworks.append("Jest")
            if 'mocha' in package_json:
                frameworks.append("Mocha")
            if 'jasmine' in package_json:
                frameworks.append("Jasmine")
            if 'vitest' in package_json:
                frameworks.append("Vitest")
            if 'karma' in package_json:
                frameworks.append("Karma")
    except Exception:
        pass
    
    # Java
    try:
        pom_xml = fetch_file_content(owner, repo, "pom.xml")
        if pom_xml:
            if 'junit' in pom_xml:
                frameworks.append("JUnit")
            if 'testng' in pom_xml:
                frameworks.append("TestNG")
    except Exception:
        pass
    
    try:
        build_gradle = fetch_file_content(owner, repo, "build.gradle")
        if build_gradle:
            if 'junit' in build_gradle:
                frameworks.append("JUnit")
            if 'testng' in build_gradle:
                frameworks.append("TestNG")
    except Exception:
        pass
    
    # Ruby
    try:
        gemfile = fetch_file_content(owner, repo, "Gemfile")
        if gemfile:
            if 'rspec' in gemfile:
                frameworks.append("RSpec")
            if 'minitest' in gemfile:
                frameworks.append("Minitest")
    except Exception:
        pass
    
    # Go
    try:
        go_mod = fetch_file_content(owner, repo, "go.mod")
        if go_mod:
            frameworks.append("Go testing")
    except Exception:
        pass
    
    # Rust
    try:
        cargo_toml = fetch_file_content(owner, repo, "Cargo.toml")
        if cargo_toml:
            if '[dev-dependencies]' in cargo_toml:
                frameworks.append("Rust testing")
    except Exception:
        pass
    
    # Remove duplicates
    return list(set(frameworks))


def detect_coverage_tools(owner: str, repo: str) -> List[str]:
    """
    Detect code coverage tools used in the repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected coverage tools.
    """
    tools = []
    
    try:
        # Check for coverage configuration files
        coverage_config = fetch_file_content(owner, repo, ".coveragerc")
        if coverage_config:
            tools.append("coverage.py")
    except Exception:
        pass
    
    try:
        codecov_config = fetch_file_content(owner, repo, "codecov.yml")
        if codecov_config:
            tools.append("Codecov")
    except Exception:
        pass
    
    try:
        codacy_config = fetch_file_content(owner, repo, ".codacy.yml")
        if codacy_config:
            tools.append("Codacy")
    except Exception:
        pass
    
    try:
        sonar_config = fetch_file_content(owner, repo, "sonar-project.properties")
        if sonar_config:
            tools.append("SonarQube")
    except Exception:
        pass
    
    try:
        # Check CI configs for coverage commands
        github_actions = fetch_file_content(owner, repo, ".github/workflows")
        if github_actions:
            if 'coverage' in github_actions:
                tools.append("GitHub Coverage")
            if 'codecov' in github_actions:
                tools.append("Codecov")
    except Exception:
        pass
    
    try:
        travis = fetch_file_content(owner, repo, ".travis.yml")
        if travis:
            if 'coverage' in travis:
                tools.append("coverage.py")
            if 'codecov' in travis:
                tools.append("Codecov")
    except Exception:
        pass
    
    # Remove duplicates
    return list(set(tools))


def extract_ci_info(owner: str, repo: str) -> Dict:
    """
    Extract comprehensive continuous integration information.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Dict: Dictionary with CI information.
    """
    ci_info = {
        "platforms": detect_ci_platforms(owner, repo),
        "testingFrameworks": detect_testing_frameworks(owner, repo),
        "coverageTools": detect_coverage_tools(owner, repo)
    }
    
    return ci_info


def format_ci_info(ci_info: Dict) -> str:
    """
    Format CI information as a human-readable string.

    Args:
        ci_info (Dict): CI information dictionary.

    Returns:
        str: Formatted CI information.
    """
    parts = []
    
    if ci_info.get("platforms"):
        parts.append(f"CI Platforms: {', '.join(ci_info['platforms'])}")
    
    if ci_info.get("testingFrameworks"):
        parts.append(f"Testing: {', '.join(ci_info['testingFrameworks'])}")
    
    if ci_info.get("coverageTools"):
        parts.append(f"Coverage: {', '.join(ci_info['coverageTools'])}")
    
    return " | ".join(parts) if parts else None


def get(repository_url: str) -> Dict:
    """
    Extract continuous integration information from a GitHub repository.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'continuousIntegration' key if CI info found.
    """
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}
    
    ci_info = extract_ci_info(owner, repo)
    
    # Only return if we found something
    if ci_info.get("platforms") or ci_info.get("testingFrameworks") or ci_info.get("coverageTools"):
        return {"continuousIntegration": ci_info}
    
    return {}
