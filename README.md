# Codemeta 3.1 Generator

A comprehensive Python-based metadata generator that creates Codemeta 3.1 compliant JSON-LD files from GitHub repositories through web scraping.

## Overview

This project implements a modular Python architecture where each metadata element is handled by a dedicated module. The generator scrapes GitHub repository information via web browsing (not the GitHub API) and produces rich, standards-compliant Codemeta 3.1 metadata files.

## Features

- **Modular Architecture**: Each metadata element has its own module for maintainability and extensibility
- **Web Scraping**: Extracts repository information directly from GitHub web pages
- **Codemeta 3.1 Compliant**: Generates metadata fully compliant with the Codemeta 3.1 JSON-LD standard
- **Comprehensive Metadata**: Captures all available metadata elements from the schema
- **Validation**: Built-in schema validation to ensure compliance

## Project Structure

```
src/
├── __init__.py
├── scraper.py              # GitHub web scraper
├── core_metadata.py        # Basic metadata (name, description, version)
├── dates.py               # Date-related metadata
├── people.py              # Authors, contributors, maintainers
├── technical.py           # Programming languages, OS, requirements
├── licensing.py           # License and copyright information
├── documentation.py       # README, help, release notes
├── development.py         # Development status, CI, build instructions
├── references.py          # Citations and related links
├── categories.py          # Application categories and keywords
├── validator.py           # Schema validation
├── output.py              # JSON-LD output generation
└── generator.py           # Main orchestrator

tests/
├── __init__.py
├── test_scraper.py
├── test_core_metadata.py
├── test_people.py
├── test_technical.py
└── test_integration.py

docs/
├── ARCHITECTURE.md        # System design and module interactions
├── MODULES.md            # Module documentation
└── USAGE.md              # Usage guide

examples/
└── sample_codemeta.json  # Example output
```

## Installation

```bash
git clone https://github.com/rsiebes/sshoc-nl-codemeta-generator.git
cd sshoc-nl-codemeta-generator
pip install -r requirements.txt
```

## Usage

```python
from src.generator import CodeMetaGenerator

# Create generator instance
generator = CodeMetaGenerator()

# Generate metadata from GitHub repository
codemeta = generator.generate("https://github.com/owner/repo")

# Save to file
codemeta.save("codemeta.json")
```

## Development

This project is developed iteratively, with each module being created, tested, and verified for both schema compliance and data accuracy.

## License

MIT License - See LICENSE file for details

## Author

Ronald Siebes (r.m.siebes@vu.nl)
ORCID: 0000-0001-8772-7904
