"""
CodeMeta Input Method Module

This module extracts input methods and interfaces from a GitHub repository.
It detects how users interact with the software (CLI, GUI, API, Web, etc.).
"""

from typing import Dict, List, Optional
from src.github_api import parse_repository_url, fetch_file_content
import re


def detect_cli_interface(owner: str, repo: str) -> bool:
    """
    Detect if the software has a command-line interface.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        bool: True if CLI interface detected.
    """
    # Check for CLI indicators
    cli_indicators = [
        "argparse", "click", "typer", "docopt", "fire",  # Python
        "commander", "yargs", "minimist", "oclif",  # Node.js
        "clap", "structopt",  # Rust
        "cobra", "urfave/cli",  # Go
    ]
    
    try:
        # Check setup.py
        setup_py = fetch_file_content(owner, repo, "setup.py")
        if setup_py:
            for indicator in cli_indicators:
                if indicator in setup_py.lower():
                    return True
        
        # Check pyproject.toml
        pyproject = fetch_file_content(owner, repo, "pyproject.toml")
        if pyproject:
            for indicator in cli_indicators:
                if indicator in pyproject.lower():
                    return True
        
        # Check package.json
        package_json = fetch_file_content(owner, repo, "package.json")
        if package_json:
            for indicator in cli_indicators:
                if indicator in package_json.lower():
                    return True
        
        # Check Cargo.toml
        cargo_toml = fetch_file_content(owner, repo, "Cargo.toml")
        if cargo_toml:
            for indicator in cli_indicators:
                if indicator in cargo_toml.lower():
                    return True
        
        # Check for bin/ or scripts/ directories
        bin_content = fetch_file_content(owner, repo, "bin")
        if bin_content:
            return True
        
        scripts_content = fetch_file_content(owner, repo, "scripts")
        if scripts_content:
            return True
    except Exception:
        pass
    
    return False


def detect_gui_interface(owner: str, repo: str) -> bool:
    """
    Detect if the software has a graphical user interface.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        bool: True if GUI interface detected.
    """
    gui_indicators = [
        "tkinter", "pyqt", "pyside", "wxpython", "gtk",  # Python
        "electron", "qt", "gtk", "wxwidgets",  # General
        "imgui", "dear imgui", "nuklear",  # C/C++
        "druid", "iced", "fltk-rs",  # Rust
        "fyne", "gotk3",  # Go
    ]
    
    try:
        # Check setup.py
        setup_py = fetch_file_content(owner, repo, "setup.py")
        if setup_py:
            for indicator in gui_indicators:
                if indicator in setup_py.lower():
                    return True
        
        # Check pyproject.toml
        pyproject = fetch_file_content(owner, repo, "pyproject.toml")
        if pyproject:
            for indicator in gui_indicators:
                if indicator in pyproject.lower():
                    return True
        
        # Check package.json
        package_json = fetch_file_content(owner, repo, "package.json")
        if package_json:
            for indicator in gui_indicators:
                if indicator in package_json.lower():
                    return True
        
        # Check for UI directories
        ui_content = fetch_file_content(owner, repo, "ui")
        if ui_content:
            return True
        
        gui_content = fetch_file_content(owner, repo, "gui")
        if gui_content:
            return True
    except Exception:
        pass
    
    return False


