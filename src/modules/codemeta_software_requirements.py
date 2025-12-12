"""
CodeMeta Software Requirements Module

This module extracts software dependencies and requirements from a GitHub repository.
It detects required libraries, packages, and external software dependencies with version ranges.
Outputs SoftwareApplication objects with minVersion and maxVersion according to CodeMeta 3.1 schema.
"""

from typing import Dict, List, Optional, Set, Tuple
from src.github_api import (
    parse_repository_url,
    fetch_file_content,
)
import re


def parse_version_specifier(spec: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse version specifier and extract min and max versions.
    
    Args:
        spec (str): Version specifier (e.g., ">=1.0,<2.0", "~=1.5", "1.0-2.0")
    
    Returns:
        Tuple[Optional[str], Optional[str]]: (min_version, max_version)
    """
    min_version = None
    max_version = None
    
    # Handle range formats: "1.0-2.0", "1.0 to 2.0"
    range_match = re.search(r'(\d+\.[\d.]+)\s*(?:to|-)(\d+\.[\d.]+)', spec)
    if range_match:
        min_version = range_match.group(1)
        max_version = range_match.group(2)
        return min_version, max_version
    
    # Handle plain version numbers (e.g., "1.0.0")
    plain_version_match = re.match(r'^(\d+\.\d+(?:\.\d+)*)$', spec.strip())
    if plain_version_match:
        min_version = plain_version_match.group(1)
        max_version = plain_version_match.group(1)
        return min_version, max_version
    
    # Handle pip version specifiers
    # >= version
    ge_match = re.search(r'>=\s*(\d+\.[\d.]*)', spec)
    if ge_match:
        min_version = ge_match.group(1)
    
    # <= version
    le_match = re.search(r'<=\s*(\d+\.[\d.]*)', spec)
    if le_match:
        max_version = le_match.group(1)
    
    # > version (exclusive)
    gt_match = re.search(r'>\s*(\d+\.[\d.]*)', spec)
    if gt_match and not ge_match:
        min_version = gt_match.group(1)
    
    # < version (exclusive)
    lt_match = re.search(r'<\s*(\d+\.[\d.]*)', spec)
    if lt_match and not le_match:
        max_version = lt_match.group(1)
    
    # == version (exact)
    eq_match = re.search(r'==\s*(\d+\.[\d.]*)', spec)
    if eq_match:
        min_version = eq_match.group(1)
        max_version = eq_match.group(1)
    
    # ~= compatible release
    compat_match = re.search(r'~=\s*(\d+\.[\d.]*)', spec)
    if compat_match:
        version = compat_match.group(1)
        parts = version.split('.')
        if len(parts) >= 2:
            min_version = version
            # ~= allows changes in the second-to-last component
            next_minor = str(int(parts[-2]) + 1)
            max_version = '.'.join(parts[:-2]) + '.' + next_minor
    
    return min_version, max_version


def create_software_requirement(name: str, version_spec: str = None) -> Dict:
    """
    Create a SoftwareApplication object for a requirement.
    
    Args:
        name (str): Name of the software requirement
        version_spec (str): Version specification string
    
    Returns:
        Dict: SoftwareApplication object with minVersion and maxVersion
    """
    req_obj = {
        "@type": "SoftwareApplication",
        "name": name
    }
    
    if version_spec:
        min_ver, max_ver = parse_version_specifier(version_spec)
        if min_ver:
            req_obj["minVersion"] = min_ver
        if max_ver:
            req_obj["maxVersion"] = max_ver
    
    return req_obj


def extract_python_requirements(owner: str, repo: str) -> List[Dict]:
    """
    Extract Python package requirements with versions.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[Dict]: List of SoftwareApplication requirement objects.
    """
    try:
        requirements = []
        seen = set()

        # Check requirements.txt
        requirements_txt = fetch_file_content(owner, repo, "requirements.txt")
        if requirements_txt:
            for line in requirements_txt.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name and version spec
                    match = re.match(r'([a-zA-Z0-9\-_.]+)\s*(.*)', line)
                    if match:
                        package_name = match.group(1)
                        version_spec = match.group(2)
                        
                        if package_name not in seen:
                            req_obj = create_software_requirement(package_name, version_spec)
                            requirements.append(req_obj)
                            seen.add(package_name)

        # Check setup.py
        setup_py = fetch_file_content(owner, repo, "setup.py")
        if setup_py:
            # Look for install_requires
            install_requires_match = re.search(r'install_requires\s*=\s*\[(.*?)\]', setup_py, re.DOTALL)
            if install_requires_match:
                deps_str = install_requires_match.group(1)
                for dep in re.findall(r"['\"]([^'\"]+)['\"]", deps_str):
                    match = re.match(r'([a-zA-Z0-9\-_.]+)\s*(.*)', dep)
                    if match:
                        package_name = match.group(1)
                        version_spec = match.group(2)
                        
                        if package_name not in seen:
                            req_obj = create_software_requirement(package_name, version_spec)
                            requirements.append(req_obj)
                            seen.add(package_name)

        # Check pyproject.toml
        pyproject_toml = fetch_file_content(owner, repo, "pyproject.toml")
        if pyproject_toml:
            # Look for dependencies
            deps_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', pyproject_toml, re.DOTALL)
            if deps_match:
                deps_str = deps_match.group(1)
                for dep in re.findall(r"['\"]([^'\"]+)['\"]", deps_str):
                    match = re.match(r'([a-zA-Z0-9\-_.]+)\s*(.*)', dep)
                    if match:
                        package_name = match.group(1)
                        version_spec = match.group(2)
                        
                        if package_name not in seen:
                            req_obj = create_software_requirement(package_name, version_spec)
                            requirements.append(req_obj)
                            seen.add(package_name)

        return sorted(requirements, key=lambda x: x.get('name', ''))

    except Exception:
        return []


def extract_nodejs_requirements(owner: str, repo: str) -> List[Dict]:
    """
    Extract Node.js package requirements with versions.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[Dict]: List of SoftwareApplication requirement objects.
    """
    try:
        requirements = []
        seen = set()

        # Check package.json
        package_json = fetch_file_content(owner, repo, "package.json")
        if package_json:
            # Extract dependencies
            deps_match = re.search(r'"dependencies"\s*:\s*\{(.*?)\}', package_json, re.DOTALL)
            if deps_match:
                deps_str = deps_match.group(1)
                for match in re.finditer(r'"([^"]+)"\s*:\s*"([^"]+)"', deps_str):
                    dep_name = match.group(1)
                    version_spec = match.group(2)
                    
                    if dep_name and not dep_name.startswith('@') and dep_name not in seen:
                        req_obj = create_software_requirement(dep_name, version_spec)
                        requirements.append(req_obj)
                        seen.add(dep_name)

            # Extract devDependencies
            dev_deps_match = re.search(r'"devDependencies"\s*:\s*\{(.*?)\}', package_json, re.DOTALL)
            if dev_deps_match:
                dev_deps_str = dev_deps_match.group(1)
                for match in re.finditer(r'"([^"]+)"\s*:\s*"([^"]+)"', dev_deps_str):
                    dep_name = match.group(1)
                    version_spec = match.group(2)
                    
                    if dep_name and not dep_name.startswith('@') and dep_name not in seen:
                        req_obj = create_software_requirement(dep_name, version_spec)
                        requirements.append(req_obj)
                        seen.add(dep_name)

        return sorted(requirements, key=lambda x: x.get('name', ''))

    except Exception:
        return []


def extract_java_requirements(owner: str, repo: str) -> List[Dict]:
    """
    Extract Java package requirements with versions.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[Dict]: List of SoftwareApplication requirement objects.
    """
    try:
        requirements = []
        seen = set()

        # Check pom.xml
        pom_xml = fetch_file_content(owner, repo, "pom.xml")
        if pom_xml:
            # Extract dependencies with versions
            for match in re.finditer(r'<artifactId>([^<]+)</artifactId>\s*(?:<scope>[^<]+</scope>\s*)?<version>([^<]+)</version>', pom_xml, re.DOTALL):
                artifact_id = match.group(1)
                version = match.group(2)
                
                if artifact_id and artifact_id not in seen:
                    req_obj = create_software_requirement(artifact_id, version)
                    requirements.append(req_obj)
                    seen.add(artifact_id)

        # Check build.gradle
        build_gradle = fetch_file_content(owner, repo, "build.gradle")
        if build_gradle:
            # Extract dependencies
            for match in re.finditer(r"['\"]([^'\"]+:[^'\"]+):([^'\"]+)['\"]", build_gradle):
                dep = match.group(1)
                version = match.group(2)
                
                if dep and dep not in seen:
                    req_obj = create_software_requirement(dep, version)
                    requirements.append(req_obj)
                    seen.add(dep)

        return sorted(requirements, key=lambda x: x.get('name', ''))

    except Exception:
        return []


def extract_ruby_requirements(owner: str, repo: str) -> List[Dict]:
    """
    Extract Ruby gem requirements with versions.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[Dict]: List of SoftwareApplication requirement objects.
    """
    try:
        requirements = []
        seen = set()

        # Check Gemfile
        gemfile = fetch_file_content(owner, repo, "Gemfile")
        if gemfile:
            # Extract gems with versions
            for match in re.finditer(r"gem\s+['\"]([^'\"]+)['\"](?:\s*,\s*['\"]([^'\"]+)['\"])?", gemfile):
                gem_name = match.group(1)
                version = match.group(2) if match.group(2) else None
                
                if gem_name and gem_name not in seen:
                    req_obj = create_software_requirement(gem_name, version)
                    requirements.append(req_obj)
                    seen.add(gem_name)

        return sorted(requirements, key=lambda x: x.get('name', ''))

    except Exception:
        return []


def extract_go_requirements(owner: str, repo: str) -> List[Dict]:
    """
    Extract Go module requirements with versions.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[Dict]: List of SoftwareApplication requirement objects.
    """
    try:
        requirements = []
        seen = set()

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
                            module = parts[0]
                            version = parts[1] if len(parts) > 1 else None
                            
                            if module not in seen:
                                req_obj = create_software_requirement(module, version)
                                requirements.append(req_obj)
                                seen.add(module)
            
            # Also check for single-line requires
            for match in re.finditer(r'require\s+([\w\./\-]+)\s+([\w\./\-]+)', go_mod):
                module = match.group(1)
                version = match.group(2)
                
                if module and '/' in module and module not in seen:
                    req_obj = create_software_requirement(module, version)
                    requirements.append(req_obj)
                    seen.add(module)

        return sorted(requirements, key=lambda x: x.get('name', ''))

    except Exception:
        return []


def extract_rust_requirements(owner: str, repo: str) -> List[Dict]:
    """
    Extract Rust crate requirements with versions.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[Dict]: List of SoftwareApplication requirement objects.
    """
    try:
        requirements = []
        seen = set()

        # Check Cargo.toml
        cargo_toml = fetch_file_content(owner, repo, "Cargo.toml")
        if cargo_toml:
            # Extract dependencies with versions
            for match in re.finditer(r'(\w+)\s*=\s*["\{]([^"}\n]+)', cargo_toml):
                crate_name = match.group(1)
                version_spec = match.group(2)
                
                if crate_name and crate_name not in ['package', 'dependencies', 'dev-dependencies', 'build-dependencies'] and crate_name not in seen:
                    req_obj = create_software_requirement(crate_name, version_spec)
                    requirements.append(req_obj)
                    seen.add(crate_name)

        return sorted(requirements, key=lambda x: x.get('name', ''))

    except Exception:
        return []


def extract_system_requirements(owner: str, repo: str) -> List[Dict]:
    """
    Extract system-level requirements from README and documentation.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[Dict]: List of SoftwareApplication requirement objects.
    """
    try:
        requirements = []
        seen = set()

        # Check README
        readme = fetch_file_content(owner, repo, "README.md")
        if readme:
            # Look for version patterns
            patterns = [
                r'(?:requires?|needs?)\s+([A-Za-z0-9\.\-_]+)\s+(?:version\s+)?(?:>=\s*)?(\d+\.[\d.]*)',
                r'(?:requires?|needs?)\s+([A-Za-z0-9\.\-_]+)\s+([0-9]+\.[0-9.]+)',
            ]
            for pattern in patterns:
                for match in re.finditer(pattern, readme, re.IGNORECASE):
                    req_name = match.group(1).strip()
                    version = match.group(2).strip() if len(match.groups()) > 1 else None
                    
                    if req_name and len(req_name) > 2 and req_name not in seen:
                        req_obj = create_software_requirement(req_name, version)
                        requirements.append(req_obj)
                        seen.add(req_name)

        return sorted(requirements, key=lambda x: x.get('name', ''))

    except Exception:
        return []


def get(repository_url: str) -> Dict:
    """
    Extract software requirements from a GitHub repository.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'softwareRequirements' key containing SoftwareApplication objects
              with minVersion and maxVersion according to CodeMeta 3.1 schema.
    """
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    # Extract requirements from multiple sources
    all_requirements = []
    seen_names = set()

    # Extract Python requirements
    python_reqs = extract_python_requirements(owner, repo)
    for req in python_reqs:
        name = req.get('name')
        if name and name not in seen_names:
            all_requirements.append(req)
            seen_names.add(name)

    # Extract Node.js requirements
    nodejs_reqs = extract_nodejs_requirements(owner, repo)
    for req in nodejs_reqs:
        name = req.get('name')
        if name and name not in seen_names:
            all_requirements.append(req)
            seen_names.add(name)

    # Extract Java requirements
    java_reqs = extract_java_requirements(owner, repo)
    for req in java_reqs:
        name = req.get('name')
        if name and name not in seen_names:
            all_requirements.append(req)
            seen_names.add(name)

    # Extract Ruby requirements
    ruby_reqs = extract_ruby_requirements(owner, repo)
    for req in ruby_reqs:
        name = req.get('name')
        if name and name not in seen_names:
            all_requirements.append(req)
            seen_names.add(name)

    # Extract Go requirements
    go_reqs = extract_go_requirements(owner, repo)
    for req in go_reqs:
        name = req.get('name')
        if name and name not in seen_names:
            all_requirements.append(req)
            seen_names.add(name)

    # Extract Rust requirements
    rust_reqs = extract_rust_requirements(owner, repo)
    for req in rust_reqs:
        name = req.get('name')
        if name and name not in seen_names:
            all_requirements.append(req)
            seen_names.add(name)

    # Extract system requirements
    system_reqs = extract_system_requirements(owner, repo)
    for req in system_reqs:
        name = req.get('name')
        if name and name not in seen_names:
            all_requirements.append(req)
            seen_names.add(name)

    if not all_requirements:
        return {}

    # Sort by name
    all_requirements.sort(key=lambda x: x.get('name', ''))

    return {
        "softwareRequirements": all_requirements
    }
