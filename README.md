# Codemeta Generator

A Python command-line tool that generates Codemeta 3.1 compliant metadata from GitHub repository URLs.

## Overview

This tool takes a GitHub repository URL as input and generates a comprehensive `codemeta.jsonld` file that conforms to the [Codemeta 3.1 standard](https://raw.githubusercontent.com/codemeta/codemeta/3.1/codemeta.jsonld).

## Features

- **Modular Architecture**: Each Codemeta schema element is handled by a dedicated submodule
- **Robust Error Handling**: Graceful error handling with informative error messages
- **Detailed Logging**: Comprehensive logging for debugging and transparency
- **Public Repository Support**: Works with public GitHub repositories without authentication

## Installation

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

Generate Codemeta for a GitHub repository:

```bash
python -m src.main https://github.com/owner/repo
```

This will create a `codemeta.jsonld` file in the current directory.

### Custom Output Path

Specify a custom output path:

```bash
python -m src.main https://github.com/owner/repo --output /path/to/codemeta.jsonld
```

### Verbose Logging

Enable verbose logging for debugging:

```bash
python -m src.main https://github.com/owner/repo -v
```

## Project Structure

```
src/
├── __init__.py
├── main.py                 # CLI entry point
├── codemeta_generator.py   # Main orchestrator
├── core/
│   ├── __init__.py
│   ├── config.py          # CLI argument parsing
│   ├── errors.py          # Custom exception classes
│   ├── github_api.py      # GitHub API interactions
│   └── logger.py          # Logging configuration
└── submodules/            # Codemeta schema element modules
    └── __init__.py
```

## Development

### Adding New Codemeta Properties

Each Codemeta schema element should be implemented as a separate submodule under `src/submodules/`. 

For example, to add support for the `author` property, create `src/submodules/author.py` with a class that handles author metadata extraction and generation.

## License

[Your License Here]

## Contributing

Contributions are welcome. Please follow the existing code style and structure.
