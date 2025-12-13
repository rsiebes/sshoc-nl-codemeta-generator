"""
CodeMeta Executable Module

This module extracts executable files and entry points from a GitHub repository.
It detects command-line tools, scripts, and executable entry points.
"""

from typing import Dict, List, Optional
from src.github_api import parse_repository_url, fetch_file_content
import re


def detect_cli_entry_points(owner: str, repo: str) -> List[str]:
    """
    Detect CLI entry points from package configuration files.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected CLI entry points.
    """
    entry_points = []
    
    # Check setup.py for entry_points
    try:
        setup_py = fetch_file_content(owner, repo, "setup.py")
        if setup_py:
            # Extract entry_points console_scripts
            pattern = r"entry_points\s*=\s*\{[^}]*console_scripts[^}]*\}"
            matches = re.findall(pattern, setup_py, re.DOTALL)
            if matches:
                # Extract individual script names
                script_pattern = r"['\"]([^'\"]+)\s*=[^'\"]*['\"]"
                for match in matches:
                    scripts = re.findall(script_pattern, match)
                    entry_points.extend(scripts)
    except Exception:
        pass
    
    # Check pyproject.toml for scripts
    try:
        pyproject = fetch_file_content(owner, repo, "pyproject.toml")
        if pyproject:
            # Extract scripts section
            if "[project.scripts]" in pyproject or "[tool.poetry.scripts]" in pyproject:
                lines = pyproject.split('\n')
                in_scripts = False
                for line in lines:
                    if "[project.scripts]" in line or "[tool.poetry.scripts]" in line:
                        in_scripts = True
                    elif in_scripts and line.startswith("["):
                        in_scripts = False
                    elif in_scripts and "=" in line:
                        script_name = line.split("=")[0].strip().strip('"\'')
                        if script_name and not script_name.startswith("#"):
                            entry_points.append(script_name)
    except Exception:
        pass
    
    # Check package.json for bin field
    try:
        package_json = fetch_file_content(owner, repo, "package.json")
        if package_json:
            # Extract bin field
            pattern = r'"bin"\s*:\s*\{([^}]*)\}'
            matches = re.findall(pattern, package_json)
            if matches:
                for match in matches:
                    # Extract script names
                    script_pattern = r'"([^"]+)"\s*:'
                    scripts = re.findall(script_pattern, match)
                    entry_points.extend(scripts)
    except Exception:
        pass
    
    # Check Cargo.toml for binary targets
    try:
        cargo_toml = fetch_file_content(owner, repo, "Cargo.toml")
        if cargo_toml:
            # Extract [[bin]] sections
            pattern = r"\[\[bin\]\].*?name\s*=\s*['\"]([^'\"]+)['\"]"
            matches = re.findall(pattern, cargo_toml, re.DOTALL)
            entry_points.extend(matches)
    except Exception:
        pass
    
    return list(set(entry_points))


def detect_shell_scripts(owner: str, repo: str) -> List[str]:
    """
    Detect shell scripts and executable files.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected shell scripts.
    """
    scripts = []
    
    # Common script locations
    script_dirs = ["bin", "scripts", "tools", "cmd"]
    
    for script_dir in script_dirs:
        try:
            dir_content = fetch_file_content(owner, repo, script_dir)
            if dir_content:
                # Extract script names from directory listing
                # This is a simplified approach - in reality we'd need directory listing
                scripts.append(f"{script_dir}/*")
        except Exception:
            pass
    
    return list(set(scripts))


def detect_executable_files(owner: str, repo: str) -> List[str]:
    """
    Detect executable files in the repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected executable files.
    """
    executables = []
    
    # Detect CLI entry points
    cli_points = detect_cli_entry_points(owner, repo)
    executables.extend(cli_points)
    
    # Detect shell scripts
    shell_scripts = detect_shell_scripts(owner, repo)
    executables.extend(shell_scripts)
    
    # Check for Makefile targets
    try:
        makefile = fetch_file_content(owner, repo, "Makefile")
        if makefile:
            # Extract target names
            pattern = r"^([a-zA-Z_][a-zA-Z0-9_-]*):"
            targets = re.findall(pattern, makefile, re.MULTILINE)
            # Filter out common non-executable targets
            non_exec = {"all", "clean", "test", "build", "install", "help"}
            exec_targets = [t for t in targets if t not in non_exec]
            executables.extend(exec_targets)
    except Exception:
        pass
    
    # Check for executable scripts in root
    try:
        # Common executable names
        common_execs = ["cli.py", "main.py", "run.py", "start.py", "server.py"]
        for exec_name in common_execs:
            exec_content = fetch_file_content(owner, repo, exec_name)
            if exec_content and ("#!/" in exec_content or "__main__" in exec_content):
                executables.append(exec_name)
    except Exception:
        pass
    
    return list(set(executables))


def format_executable_info(executables: List[str]) -> str:
    """
    Format executable information as a human-readable string.

    Args:
        executables (List[str]): List of executables.

    Returns:
        str: Formatted executable information.
    """
    if not executables:
        return None
    
    return ", ".join(sorted(executables))


def get(repository_url: str) -> Dict:
    """
    Extract executable information from a GitHub repository.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'executable' key if executables found.
    """
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}
    
    executables = detect_executable_files(owner, repo)
    
    # Only return if we found something
    if executables:
        return {"executable": executables}
    
    return {}
