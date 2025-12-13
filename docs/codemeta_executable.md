# CodeMeta Executable Module

## Overview

The `codemeta_executable.py` module extracts executable files and entry points from a GitHub repository. It identifies command-line tools, scripts, and executable entry points defined in package configuration files.

## Features

### Executable Detection

The module detects executables from multiple sources:

1. **CLI Entry Points** (setup.py, pyproject.toml, package.json, Cargo.toml)
   - Python setuptools entry_points
   - Poetry scripts
   - Node.js bin field
   - Rust binary targets

2. **Shell Scripts**
   - bin/ directory
   - scripts/ directory
   - tools/ directory
   - cmd/ directory

3. **Makefile Targets**
   - Executable targets (excluding common non-executable ones)
   - Custom build commands

4. **Python Executable Scripts**
   - cli.py, main.py, run.py, start.py, server.py
   - Scripts with shebang or __main__

## Detection Strategies

### 1. Python setuptools (setup.py)

```python
entry_points={
    'console_scripts': [
        'myapp=myapp.cli:main',
        'myapp-admin=myapp.admin:main',
    ],
}
```

Detects: `myapp`, `myapp-admin`

### 2. Poetry (pyproject.toml)

```toml
[tool.poetry.scripts]
myapp = "myapp.cli:main"
myapp-admin = "myapp.admin:main"
```

Detects: `myapp`, `myapp-admin`

### 3. Python setuptools (pyproject.toml)

```toml
[project.scripts]
mycli = "mypackage.cli:main"
myapp = "mypackage.app:run"
```

Detects: `mycli`, `myapp`

### 4. Node.js (package.json)

```json
{
  "bin": {
    "myapp": "./bin/cli.js",
    "myapp-admin": "./bin/admin.js"
  }
}
```

Detects: `myapp`, `myapp-admin`

### 5. Rust (Cargo.toml)

```toml
[[bin]]
name = "myapp"
path = "src/main.rs"

[[bin]]
name = "myapp-cli"
path = "src/cli.rs"
```

Detects: `myapp`, `myapp-cli`

### 6. Makefile

```makefile
run:
	python main.py

deploy:
	./deploy.sh
```

Detects: `run`, `deploy` (excludes common non-executable targets like all, clean, test, build, install, help)

## Output Format

The module returns a list of executable names:

```json
{
  "executable": [
    "flask",
    "myapp",
    "myapp-admin",
    "cli"
  ]
}
```

## Real Repository Examples

### Flask

```json
{
  "executable": ["flask"]
}
```

Source: Detected from `pyproject.toml` entry points

### Requests

```json
{
  "executable": []
}
```

Note: Requests is a library without CLI entry points

## API Reference

### `detect_cli_entry_points(owner, repo)`

Detects CLI entry points from package configuration files.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name

**Returns:**
- List[str]: List of detected CLI entry points

**Example:**
```python
entry_points = detect_cli_entry_points("pallets", "flask")
# Returns: ["flask"]
```

### `detect_shell_scripts(owner, repo)`

Detects shell scripts in common directories.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name

**Returns:**
- List[str]: List of detected shell script directories

**Example:**
```python
scripts = detect_shell_scripts("owner", "repo")
# Returns: ["bin/*", "scripts/*"]
```

### `detect_executable_files(owner, repo)`

Detects all executable files and entry points.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name

**Returns:**
- List[str]: List of all detected executables

**Example:**
```python
executables = detect_executable_files("pallets", "flask")
# Returns: ["flask"]
```

### `get(repository_url)`

Main function to extract executable information from a repository.

**Parameters:**
- `repository_url` (str): GitHub repository URL

**Returns:**
- Dict: Dictionary with 'executable' key if executables found, empty dict otherwise

**Example:**
```python
result = get("https://github.com/pallets/flask")
# Returns: {"executable": ["flask"]}
```

## Integration with CodeMeta Generator

The module is automatically integrated with the CodeMeta generator orchestrator:

```python
from src.codemeta_generator import generate

result = generate("https://github.com/pallets/flask")
print(result["executable"])  # ["flask"]
```

## Error Handling

The module gracefully handles errors:

- Missing files return empty lists
- Invalid URLs return empty dictionaries
- Parsing errors are silently ignored
- Duplicate executables are automatically removed

## Testing

The module includes 22 comprehensive unit tests:

- CLI entry point detection (6 tests)
- Shell script detection (4 tests)
- Executable file detection (5 tests)
- Info formatting (3 tests)
- Main function (3 tests)
- Data validation (1 test)

Run tests with:
```bash
python3 -m unittest tests.test_codemeta_executable -v
```

## Limitations

1. Directory listing is simulated (returns `dir/*` pattern)
2. Makefile parsing is basic (regex-based)
3. Doesn't detect executables in compiled binaries
4. Doesn't detect executables in Docker containers
5. Doesn't analyze GitHub Actions workflows for executable definitions

## Future Enhancements

- Support for more build systems (Gradle, Maven, etc.)
- Detection of executable permissions in git
- Analysis of GitHub Actions workflows
- Support for container-based executables
- Executable version detection
- Executable dependency tracking
