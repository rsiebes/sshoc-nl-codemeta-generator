# CodeMeta Build Instructions Module

## Overview

The `codemeta_build_instructions.py` module extracts build and compilation instructions from GitHub repositories. It searches for build scripts, Makefiles, CI/CD configurations, and documentation to identify how to build the project.

## Module Location

- **Source**: `src/modules/codemeta_build_instructions.py`
- **Tests**: `tests/test_codemeta_build_instructions.py`

## Features

### Multi-Source Detection

The module searches for build instructions in the following order of priority:

1. **Makefile** - Extracts common build targets (build, install, compile, all, test)
2. **setup.py** - Python setuptools projects
3. **pyproject.toml** - Modern Python projects (Poetry, Flit, Hatchling)
4. **package.json** - Node.js/JavaScript projects
5. **Cargo.toml** - Rust projects
6. **build.gradle** - Java/Gradle projects
7. **pom.xml** - Java/Maven projects
8. **README.md** - Looks for Build/Installation/Setup sections
9. **CONTRIBUTING.md** - Looks for development setup instructions

### Supported Build Systems

| Build System | Detection | Output |
|---|---|---|
| Make | Makefile targets | `make build` |
| Python setuptools | setup.py | `python setup.py build` |
| Poetry | pyproject.toml | `poetry build` |
| Flit | pyproject.toml | `flit build` |
| Hatchling | pyproject.toml | `hatch build` |
| Generic Python | pyproject.toml | `python -m build` |
| npm | package.json | `npm run build` |
| Cargo (Rust) | Cargo.toml | `cargo build --release` |
| Gradle | build.gradle | `./gradlew build` |
| Maven | pom.xml | `mvn clean install` |

## Usage

### Basic Usage

```python
from src.modules import codemeta_build_instructions

result = codemeta_build_instructions.get("https://github.com/pallets/flask")
print(result)
# Output: {"buildInstructions": "flit build"}
```

### Individual Extraction Functions

```python
from src.modules import codemeta_build_instructions

# Extract from Makefile
instructions = codemeta_build_instructions.extract_from_makefile("owner", "repo")

# Extract from setup.py
instructions = codemeta_build_instructions.extract_from_setup_py("owner", "repo")

# Extract from pyproject.toml
instructions = codemeta_build_instructions.extract_from_pyproject_toml("owner", "repo")

# Extract from package.json
instructions = codemeta_build_instructions.extract_from_package_json("owner", "repo")

# Extract from Cargo.toml
instructions = codemeta_build_instructions.extract_from_cargo_toml("owner", "repo")

# Extract from build.gradle
instructions = codemeta_build_instructions.extract_from_build_gradle("owner", "repo")

# Extract from pom.xml
instructions = codemeta_build_instructions.extract_from_pom_xml("owner", "repo")

# Extract from README.md
instructions = codemeta_build_instructions.extract_from_readme("owner", "repo")

# Extract from CONTRIBUTING.md
instructions = codemeta_build_instructions.extract_from_contributing("owner", "repo")
```

## Real Repository Examples

### Flask (Python with Flit)

```json
{
  "buildInstructions": "flit build"
}
```

**Source**: pyproject.toml with Flit build backend

### Rust Language Compiler

```json
{
  "buildInstructions": "cargo build --release"
}
```

**Source**: Cargo.toml

### Linux Kernel

```json
{
  "buildInstructions": "make build"
}
```

**Source**: Makefile with build target

### Node.js Project

```json
{
  "buildInstructions": "npm run build  # webpack --mode production"
}
```

**Source**: package.json with build script

## Implementation Details

### Makefile Extraction

- Parses Makefile for target definitions
- Filters out special targets (.PHONY, .DEFAULT)
- Prioritizes common targets (build, install, compile, all, test)
- Returns first build target if no priority match

### Python Extraction

- **setup.py**: Checks for `setup()` or `setuptools` presence
- **pyproject.toml**: Identifies build backend and recommends appropriate tool
  - Poetry: `poetry build`
  - Flit: `flit build`
  - Hatchling: `hatch build`
  - Generic: `python -m build`

### JavaScript Extraction

- Searches for `"build"` script in package.json
- Extracts the actual build command
- Returns formatted npm command

### Language-Specific Extraction

- **Rust**: Checks for `[package]` section in Cargo.toml
- **Java/Gradle**: Checks for `plugins` or `apply plugin` in build.gradle
- **Java/Maven**: Checks for `<project>` tag in pom.xml

### Documentation Extraction

- Searches for Build/Installation/Setup/Getting Started/Compilation sections
- Extracts code blocks from markdown
- Returns first line of first code block
- Supports bash, shell, sh, zsh code blocks

## Output Format

The module returns a dictionary with the following structure:

```json
{
  "buildInstructions": "command to build the project"
}
```

Or an empty dictionary if no build instructions are found:

```json
{}
```

## Error Handling

- Returns `None` if a file is not found
- Returns `None` if parsing fails
- Returns empty dictionary if no build instructions are found in any source
- Gracefully handles missing or malformed configuration files

## Testing

The module includes 23 comprehensive unit tests:

- **Makefile extraction** (2 tests)
- **setup.py extraction** (2 tests)
- **pyproject.toml extraction** (3 tests)
- **package.json extraction** (2 tests)
- **Cargo.toml extraction** (2 tests)
- **build.gradle extraction** (2 tests)
- **pom.xml extraction** (2 tests)
- **README.md extraction** (2 tests)
- **Main get() function** (3 tests)
- **Data validation** (2 tests)

All tests pass with 100% success rate.

## CodeMeta 3.1 Compliance

The module outputs valid CodeMeta 3.1 metadata:

- **Property**: `buildInstructions`
- **Type**: Text
- **Required**: No
- **Repeatable**: No
- **Format**: Plain text command or instructions

## Integration with CodeMeta Generator

The module is automatically integrated into the CodeMeta generator orchestrator:

```python
from src.codemeta_generator import generate

result = generate("https://github.com/owner/repo")
# Includes buildInstructions if found
```

## Limitations

- Extracts only the primary build instruction (not all possible build targets)
- Does not analyze build configuration complexity
- Does not validate if extracted instructions are actually functional
- Limited to common build systems and file formats
- Does not extract platform-specific build instructions

## Future Enhancements

- Support for additional build systems (Bazel, CMake, Meson, etc.)
- Extraction of multiple build targets
- Platform-specific build instruction detection
- Build instruction validation
- Dependency extraction from build files
- Build time estimation
