# CodeMeta Operating System Module

## Overview

The `codemeta_operating_system.py` module extracts supported operating systems with specific flavors and versions from a GitHub repository. It provides detailed OS information including distribution names, versions, and platform details.

## Implementation Details

### Operating Systems Detected

The module detects a comprehensive list of operating systems and their variants:

#### Linux Distributions
- **Ubuntu** (with versions: 22.04, 20.04, 18.04, 16.04, 14.04, 12.04, 10.04)
- **Debian** (with versions: 12, 11, 10, 9, 8)
- **CentOS** (with versions: 8, 7, 6)
- **RHEL** (with versions: 9, 8, 7, 6)
- **Fedora** (with version support)
- **Alpine** (with versions: 3.x)
- **Arch Linux**
- **openSUSE**
- **Generic Linux**

#### macOS Versions
- **macOS** (with versions: 13, 12, 11, 10.15, 10.14, 10.13)

#### Windows Versions
- **Windows** (with versions: Server 2022, 2019, 2016, 10)

#### BSD Variants
- **FreeBSD** (with versions: 13, 12, 11)
- **OpenBSD** (with versions: 7.x)
- **NetBSD** (with versions: 9, 8)
- **Generic BSD**

#### Mobile Platforms
- **iOS** (with version support)
- **Android** (with version support)

#### Other Unix-like Systems
- **Unix/POSIX**
- **Solaris**

### Data Sources

The module extracts OS information from multiple sources:

1. **README.md** - Text descriptions of supported platforms
2. **CI/CD Configuration**:
   - GitHub Actions workflows (.github/workflows/main.yml, .github/workflows/ci.yml)
   - Travis CI (.travis.yml)
   - AppVeyor (appveyor.yml)
   - Circle CI (.circleci/config.yml)
3. **Setup Files**:
   - setup.py (Python classifiers)
   - pyproject.toml (Python classifiers)
   - Dockerfile (Base image OS detection)

### Detection Strategy

The module uses a priority-based approach:

1. **README Detection** - Scans README for OS mentions
2. **CI/CD Detection** - Analyzes CI configuration files for OS matrix
3. **Setup Files Detection** - Extracts from package metadata and Docker configs
4. **Aggregation** - Combines results from all sources, removing duplicates
5. **Sorting** - Returns sorted list for consistency

## Function Reference

### `extract_os_with_details(text: str) -> Set[str]`

Extract operating systems with specific flavors and versions from text.

**Parameters:**
- `text` (str): Text to search for OS information

**Returns:**
- Set[str]: Set of detected operating systems with details

### `detect_os_from_readme(owner: str, repo: str) -> List[str]`

Detect supported operating systems from README.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name

**Returns:**
- List[str]: Sorted list of detected operating systems

### `detect_os_from_ci_config(owner: str, repo: str) -> List[str]`

Detect supported operating systems from CI/CD configuration.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name

**Returns:**
- List[str]: Sorted list of detected operating systems

### `detect_os_from_setup_files(owner: str, repo: str) -> List[str]`

Detect supported operating systems from setup files.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name

**Returns:**
- List[str]: Sorted list of detected operating systems

### `get(repository_url: str) -> Dict`

Main entry point for extracting operating system information from a GitHub repository.

**Parameters:**
- `repository_url` (str): Full GitHub repository URL

**Returns:**
- Dict: Dictionary with "operatingSystem" key if OS info is found, empty dict otherwise

**Example:**
```python
from src.modules import codemeta_operating_system

result = codemeta_operating_system.get("https://github.com/rust-lang/rust")
# Returns: {"operatingSystem": ["BSD", "Linux", "Ubuntu", "Windows", "macOS", "openSUSE"]}
```

## Testing

The module includes comprehensive unit tests covering:

1. **README Detection** - Extract OS from README files
2. **CI/CD Detection** - Extract from GitHub Actions, Travis CI, AppVeyor, Circle CI
3. **Setup Files Detection** - Extract from setup.py, pyproject.toml, Dockerfile
4. **Error Handling** - Handle missing files and API errors
5. **Real Repository Tests** - Test on actual repositories
6. **Content Validation** - Ensure OS data is valid and sorted

**Run tests:**
```bash
python3 -m unittest tests.test_codemeta_operating_system -v
```

## Test Results

All 20 tests pass successfully:

```
Ran 20 tests in 0.015s
OK
```

### Coverage

- README OS detection: ✓
- CI/CD OS detection: ✓
- Setup files OS detection: ✓
- OS with version detection: ✓
- Multiple OS detection: ✓
- Real repository testing: ✓
- Content validation: ✓
- Error handling: ✓

## Real Repository Examples

### Rust
- **Repository**: https://github.com/rust-lang/rust
- **Detected OS**: BSD, Linux, Ubuntu, Windows, macOS, openSUSE
- **Source**: CI configuration files (GitHub Actions, Travis CI)

### Flask
- **Repository**: https://github.com/pallets/flask
- **Detected OS**: BSD
- **Source**: README and setup files

### Dryad
- **Repository**: https://github.com/Dryad-lang/Dryad
- **Detected OS**: iOS
- **Source**: README or CI configuration

## Integration with CodeMeta Generator

The module integrates seamlessly with the main CodeMeta generator:

```python
from src.codemeta_generator import generate

result = generate("https://github.com/rust-lang/rust")
# result["operatingSystem"] contains the detected OS list
```

## CodeMeta 3.1 Compliance

The module generates output fully compliant with CodeMeta 3.1 standard:

