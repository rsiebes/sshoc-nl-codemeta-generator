# CodeMeta Input Method Module

## Overview

The `codemeta_input_method.py` module extracts input methods and user interfaces from a GitHub repository. It detects how users interact with the software (CLI, GUI, Web, API, Library).

## Features

### Input Method Detection

The module detects five types of input methods:

1. **Command-Line Interface (CLI)**
   - Detects CLI frameworks (click, typer, argparse, commander, yargs)
   - Checks for bin/ and scripts/ directories
   - Identifies entry points in configuration files

2. **Graphical User Interface (GUI)**
   - Detects GUI frameworks (PyQt, PySide, wxPython, Electron, GTK)
   - Identifies ui/ and gui/ directories
   - Checks for GUI dependencies

3. **Web Interface**
   - Detects web frameworks (Flask, Django, FastAPI, Express, React, Vue)
   - Identifies web/ and frontend/ directories
   - Checks for web dependencies

4. **Application Programming Interface (API)**
   - Detects REST/GraphQL APIs (fastapi, flask, express)
   - Identifies OpenAPI/Swagger specifications
   - Checks for API documentation

5. **Programmatic Interface (Library/SDK)**
   - Detects libraries and SDKs for programmatic use
   - Identifies packages without CLI entry points
   - Checks for import/require statements in documentation

## Detection Strategies

### 1. CLI Detection

```python
# From setup.py
install_requires=['click>=7.0']

# From pyproject.toml
dependencies = ['typer>=0.3.0']

# From package.json
"dependencies": {"commander": "^9.0.0"}
```

### 2. GUI Detection

```python
# From setup.py
install_requires=['PyQt5>=5.15']

# From pyproject.toml
dependencies = ['pyside2>=5.15']

# From package.json
"dependencies": {"electron": "^13.0.0"}
```

### 3. Web Interface Detection

```python
# From setup.py
install_requires=['flask>=1.0']

# From pyproject.toml
dependencies = ['django>=3.0']

# From package.json
"dependencies": {"react": "^17.0.0"}
```

### 4. API Detection

```markdown
# MyApp

This library provides a REST API for data access.
```

```yaml
# openapi.yaml
openapi: 3.0.0
```

### 5. Library Detection

```markdown
# MyLib

A Python library for data processing.
Import it with: from mylib import process
```

## Output Format

The module returns a list of detected input methods:

```json
{
  "inputMethod": [
    "Command-line interface",
    "Web interface",
    "Application programming interface"
  ]
}
```

## Real Repository Examples

### Flask

```json
{
  "inputMethod": [
    "Command-line interface",
    "Web interface",
    "Application programming interface",
    "Programmatic interface"
  ]
}
```

### PyQt

```json
{
  "inputMethod": [
    "Graphical user interface",
    "Programmatic interface"
  ]
}
```

### Requests

```json
{
  "inputMethod": [
    "Programmatic interface"
  ]
}
```

### Jupyter

```json
{
  "inputMethod": [
    "Web interface",
    "Command-line interface",
    "Graphical user interface"
  ]
}
```

## API Reference

### `detect_cli_interface(owner, repo)`

Detects if the software has a command-line interface.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name

**Returns:**
- bool: True if CLI interface detected

**Example:**
```python
has_cli = detect_cli_interface("pallets", "flask")
# Returns: True
```

### `detect_gui_interface(owner, repo)`

Detects if the software has a graphical user interface.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name

**Returns:**
- bool: True if GUI interface detected

**Example:**
```python
has_gui = detect_gui_interface("rivertools", "pyqt5-app")
# Returns: True
```

### `detect_web_interface(owner, repo)`

Detects if the software has a web interface.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name

**Returns:**
- bool: True if web interface detected

**Example:**
```python
has_web = detect_web_interface("pallets", "flask")
# Returns: True
```

### `detect_api_interface(owner, repo)`

Detects if the software provides an API interface.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name

**Returns:**
- bool: True if API interface detected

**Example:**
```python
has_api = detect_api_interface("pallets", "flask")
# Returns: True
```

### `detect_library_interface(owner, repo)`

Detects if the software is a library/SDK for programmatic use.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name

**Returns:**
- bool: True if library interface detected

**Example:**
```python
is_library = detect_library_interface("psf", "requests")
# Returns: True
```

### `get_input_methods(owner, repo)`

Detects all input methods from a repository.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name

**Returns:**
- List[str]: List of detected input methods

**Example:**
```python
methods = get_input_methods("pallets", "flask")
# Returns: ["Command-line interface", "Web interface", "Application programming interface", "Programmatic interface"]
```

### `get(repository_url)`

Main function to extract input method information from a repository.

**Parameters:**
- `repository_url` (str): GitHub repository URL

**Returns:**
- Dict: Dictionary with 'inputMethod' key if methods found, empty dict otherwise

**Example:**
```python
result = get("https://github.com/pallets/flask")
# Returns: {"inputMethod": ["Command-line interface", "Web interface", ...]}
```

## Integration with CodeMeta Generator

The module is automatically integrated with the CodeMeta generator orchestrator:

```python
from src.codemeta_generator import generate

result = generate("https://github.com/pallets/flask")
print(result["inputMethod"])  # ["Command-line interface", "Web interface", ...]
```

## Error Handling

The module gracefully handles errors:

- Missing files return False for detection functions
- Invalid URLs return empty dictionaries
- Parsing errors are silently ignored
- Duplicate methods are automatically removed

## Testing

The module includes 27 comprehensive unit tests:

- CLI detection (4 tests)
- GUI detection (4 tests)
- Web interface detection (4 tests)
- API detection (4 tests)
- Library detection (3 tests)
- Main function (3 tests)
- Data validation (2 tests)

Run tests with:
```bash
python3 -m unittest tests.test_codemeta_input_method -v
```

## Limitations

1. Keyword-based detection may miss some interfaces
2. Doesn't analyze actual code for interface types
3. Limited to predefined framework lists
4. Doesn't detect custom or proprietary interfaces
5. May have false positives for dependencies

## Future Enhancements

- Machine learning-based interface detection
- Analysis of actual code for interface patterns
- Support for more framework types
- Detection of interface versions
- Detection of interface capabilities
- Support for custom interface definitions
