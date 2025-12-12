"""
CodeMeta Build Instructions Module

This module extracts detailed, machine-executable build instructions from a GitHub repository.
It searches for build scripts, Makefiles, CI/CD configurations, and documentation.
Instructions are formatted with human-readable annotations to explain each step.
"""

from typing import Dict, Optional, List
from src.github_api import parse_repository_url, fetch_file_content
import re
import json


def extract_from_makefile(owner: str, repo: str) -> Optional[List[Dict]]:
    """
    Extract build instructions from Makefile.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[List[Dict]]: List of build steps if found.
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
            selected_target = None
            
            for target in priority_targets:
                if target in build_targets:
                    selected_target = target
                    break
            
            if not selected_target:
                selected_target = build_targets[0]
            
            return [
                {
                    "step": 1,
                    "command": f"make {selected_target}",
                    "description": f"Execute the '{selected_target}' target from Makefile",
                    "annotation": "Makefile-based build system",
                    "type": "build"
                }
            ]

        return None

    except Exception:
        return None


def extract_from_setup_py(owner: str, repo: str) -> Optional[List[Dict]]:
    """
    Extract build instructions from setup.py.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[List[Dict]]: List of build steps if found.
    """
    try:
        setup_py = fetch_file_content(owner, repo, "setup.py")
        if not setup_py:
            return None

        # Check if it's a setuptools project
        if 'setup(' in setup_py or 'setuptools' in setup_py:
            return [
                {
                    "step": 1,
                    "command": "python setup.py build",
                    "description": "Build the Python package using setuptools",
                    "annotation": "Python setuptools build system",
                    "type": "build"
                },
                {
                    "step": 2,
                    "command": "python setup.py install",
                    "description": "Install the built package",
                    "annotation": "Optional: Install after building",
                    "type": "install",
                    "optional": True
                }
            ]

        return None

    except Exception:
        return None


def extract_from_pyproject_toml(owner: str, repo: str) -> Optional[List[Dict]]:
    """
    Extract build instructions from pyproject.toml.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[List[Dict]]: List of build steps if found.
    """
    try:
        pyproject = fetch_file_content(owner, repo, "pyproject.toml")
        if not pyproject:
            return None

        # Check for build system
        if 'build-backend' in pyproject or '[build-system]' in pyproject:
            steps = []
            
            # Check for specific build tools
            if 'poetry' in pyproject:
                steps = [
                    {
                        "step": 1,
                        "command": "poetry install",
                        "description": "Install project dependencies using Poetry",
                        "annotation": "Poetry dependency management",
                        "type": "dependencies"
                    },
                    {
                        "step": 2,
                        "command": "poetry build",
                        "description": "Build the package using Poetry",
                        "annotation": "Poetry build backend",
                        "type": "build"
                    }
                ]
            elif 'flit' in pyproject:
                steps = [
                    {
                        "step": 1,
                        "command": "flit install --deps develop",
                        "description": "Install project with development dependencies using Flit",
                        "annotation": "Flit dependency management",
                        "type": "dependencies"
                    },
                    {
                        "step": 2,
                        "command": "flit build",
                        "description": "Build the package using Flit",
                        "annotation": "Flit build backend",
                        "type": "build"
                    }
                ]
            elif 'hatchling' in pyproject:
                steps = [
                    {
                        "step": 1,
                        "command": "pip install -e .",
                        "description": "Install project in editable mode with dependencies",
                        "annotation": "Hatchling build backend",
                        "type": "dependencies"
                    },
                    {
                        "step": 2,
                        "command": "hatch build",
                        "description": "Build the package using Hatch",
                        "annotation": "Hatch build system",
                        "type": "build"
                    }
                ]
            else:
                steps = [
                    {
                        "step": 1,
                        "command": "pip install build",
                        "description": "Install the Python build module",
                        "annotation": "Standard Python build tools",
                        "type": "dependencies"
                    },
                    {
                        "step": 2,
                        "command": "python -m build",
                        "description": "Build the package using standard Python build system",
                        "annotation": "PEP 517/518 compliant build",
                        "type": "build"
                    }
                ]
            
            return steps if steps else None

        return None

    except Exception:
        return None


def extract_from_package_json(owner: str, repo: str) -> Optional[List[Dict]]:
    """
    Extract build instructions from package.json.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[List[Dict]]: List of build steps if found.
    """
    try:
        package_json = fetch_file_content(owner, repo, "package.json")
        if not package_json:
            return None

        steps = []
        
        # Look for install script
        steps.append({
            "step": 1,
            "command": "npm install",
            "description": "Install project dependencies from package.json",
            "annotation": "Node.js dependency management",
            "type": "dependencies"
        })
        
        # Look for build script
        build_match = re.search(r'"build"\s*:\s*"([^"]+)"', package_json)
        if build_match:
            script = build_match.group(1)
            steps.append({
                "step": 2,
                "command": "npm run build",
                "description": f"Build the project: {script}",
                "annotation": "npm build script",
                "type": "build"
            })
            return steps

        # Look for scripts section
        if '"scripts"' in package_json:
            steps.append({
                "step": 2,
                "command": "npm run build",
                "description": "Build the project using npm build script",
                "annotation": "npm build script",
                "type": "build"
            })
            return steps

        return None

    except Exception:
        return None


def extract_from_cargo_toml(owner: str, repo: str) -> Optional[List[Dict]]:
    """
    Extract build instructions from Cargo.toml (Rust).

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[List[Dict]]: List of build steps if found.
    """
    try:
        cargo_toml = fetch_file_content(owner, repo, "Cargo.toml")
        if not cargo_toml:
            return None

        if '[package]' in cargo_toml:
            return [
                {
                    "step": 1,
                    "command": "cargo build",
                    "description": "Build the Rust project in debug mode",
                    "annotation": "Rust debug build",
                    "type": "build"
                },
                {
                    "step": 2,
                    "command": "cargo build --release",
                    "description": "Build the Rust project in optimized release mode",
                    "annotation": "Rust optimized release build",
                    "type": "build",
                    "recommended": True
                },
                {
                    "step": 3,
                    "command": "cargo test",
                    "description": "Run all tests",
                    "annotation": "Optional: Run test suite",
                    "type": "test",
                    "optional": True
                }
            ]

        return None

    except Exception:
        return None


def extract_from_build_gradle(owner: str, repo: str) -> Optional[List[Dict]]:
    """
    Extract build instructions from build.gradle (Java/Gradle).

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[List[Dict]]: List of build steps if found.
    """
    try:
        build_gradle = fetch_file_content(owner, repo, "build.gradle")
        if not build_gradle:
            return None

        if 'plugins' in build_gradle or 'apply plugin' in build_gradle:
            return [
                {
                    "step": 1,
                    "command": "./gradlew clean",
                    "description": "Clean previous build artifacts",
                    "annotation": "Gradle clean task",
                    "type": "clean"
                },
                {
                    "step": 2,
                    "command": "./gradlew build",
                    "description": "Build the Java project using Gradle",
                    "annotation": "Gradle build system",
                    "type": "build"
                },
                {
                    "step": 3,
                    "command": "./gradlew test",
                    "description": "Run all tests",
                    "annotation": "Optional: Run test suite",
                    "type": "test",
                    "optional": True
                }
            ]

        return None

    except Exception:
        return None


def extract_from_pom_xml(owner: str, repo: str) -> Optional[List[Dict]]:
    """
    Extract build instructions from pom.xml (Java/Maven).

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[List[Dict]]: List of build steps if found.
    """
    try:
        pom_xml = fetch_file_content(owner, repo, "pom.xml")
        if not pom_xml:
            return None

        if '<project' in pom_xml:
            return [
                {
                    "step": 1,
                    "command": "mvn clean",
                    "description": "Clean previous build artifacts",
                    "annotation": "Maven clean phase",
                    "type": "clean"
                },
                {
                    "step": 2,
                    "command": "mvn install",
                    "description": "Build the Java project and install to local repository",
                    "annotation": "Maven build and install",
                    "type": "build"
                },
                {
                    "step": 3,
                    "command": "mvn test",
                    "description": "Run all tests",
                    "annotation": "Optional: Run test suite",
                    "type": "test",
                    "optional": True
                }
            ]

        return None

    except Exception:
        return None


def extract_from_readme(owner: str, repo: str) -> Optional[List[Dict]]:
    """
    Extract build instructions from README.md.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[List[Dict]]: List of build steps if found.
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
                # Parse commands from code block
                instructions = code_blocks[0].strip()
                commands = [cmd.strip() for cmd in instructions.split('\n') if cmd.strip() and not cmd.strip().startswith('#')]
                
                if commands:
                    steps = []
                    for idx, cmd in enumerate(commands, 1):
                        steps.append({
                            "step": idx,
                            "command": cmd,
                            "description": f"Execute: {cmd}",
                            "annotation": "From README.md build section",
                            "type": "build"
                        })
                    return steps

        return None

    except Exception:
        return None


def extract_from_contributing(owner: str, repo: str) -> Optional[List[Dict]]:
    """
    Extract build instructions from CONTRIBUTING.md.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[List[Dict]]: List of build steps if found.
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
                commands = [cmd.strip() for cmd in instructions.split('\n') if cmd.strip() and not cmd.strip().startswith('#')]
                
                if commands:
                    steps = []
                    for idx, cmd in enumerate(commands, 1):
                        steps.append({
                            "step": idx,
                            "command": cmd,
                            "description": f"Execute: {cmd}",
                            "annotation": "From CONTRIBUTING.md setup section",
                            "type": "build"
                        })
                    return steps

        return None

    except Exception:
        return None


def get(repository_url: str) -> Dict:
    """
    Extract detailed build instructions from a GitHub repository.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'buildInstructions' key containing step-by-step instructions if found.
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
