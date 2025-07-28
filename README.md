# CodeMeta Generator

A comprehensive toolkit for generating, enhancing, and managing CodeMeta files for research software projects. This repository provides tools to create standardized metadata for software repositories, with a focus on research software discoverability and citation.

## Overview

CodeMeta is a standardized metadata schema for software, designed to improve software discoverability, citation, and preservation. This toolkit provides automated generation and enhancement of CodeMeta files, with support for both CodeMeta 2.0 and 3.0 schemas.

## Features

- 🚀 **Automated CodeMeta Generation**: Generate comprehensive CodeMeta files from GitHub repositories
- 📊 **Schema Support**: Full support for CodeMeta 2.0 and 3.0 schemas
- 🔄 **Bulk Processing**: Process multiple repositories and CodeMeta files simultaneously
- 🏢 **Organizational Context**: Add organizational information and project relationships
- 📚 **Publication Integration**: Include reference publications with DOI links
- 🔍 **Intelligent Categorization**: Automatic application categorization based on project characteristics
- ✅ **Validation**: Ensure CodeMeta files comply with schema standards

## Use Cases

This toolkit has been successfully used to generate and enhance CodeMeta files for:

- **SODA Science Projects**: 47+ research software projects from Utrecht University
- **Individual Repositories**: Personal and academic software projects
- **Research Organizations**: Multi-project software portfolios
- **Academic Software**: Tools for computational research and data science

## Quick Start

### Installation

```bash
git clone https://github.com/your-username/codemeta-generator.git
cd codemeta-generator
pip install -r requirements.txt
```

### Basic Usage

```python
from src.codemeta_generator import CodeMetaGenerator

# Generate CodeMeta for a single repository
generator = CodeMetaGenerator()
codemeta = generator.generate_from_github("https://github.com/owner/repo")

# Enhance existing CodeMeta files
enhancer = CodeMetaEnhancer()
enhancer.enhance_file("codemeta.json")

# Bulk process multiple files
processor = BulkProcessor()
processor.process_directory("./codemeta_files/")
```

### Command Line Interface

```bash
# Generate CodeMeta for a repository
python -m src.cli generate --repo https://github.com/owner/repo --output codemeta.json

# Enhance existing CodeMeta files
python -m src.cli enhance --input codemeta.json --schema 3.0

# Bulk process files
python -m src.cli bulk --directory ./examples/soda_science/ --output ./enhanced/
```

## Examples

The `examples/` directory contains real-world examples from the SODA Science research group:

- **SODA Science Collection**: 47 comprehensive CodeMeta files for research software projects
- **Individual Projects**: Examples for different types of software (data analysis, web applications, educational materials)
- **Publication Integration**: Examples with reference publications and DOI links

### SODA Science Use Case

The SODA Science research group at Utrecht University serves as a primary use case, demonstrating:

- Organizational metadata integration
- Multi-project software portfolios
- Research software categorization
- Publication and citation management

## Repository Structure

```
codemeta-generator/
├── src/                          # Core source code
│   ├── codemeta_generator.py     # Main generation logic
│   ├── enhancer.py              # Enhancement and validation
│   ├── bulk_processor.py        # Batch processing tools
│   ├── schema_validator.py      # Schema validation
│   └── cli.py                   # Command line interface
├── examples/                     # Example CodeMeta files
│   ├── soda_science/            # SODA Science project examples
│   ├── individual_repos/        # Single repository examples
│   └── templates/               # CodeMeta templates
├── docs/                        # Documentation
│   ├── user_guide.md           # User guide and tutorials
│   ├── api_reference.md        # API documentation
│   └── schema_guide.md         # CodeMeta schema guide
├── tests/                       # Test suite
│   ├── test_generator.py       # Generation tests
│   ├── test_enhancer.py        # Enhancement tests
│   └── test_validation.py      # Validation tests
├── requirements.txt             # Python dependencies
├── setup.py                    # Package setup
├── LICENSE                     # License file
└── README.md                   # This file
```

## Documentation

- **[User Guide](docs/user_guide.md)**: Comprehensive guide for using the toolkit
- **[API Reference](docs/api_reference.md)**: Detailed API documentation
- **[Schema Guide](docs/schema_guide.md)**: CodeMeta schema reference and best practices

## CodeMeta Schema Support

### CodeMeta 3.0 (Recommended)
- Latest schema version with enhanced features
- Improved organizational and publication metadata
- Better support for research software contexts

### CodeMeta 2.0 (Legacy Support)
- Backward compatibility for existing files
- Migration tools to upgrade to 3.0

## Key Features in Detail

### Automated Generation
- Extract metadata from GitHub repositories
- Analyze repository structure and dependencies
- Generate comprehensive software requirements
- Include author information with ORCID integration

### Enhancement Capabilities
- Add missing metadata fields
- Update schema versions
- Include organizational context
- Integrate publication references

### Organizational Integration
- Support for research groups and institutions
- Multi-project portfolio management
- Hierarchical organizational structures
- Institutional affiliation tracking

### Publication Management
- DOI integration for reference publications
- Multiple publication types (articles, datasets, software)
- Publisher information and metadata
- Citation and impact tracking

## Contributing

We welcome contributions to improve the CodeMeta Generator toolkit:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this toolkit in your research, please cite:

```bibtex
@software{codemeta_generator,
  title = {CodeMeta Generator: A Toolkit for Research Software Metadata},
  author = {Siebes, Ronald},
  year = {2025},
  url = {https://github.com/your-username/codemeta-generator},
  note = {Software toolkit for generating and managing CodeMeta files}
}
```

## Maintainer

**Ronald Siebes**  
UCDS Group, VU Amsterdam  
ORCID: [0000-0001-8772-7904](https://orcid.org/0000-0001-8772-7904)  
Email: [r.siebes@vu.nl](mailto:r.siebes@vu.nl)

## Acknowledgments

- **SODA Science Research Group** (Utrecht University) for providing comprehensive use case examples
- **CodeMeta Community** for developing and maintaining the metadata schema
- **Research Software Engineering Community** for best practices and standards

## Related Projects

- [CodeMeta](https://codemeta.github.io/): The CodeMeta metadata schema
- [SODA Science](https://sodascience.github.io/): Scalable Open Data Analytics research group
- [Research Software Directory](https://research-software-directory.org/): Software discovery platform

---

*This toolkit supports the FAIR (Findable, Accessible, Interoperable, Reusable) principles for research software by providing standardized, machine-readable metadata.*