def detect_web_interface(owner: str, repo: str) -> bool:
    """
    Detect if the software has a web interface.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        bool: True if web interface detected.
    """
    web_indicators = [
        "flask", "django", "fastapi", "starlette",  # Python
        "express", "react", "vue", "angular", "next",  # Node.js/JavaScript
        "actix", "rocket", "axum",  # Rust
        "gin", "echo", "fiber",  # Go
        "rails", "sinatra",  # Ruby
    ]
    
    try:
        # Check setup.py
        setup_py = fetch_file_content(owner, repo, "setup.py")
        if setup_py:
            for indicator in web_indicators:
                if indicator in setup_py.lower():
                    return True
        
        # Check pyproject.toml
        pyproject = fetch_file_content(owner, repo, "pyproject.toml")
        if pyproject:
            for indicator in web_indicators:
                if indicator in pyproject.lower():
                    return True
        
        # Check package.json
        package_json = fetch_file_content(owner, repo, "package.json")
        if package_json:
            for indicator in web_indicators:
                if indicator in package_json.lower():
                    return True
        
        # Check Cargo.toml
        cargo_toml = fetch_file_content(owner, repo, "Cargo.toml")
        if cargo_toml:
            for indicator in web_indicators:
                if indicator in cargo_toml.lower():
                    return True
        
        # Check for web directories
        web_content = fetch_file_content(owner, repo, "web")
        if web_content:
            return True
        
        frontend_content = fetch_file_content(owner, repo, "frontend")
        if frontend_content:
            return True
    except Exception:
        pass
    
    return False


def detect_api_interface(owner: str, repo: str) -> bool:
    """
    Detect if the software provides an API interface.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        bool: True if API interface detected.
    """
    api_indicators = [
        "rest", "graphql", "grpc", "openapi", "swagger",
        "fastapi", "flask", "django", "express", "actix",
        "@app.route", "@api", "endpoint", "api/v",
    ]
    
    try:
        # Check README
        readme = fetch_file_content(owner, repo, "README.md")
        if readme:
            readme_lower = readme.lower()
            if "api" in readme_lower or "rest" in readme_lower or "graphql" in readme_lower:
                return True
        
        # Check setup.py
        setup_py = fetch_file_content(owner, repo, "setup.py")
        if setup_py:
            for indicator in api_indicators:
                if indicator in setup_py.lower():
                    return True
        
        # Check pyproject.toml
        pyproject = fetch_file_content(owner, repo, "pyproject.toml")
        if pyproject:
            for indicator in api_indicators:
                if indicator in pyproject.lower():
                    return True
        
        # Check for API documentation
        api_docs = fetch_file_content(owner, repo, "docs/api.md")
        if api_docs:
            return True
        
        openapi = fetch_file_content(owner, repo, "openapi.yaml")
        if openapi:
            return True
    except Exception:
        pass
    
    return False


def detect_library_interface(owner: str, repo: str) -> bool:
    """
    Detect if the software is a library/SDK for programmatic use.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        bool: True if library interface detected.
    """
    try:
        # Check if it's primarily a library
        readme = fetch_file_content(owner, repo, "README.md")
        if readme:
            readme_lower = readme.lower()
            if "library" in readme_lower or "sdk" in readme_lower or "package" in readme_lower:
                if "import" in readme_lower or "require" in readme_lower:
                    return True
        
        # Check setup.py for library indicators
        setup_py = fetch_file_content(owner, repo, "setup.py")
        if setup_py:
            if "packages=" in setup_py and "entry_points" not in setup_py:
                return True
        
        # Check pyproject.toml
        pyproject = fetch_file_content(owner, repo, "pyproject.toml")
        if pyproject:
            if "[project.scripts]" not in pyproject and "[tool.poetry.scripts]" not in pyproject:
                if "name" in pyproject:
                    return True
    except Exception:
        pass
    
    return False


def get_input_methods(owner: str, repo: str) -> List[str]:
    """
    Detect all input methods from a repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected input methods.
    """
    methods = []
    
    if detect_cli_interface(owner, repo):
        methods.append("Command-line interface")
    
    if detect_gui_interface(owner, repo):
        methods.append("Graphical user interface")
    
    if detect_web_interface(owner, repo):
        methods.append("Web interface")
    
    if detect_api_interface(owner, repo):
        methods.append("Application programming interface")
    
    if detect_library_interface(owner, repo):
        methods.append("Programmatic interface")
    
    return methods


def get(repository_url: str) -> Dict:
    """
    Extract input method information from a GitHub repository.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'inputMethod' key if methods found.
    """
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}
    
    methods = get_input_methods(owner, repo)
    
    # Only return if we found something
    if methods:
        return {"inputMethod": methods}
    
    return {}