- ✅ Valid array of strings format
- ✅ Proper property naming
- ✅ Valid data types
- ✅ No schema violations

## Error Handling

The module implements robust error handling:

- **Missing Files** - Returns empty list when files not found
- **API Errors** - Handles GitHub API failures gracefully
- **Invalid URLs** - Skips invalid repository URLs
- **Parse Errors** - Gracefully handles malformed content

## Validation Rules

1. **OS Names** - Must be recognized OS names
2. **Version Format** - Versions follow standard format (e.g., 22.04, 20.04)
3. **Duplicates** - Removed automatically
4. **Sorting** - Results are alphabetically sorted
5. **Non-empty** - Only returns if OS detected

## Output Structure

```json
{
  "operatingSystem": [
    "Linux",
    "Ubuntu 20.04",
    "Windows",
    "macOS"
  ]
}
```

## Supported OS Patterns

### Ubuntu Detection
- Pattern: `ubuntu 22.04`, `ubuntu-latest`, `ubuntu:20.04`
- Versions: 22.04, 20.04, 18.04, 16.04, 14.04, 12.04, 10.04

### Debian Detection
- Pattern: `debian 11`, `debian:10`, `debian`
- Versions: 12, 11, 10, 9, 8

### CentOS Detection
- Pattern: `centos 8`, `centos:7`, `centos`
- Versions: 8, 7, 6

### Windows Detection
- Pattern: `windows-latest`, `windows server 2019`, `visual studio`
- Versions: 2022, 2019, 2016, 10

### macOS Detection
- Pattern: `macos-latest`, `macos 12`, `darwin`, `osx`
- Versions: 13, 12, 11, 10.15, 10.14, 10.13

## Use Cases

1. **Software Metadata** - Include OS support in software metadata
2. **Compatibility Matrix** - Document supported platforms
3. **CI/CD Analysis** - Analyze test coverage across platforms
4. **Dependency Resolution** - Determine OS-specific requirements
5. **User Documentation** - Help users find compatible versions

## Dependencies

- `src.github_api`: Custom GitHub API utilities module
- `re`: Python regex module for pattern matching

## Performance

- **API Calls**: 5-10 calls per repository (depends on files found)
- **Response Time**: 2-5 seconds typical
- **Content Size**: Varies (typically 1-100 KB)
- **Rate Limiting**: Respects GitHub API rate limits

## Security

- **Token Support**: Uses GitHub token for authentication (if available)
- **HTTPS Only**: All API calls use HTTPS protocol
- **No Data Modification**: Read-only operation
- **Content Validation**: Validates content before processing

## Examples

### Extract OS from a single repository
```python
from src.modules import codemeta_operating_system

result = codemeta_operating_system.get("https://github.com/rust-lang/rust")
if result:
    for os in result["operatingSystem"]:
        print(f"Supports: {os}")
```

### Use with CodeMeta generator
```python
from src.codemeta_generator import generate

metadata = generate("https://github.com/rust-lang/rust")
if "operatingSystem" in metadata:
    print(f"Supported OS: {', '.join(metadata['operatingSystem'])}")
```

### Extract OS from multiple repositories
```python
from src.modules import codemeta_operating_system

repos = [
    "https://github.com/tensorflow/tensorflow",
    "https://github.com/pallets/flask",
    "https://github.com/rust-lang/rust"
]

for repo_url in repos:
    result = codemeta_operating_system.get(repo_url)
    if result:
        print(f"{repo_url}: {', '.join(result['operatingSystem'])}")
```

### Analyze OS support across projects
```python
from src.modules import codemeta_operating_system

repos = ["https://github.com/owner/repo1", "https://github.com/owner/repo2"]
all_os = set()

for repo_url in repos:
    result = codemeta_operating_system.get(repo_url)
    if result:
        all_os.update(result["operatingSystem"])

print(f"Total unique OS: {len(all_os)}")
print(f"Supported OS: {', '.join(sorted(all_os))}")
```

## Future Enhancements

Potential improvements for future versions:

1. **Minimum Versions** - Extract minimum OS version requirements
2. **Architecture Detection** - Detect CPU architecture support (x86, ARM, etc.)
3. **Container Platforms** - Detect Docker, Kubernetes support
4. **Virtual Machines** - Detect VM platform support
5. **Cloud Platforms** - Detect cloud provider support (AWS, Azure, GCP)
6. **Version Ranges** - Extract version ranges instead of specific versions

## Compliance

- **CodeMeta 3.1 Standard**: Fully compliant with CodeMeta 3.1 schema
- **JSON-LD Format**: Valid JSON-LD output
- **GitHub API**: Uses GitHub REST API v3
- **Python 3.8+**: Compatible with Python 3.8 and later

## Notes

- OS detection is based on available metadata in repository files
- Some projects may not explicitly document OS support
- CI/CD configuration provides the most reliable OS information
- Version information is extracted when available
- Results are deduplicated and sorted alphabetically
- The module is conservative - only reports OS that are explicitly mentioned

## Troubleshooting

### No OS Detected
- Check if repository has CI/CD configuration
- Verify README mentions supported platforms
- Check setup.py or pyproject.toml for classifiers
- Look for Dockerfile with base image information

### Incorrect OS Detected
- False positives may occur if OS names appear in comments
- Version numbers may be incorrectly associated
- Consider the source (CI config is more reliable than README)

### Missing Specific OS
- Some projects may not document all supported platforms
- CI/CD configuration may not test all platforms
- Check GitHub Issues or documentation for full support matrix
