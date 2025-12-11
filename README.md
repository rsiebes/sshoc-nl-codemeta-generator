# CodeMeta 3.1 Generator

A modular Python application for automatically generating rich and correct metadata in accordance with the CodeMeta 3.1 standard from GitHub repositories.

## Overview

The CodeMeta 3.1 Generator is built on a property-driven architecture where each CodeMeta property has its own dedicated Python module. This design ensures maximum modularity, maintainability, and compliance with the CodeMeta 3.1 specification.

## Project Structure

```
sshoc-nl-codemeta-generator/
├── src/
│   ├── __init__.py
│   ├── codemeta_generator.py      # Main orchestrator module
│   ├── schema_validator.py        # Schema validation utilities
│   ├── github_api.py              # GitHub API utilities
│   ├── utils.py                   # Common utility functions
│   └── modules/
│       ├── __init__.py
│       ├── codemeta_name.py       # Example property module
│       └── ... (other property modules)
├── tests/
│   ├── __init__.py
│   └── test_orchestrator.py       # Orchestrator tests
├── README.md                      # This file
└── ARCHITECTURE.md                # Architecture documentation
```

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/rsiebes/sshoc-nl-codemeta-generator.git
cd sshoc-nl-codemeta-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from src.codemeta_generator import generate

# Generate CodeMeta metadata
codemeta_data = generate(
    repository_url="https://github.com/rsiebes/sshoc-nl-codemeta-generator",
    output_file="codemeta.jsonld"
)
```

### Advanced Usage

```python
from src.codemeta_generator import CodeMetaGenerator

# Create a generator instance
generator = CodeMetaGenerator(verbose=True)

# Generate metadata
codemeta_data = generator.generate(
    repository_url="https://github.com/rsiebes/sshoc-nl-codemeta-generator",
    output_file="codemeta.jsonld"
)

# Access errors if any
errors = generator.get_errors()
if errors:
    print("Errors occurred during generation:")
    for error in errors:
        print(f"  - {error}")

# Access individual module results
module_results = generator.get_module_results()
for module_name, result in module_results.items():
    print(f"{module_name}: {result}")
```

### Command Line Usage

```bash
python3 src/codemeta_generator.py
```

This will generate metadata for the default repository and save it to `codemeta.jsonld`.

## Architecture

### Main Components

#### 1. CodeMetaGenerator (codemeta_generator.py)

The main orchestrator module that:
- Dynamically discovers all property modules
- Executes each module to extract metadata
- Aggregates results into a single CodeMeta structure
- Validates the generated metadata
- Writes the output to a JSON-LD file

#### 2. Property Modules (modules/codemeta_*.py)

Each property module is responsible for extracting and formatting metadata for a single CodeMeta property. All modules implement the same interface:

```python
def get(repository_url: str) -> dict:
    """
    Extract and format metadata for this property.
    
    Args:
        repository_url (str): The URL of the GitHub repository.
    
    Returns:
        dict: A dictionary containing the property name as key and the extracted value as value.
    """
    pass
```

#### 3. Schema Validator (schema_validator.py)

Provides utilities for validating CodeMeta metadata against the CodeMeta 3.1 schema:
- `validate_property()`: Validate individual properties
- `validate_metadata()`: Validate complete metadata
- `print_validation_report()`: Print a validation report

#### 4. GitHub API Utilities (github_api.py)

Provides utilities for interacting with the GitHub API:
- `parse_repository_url()`: Parse GitHub repository URLs
- `fetch_repository_info()`: Fetch repository metadata
- `fetch_repository_languages()`: Fetch programming languages
- `fetch_repository_contributors()`: Fetch contributors
- `fetch_repository_releases()`: Fetch releases
- `fetch_file_content()`: Fetch file content from the repository

#### 5. Common Utilities (utils.py)

Provides common utility functions:
- `camel_to_snake()`: Convert camelCase to snake_case
- `snake_to_camel()`: Convert snake_case to camelCase
- `is_url()`: Check if a string is a valid URL
- `is_email()`: Check if a string is a valid email
- `is_date()`: Check if a string is a valid ISO 8601 date
- `filter_empty_values()`: Remove empty values from dictionaries
- `merge_dicts()`: Merge multiple dictionaries
- `format_date()`: Format dates to ISO 8601 format
- And more...

## CodeMeta Properties

The generator supports all 71 properties defined in the CodeMeta 3.1 standard. Each property has a dedicated module:

| Property Name              | Module Name                            |
|----------------------------|----------------------------------------|
| address                    | codemeta_address.py                    |
| affiliation                | codemeta_affiliation.py                |
| applicationCategory        | codemeta_application_category.py       |
| ... (and 68 more)          | ...                                    |

See [ARCHITECTURE.md](ARCHITECTURE.md) for the complete list.

## Module Development

### Creating a New Property Module

To create a module for a new property, follow these steps:

1. Create a new file in `src/modules/` named `codemeta_{property_name}.py`
2. Implement the `get(repository_url)` function
3. Return a dictionary with the property name as key and the extracted value as value

### Example: Creating codemeta_description.py

```python
# src/modules/codemeta_description.py

from src.github_api import parse_repository_url, fetch_repository_info

def get(repository_url: str) -> dict:
    """Extracts the software description from the GitHub repository."""
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}
    
    repo_info = fetch_repository_info(owner, repo)
    if not repo_info:
        return {}
    
    description = repo_info.get("description")
    if description:
        return {"description": description}
    
    return {}
```

## Testing

Run the test suite to verify the orchestrator functionality:

```bash
python3 tests/test_orchestrator.py
```

The test suite includes:
- Module discovery tests
- Module execution tests
- CodeMeta structure building tests
- Validation tests
- Output writing tests
- Utility function tests
- Full generation tests

## Configuration

### GitHub API Token

To increase the GitHub API rate limit, set the `GITHUB_TOKEN` environment variable:

```bash
export GITHUB_TOKEN=your_github_token_here
python3 src/codemeta_generator.py
```

## Output Format

The generator produces a JSON-LD file in the CodeMeta 3.1 format:

```json
{
  "@context": "https://codemeta.github.io/terms/",
  "@type": "SoftwareSourceCode",
  "name": "software-name",
  "description": "Software description",
  "author": [
    {
      "@type": "Person",
      "name": "Author Name",
      "email": "author@example.com"
    }
  ],
  ...
}
```

## Error Handling

The generator handles errors gracefully:
- If a module fails to execute, the error is logged but the process continues
- If a module cannot extract a property, it returns an empty dictionary
- All errors are collected and can be accessed via `generator.get_errors()`

## Validation

The generated metadata is automatically validated against the CodeMeta 3.1 schema. The validation report includes:
- Overall validity status
- List of validation errors (if any)
- Count of valid and invalid properties

## Contributing

Contributions are welcome! To contribute:

1. Create a new property module following the guidelines above
2. Add tests for the new module
3. Update the documentation
4. Submit a pull request

## References

- [CodeMeta 3.1 Standard](https://codemeta.github.io/)
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [JSON-LD Specification](https://www.w3.org/TR/json-ld/)

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Authors

- Manus AI
- Original concept by rsiebes

## Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.
