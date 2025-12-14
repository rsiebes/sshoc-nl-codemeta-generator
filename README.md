# Codemeta 3.1 Generator

A Python-based tool that generates comprehensive Codemeta 3.1 metadata from GitHub repositories by scraping repository information via web browsing (no API required).

## Features

- **Web-based scraping**: Extracts metadata directly from GitHub pages without requiring API tokens
- **Modular architecture**: Each Codemeta property has its own dedicated module
- **Codemeta 3.1 compliant**: Generates valid JSON-LD metadata following the Codemeta 3.1 standard
- **Comprehensive validation**: Built-in validation for all metadata properties
- **SPDX license mapping**: Automatic mapping of license names to SPDX identifiers
- **Command-line interface**: Easy-to-use CLI for generating metadata files

## Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Generate a Codemeta file for any GitHub repository:

```bash
python codemeta_gen.py https://github.com/owner/repo
```

This will create a `codemeta.json` file in the current directory.

### Specify Output File

```bash
python codemeta_gen.py https://github.com/owner/repo -o my_codemeta.json
```

### Command-line Options

```
usage: codemeta_gen.py [-h] [-o OUTPUT] [-v] [--version] repo_url

Generate Codemeta 3.1 metadata from GitHub repositories

positional arguments:
  repo_url              GitHub repository URL (e.g., https://github.com/owner/repo)

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file path (default: codemeta.json)
  -v, --verbose         Enable verbose output
  --version             show program's version number and exit
```

## Example

```bash
$ python codemeta_gen.py https://github.com/torvalds/linux

======================================================================
Codemeta 3.1 Generator
======================================================================

Scraping repository: https://github.com/torvalds/linux
Extracted data for: linux

✅ Codemeta file generated: codemeta.json

======================================================================
✅ Generation completed successfully!
======================================================================
```

## Currently Implemented Properties

The following Codemeta 3.1 properties are currently implemented:

- ✅ **name** - Software name
- ✅ **description** - Software description
- ✅ **url** - Project website URL
- ✅ **version** - Software version
- ✅ **codeRepository** - Source code repository URL
- ✅ **license** - Software license with SPDX mapping
- ✅ **keywords** - Repository topics/keywords
- ✅ **programmingLanguage** - Programming languages used
- ✅ **dateCreated** - Creation date
- ✅ **dateModified** - Last modification date

## Project Structure

```
sshoc-nl-codemeta-generator/
├── codemeta_gen.py          # CLI entry point
├── src/
│   ├── scraper.py           # GitHub web scraper
│   ├── generator.py         # Main metadata generator
│   ├── base_metadata.py     # Base class for property modules
│   ├── utils.py             # Utility functions (SPDX mapping)
│   └── properties/          # Property modules
│       ├── name.py
│       ├── description.py
│       ├── url.py
│       ├── version.py
│       ├── code_repository.py
│       └── license.py
├── tests/                   # Test suite (52 tests)
├── docs/                    # Documentation
└── examples/                # Example outputs
```

## Development Status

This project is under active development. Currently, 6 core property modules are implemented with full validation and testing (52 tests passing).

Additional property modules will be added incrementally to support the complete Codemeta 3.1 specification (48 remaining properties).

## Testing

Run the test suite:

```bash
python -m unittest discover tests
```

Current test coverage:
- 23 core property tests
- 29 license property tests
- All tests passing ✅

## Codemeta 3.1 Standard

This tool generates metadata compliant with the [Codemeta 3.1 standard](https://codemeta.github.io/).

The generated JSON-LD files include:
- `@context`: `https://w3id.org/codemeta/3.1`
- `@type`: `SoftwareSourceCode`
- All extracted metadata properties

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Acknowledgments

- [Codemeta Project](https://codemeta.github.io/)
- [SPDX License List](https://spdx.org/licenses/)

## Author

Ronald Siebes (r.m.siebes@vu.nl)
ORCID: 0000-0001-8772-7904

## Contact

For questions or support, please open an issue on GitHub.
