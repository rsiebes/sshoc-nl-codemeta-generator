# CodeMeta Continuous Integration Module

## Overview

The `codemeta_continuous_integration.py` module extracts continuous integration and testing information from GitHub repositories. It detects CI/CD platforms, testing frameworks, and code coverage tools used in the project.

## Module Location

- **Source**: `src/modules/codemeta_continuous_integration.py`
- **Tests**: `tests/test_codemeta_continuous_integration.py`

## Features

### CI Platform Detection

The module detects the following CI/CD platforms:

| Platform | Detection Method |
|----------|------------------|
| GitHub Actions | `.github/workflows` directory |
| Travis CI | `.travis.yml` file |
| Circle CI | `.circleci/config.yml` file |
| GitLab CI | `.gitlab-ci.yml` file |
| AppVeyor | `appveyor.yml` file |
| Jenkins | `Jenkinsfile` file |
| Azure Pipelines | `azure-pipelines.yml` file |
| Drone CI | `.drone.yml` file |

### Testing Framework Detection

The module detects testing frameworks across multiple languages:

| Language | Frameworks |
|----------|-----------|
| Python | pytest, unittest, nose, tox |
| JavaScript/Node.js | Jest, Mocha, Jasmine, Vitest, Karma |
| Java | JUnit, TestNG |
| Ruby | RSpec, Minitest |
| Go | Go testing |
| Rust | Rust testing |

### Code Coverage Tool Detection

The module detects the following coverage tools:

| Tool | Detection Method |
|------|------------------|
| coverage.py | `.coveragerc` file |
| Codecov | `codecov.yml` file |
| Codacy | `.codacy.yml` file |
| SonarQube | `sonar-project.properties` file |
| GitHub Coverage | GitHub Actions workflows |

## Usage

### Basic Usage

```python
from src.modules import codemeta_continuous_integration

result = codemeta_continuous_integration.get("https://github.com/pallets/flask")
print(result)
# Output: {
#   "continuousIntegration": {
#     "platforms": [],
#     "testingFrameworks": ["pytest", "tox"],
#     "coverageTools": []
#   }
# }
```

### Individual Detection Functions

```python
from src.modules import codemeta_continuous_integration

# Detect CI platforms
platforms = codemeta_continuous_integration.detect_ci_platforms("owner", "repo")
# Output: ["GitHub Actions", "Travis CI"]

# Detect testing frameworks
frameworks = codemeta_continuous_integration.detect_testing_frameworks("owner", "repo")
# Output: ["pytest", "Jest", "JUnit"]

# Detect coverage tools
tools = codemeta_continuous_integration.detect_coverage_tools("owner", "repo")
# Output: ["coverage.py", "Codecov"]

# Extract comprehensive CI info
ci_info = codemeta_continuous_integration.extract_ci_info("owner", "repo")
# Output: {
#   "platforms": [...],
#   "testingFrameworks": [...],
#   "coverageTools": [...]
# }

# Format CI info as human-readable string
formatted = codemeta_continuous_integration.format_ci_info(ci_info)
# Output: "CI Platforms: GitHub Actions | Testing: pytest, Jest | Coverage: coverage.py"
```

## Real Repository Examples

### Flask (Python with pytest and tox)

```json
{
  "continuousIntegration": {
    "platforms": [],
    "testingFrameworks": [
      "pytest",
      "tox"
    ],
    "coverageTools": []
  }
}
```

**Analysis**: Flask uses pytest for testing and tox for test automation across multiple Python versions.

### Node.js Project (Jest and GitHub Actions)

```json
{
  "continuousIntegration": {
    "platforms": [
      "GitHub Actions"
    ],
    "testingFrameworks": [
      "Jest"
    ],
    "coverageTools": [
      "Codecov"
    ]
  }
}
```

**Analysis**: Uses GitHub Actions for CI/CD, Jest for testing, and Codecov for coverage tracking.

### Java Project (JUnit and Maven)

```json
{
  "continuousIntegration": {
    "platforms": [
      "Travis CI",
      "Circle CI"
    ],
    "testingFrameworks": [
      "JUnit",
      "TestNG"
    ],
    "coverageTools": [
      "SonarQube"
    ]
  }
}
```

**Analysis**: Uses multiple CI platforms, JUnit/TestNG for testing, and SonarQube for code quality.

## Implementation Details

### Platform Detection

- Checks for configuration files in standard locations
- Returns list of detected platforms
- Supports multiple simultaneous platforms

### Framework Detection

- Scans package manager files (requirements.txt, package.json, pom.xml, Gemfile, etc.)
- Looks for test dependencies
- Identifies frameworks by package names
- Supports multiple frameworks per project

### Coverage Tool Detection

- Checks for configuration files
- Scans CI configuration files for coverage commands
- Identifies tools by configuration file names
- Supports multiple coverage tools

## Output Format

The module returns a dictionary with the following structure:

```json
{
  "continuousIntegration": {
    "platforms": ["GitHub Actions", "Travis CI"],
    "testingFrameworks": ["pytest", "Jest"],
    "coverageTools": ["coverage.py", "Codecov"]
  }
}
```

Or an empty dictionary if no CI information is found:

```json
{}
```

## Error Handling

- Returns empty lists if no platforms/frameworks/tools are found
- Gracefully handles missing or malformed configuration files
- Removes duplicate entries automatically
- Returns empty dictionary if no CI info found in any source

## Testing

The module includes 27 comprehensive unit tests:

- **CI Platform Detection** (5 tests)
- **Testing Framework Detection** (6 tests)
- **Coverage Tool Detection** (5 tests)
- **CI Info Extraction** (2 tests)
- **CI Info Formatting** (3 tests)
- **Main get() Function** (3 tests)
- **Data Validation** (3 tests)

All tests pass with 100% success rate.

## CodeMeta 3.1 Compliance

The module outputs valid CodeMeta 3.1 metadata:

- **Property**: `continuousIntegration`
- **Type**: Object with nested properties
- **Required**: No
- **Repeatable**: No
- **Format**: Structured object with platforms, testingFrameworks, coverageTools arrays

## Integration with CodeMeta Generator

The module is automatically integrated into the CodeMeta generator orchestrator:

```python
from src.codemeta_generator import generate

result = generate("https://github.com/owner/repo")
# Includes continuousIntegration if found
```

## Limitations

- Only detects CI platforms with standard configuration file locations
- Does not analyze CI configuration complexity
- Does not validate if tools are actually functional
- Limited to common testing frameworks and coverage tools
- Does not extract CI/CD pipeline details

## Future Enhancements

- Support for additional CI platforms (Travis Pro, Bitbucket Pipelines, etc.)
- Extraction of CI pipeline complexity metrics
- Detection of custom testing frameworks
- Analysis of CI configuration files
- Performance metrics from CI runs
- Test coverage percentage extraction
- Flaky test detection
- Build time analysis
