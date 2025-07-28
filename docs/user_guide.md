# CodeMeta Generator User Guide

This guide provides comprehensive instructions for using the CodeMeta Generator toolkit to create, enhance, and manage CodeMeta files for research software projects.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Basic Usage](#basic-usage)
4. [Advanced Features](#advanced-features)
5. [SODA Science Use Case](#soda-science-use-case)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8 or higher
- Git (for cloning repositories)
- Internet connection (for GitHub API access)

### Install from Source

```bash
git clone https://github.com/your-username/codemeta-generator.git
cd codemeta-generator
pip install -r requirements.txt
```

### Install as Package

```bash
pip install -e .
```

## Quick Start

### Generate CodeMeta for a Single Repository

```python
from src.codemeta_generator import CodeMetaGenerator

# Initialize generator
generator = CodeMetaGenerator(schema_version="3.0")

# Generate CodeMeta
codemeta = generator.generate_from_github("https://github.com/owner/repo")

# Save to file
generator.save_codemeta(codemeta, "codemeta.json")
```

### Command Line Usage

```bash
# Generate CodeMeta file
python -m src.cli generate --repo https://github.com/owner/repo --output codemeta.json

# Enhance existing file
python -m src.cli enhance --input codemeta.json --schema 3.0

# Validate CodeMeta file
python -m src.cli validate codemeta.json
```

## Basic Usage

### 1. Generating CodeMeta Files

#### From GitHub Repository

```python
from src.codemeta_generator import CodeMetaGenerator

generator = CodeMetaGenerator()
codemeta = generator.generate_from_github("https://github.com/owner/repo")

# Add additional metadata
generator.add_authors(codemeta, [
    {
        "@type": "Person",
        "@id": "https://orcid.org/0000-0000-0000-0000",
        "givenName": "John",
        "familyName": "Doe"
    }
])

# Add software requirements
requirements = [
    {
        "@id": "https://github.com/numpy/numpy",
        "@type": "SoftwareApplication",
        "identifier": "numpy",
        "name": "numpy",
        "version": ">=1.20.0"
    }
]
generator.add_software_requirements(codemeta, requirements)

# Save the file
generator.save_codemeta(codemeta, "codemeta.json")
```

#### Adding Organizational Context

```python
from src.codemeta_generator import create_soda_science_organization

# Add SODA Science organizational context
soda_org = create_soda_science_organization()
generator.add_organizational_context(codemeta, soda_org)
```

### 2. Enhancing Existing CodeMeta Files

```python
from src.enhancer import CodeMetaEnhancer

enhancer = CodeMetaEnhancer(target_schema="3.0")

# Enhance a single file
enhanced = enhancer.enhance_file("codemeta.json")

# Validate enhancement
messages = enhancer.validate_enhancement(enhanced)
for message in messages:
    print(message)
```

### 3. Bulk Processing

```python
from src.bulk_processor import BulkProcessor

processor = BulkProcessor()

# Process multiple repositories
repo_urls = [
    "https://github.com/owner/repo1",
    "https://github.com/owner/repo2"
]
results = processor.process_repository_list(repo_urls, "./output/")

# Enhance multiple files
results = processor.enhance_directory("./codemeta_files/")
```

## Advanced Features

### Schema Version Management

The toolkit supports both CodeMeta 2.0 and 3.0 schemas:

```python
# Use CodeMeta 2.0
generator_v2 = CodeMetaGenerator(schema_version="2.0")

# Use CodeMeta 3.0 (recommended)
generator_v3 = CodeMetaGenerator(schema_version="3.0")

# Upgrade existing files
enhancer = CodeMetaEnhancer(target_schema="3.0")
enhanced = enhancer.enhance_file("old_codemeta.json")
```

### Adding Reference Publications

```python
from src.codemeta_generator import create_publication_reference

# Create publication reference
publication = create_publication_reference(
    doi="https://doi.org/10.21105/joss.07099",
    title="Software Title: A Research Tool",
    pub_type="ScholarlyArticle",
    publisher="Journal of Open Source Software",
    year="2024"
)

# Add to CodeMeta
generator.add_reference_publications(codemeta, publication)

# Multiple publications
publications = [publication1, publication2]
generator.add_reference_publications(codemeta, publications)
```

### Custom Software Requirements

```python
# Define software requirements with versions
requirements = [
    {
        "@id": "https://github.com/pandas-dev/pandas",
        "@type": "SoftwareApplication",
        "identifier": "pandas",
        "name": "pandas",
        "version": ">=1.3.0"
    },
    {
        "@id": "https://github.com/numpy/numpy",
        "@type": "SoftwareApplication",
        "identifier": "numpy",
        "name": "numpy",
        "version": ">=1.20.0"
    }
]

generator.add_software_requirements(codemeta, requirements)
```

### Validation and Quality Control

```python
# Validate CodeMeta file
warnings = generator.validate_codemeta(codemeta)
if warnings:
    print("Validation issues:")
    for warning in warnings:
        print(f"  - {warning}")

# Enhanced validation
enhancer = CodeMetaEnhancer()
messages = enhancer.validate_enhancement(codemeta)
```

## SODA Science Use Case

The SODA Science research group serves as a comprehensive example of using this toolkit for managing metadata across multiple research software projects.

### Processing SODA Science Repositories

```python
from src.bulk_processor import process_soda_science_repositories

# List of SODA Science repository URLs
soda_repos = [
    "https://github.com/sodascience/metasyn",
    "https://github.com/sodascience/osmenrich",
    "https://github.com/sodascience/artscraper"
    # ... more repositories
]

# Process all repositories with organizational context
results = process_soda_science_repositories(soda_repos, "./soda_codemeta/")
```

### Enhancing SODA Science Files

```python
from src.bulk_processor import enhance_soda_science_files

# Enhance existing SODA Science CodeMeta files
results = enhance_soda_science_files("./examples/soda_science/")
```

### Adding Publications to SODA Projects

```python
# Define publications for specific projects
publications_mapping = {
    "metasyn": [
        {
            "@type": "ScholarlyArticle",
            "@id": "https://doi.org/10.21105/joss.07099",
            "name": "Metasyn: A Python package for synthetic data generation"
        }
    ],
    "osmenrich": {
        "@type": "Dataset",
        "@id": "https://doi.org/10.5281/ZENODO.4548774",
        "name": "OSMenrich: Enriching OpenStreetMap data"
    }
}

# Apply publications to files
processor = BulkProcessor()
results = processor.add_reference_publications("./soda_files/", publications_mapping)
```

## Best Practices

### 1. Schema Version Selection

- **Use CodeMeta 3.0** for new projects (recommended)
- **Upgrade from 2.0** when possible for better features
- **Maintain consistency** across your organization

### 2. Metadata Completeness

- **Include ORCID IDs** for all authors
- **Add comprehensive descriptions** that explain the software's purpose
- **Specify software requirements** with version constraints
- **Include reference publications** when available

### 3. Organizational Context

- **Use consistent organizational information** across projects
- **Include institutional affiliations** for better discoverability
- **Add funding information** when applicable

### 4. Validation and Quality Control

- **Always validate** generated CodeMeta files
- **Review warnings** and address issues
- **Test with different tools** that consume CodeMeta

### 5. Maintenance

- **Update CodeMeta files** when software changes
- **Keep publication references** current
- **Review and enhance** periodically

## Command Line Interface

### Generate Command

```bash
# Basic generation
python -m src.cli generate --repo https://github.com/owner/repo --output codemeta.json

# With organizational context
python -m src.cli generate --repo https://github.com/owner/repo --output codemeta.json --organization soda
```

### Enhance Command

```bash
# Enhance existing file
python -m src.cli enhance --input codemeta.json

# Upgrade to CodeMeta 3.0
python -m src.cli enhance --input codemeta.json --schema 3.0 --output enhanced_codemeta.json
```

### Bulk Command

```bash
# Process repositories from file
python -m src.cli bulk --repos-file repos.txt --output ./output/ --organization soda

# Enhance directory of files
python -m src.cli bulk --directory ./codemeta_files/ --output ./enhanced/ --workers 8

# Generate processing report
python -m src.cli bulk --directory ./files/ --output ./enhanced/ --report report.json
```

### Validate Command

```bash
# Validate single file
python -m src.cli validate codemeta.json

# Validate directory
python -m src.cli validate ./codemeta_files/ --verbose

# Validate with specific schema
python -m src.cli validate ./files/ --schema 3.0
```

## Troubleshooting

### Common Issues

#### 1. GitHub API Rate Limiting

**Problem**: API requests fail due to rate limiting

**Solution**: 
- Add GitHub authentication token
- Reduce concurrent workers
- Add delays between requests

#### 2. Invalid Repository URLs

**Problem**: Repository URL format not recognized

**Solution**:
- Ensure URL format: `https://github.com/owner/repo`
- Check repository accessibility
- Verify repository exists

#### 3. Missing Dependencies

**Problem**: Import errors or missing packages

**Solution**:
```bash
pip install -r requirements.txt
pip install -e .
```

#### 4. Schema Validation Errors

**Problem**: Generated CodeMeta doesn't validate

**Solution**:
- Check required fields are present
- Verify schema version consistency
- Review field formats and types

#### 5. Encoding Issues

**Problem**: Unicode or encoding errors

**Solution**:
- Ensure UTF-8 encoding for all files
- Check special characters in metadata
- Use proper JSON encoding

### Getting Help

1. **Check the documentation** in the `docs/` directory
2. **Review examples** in `examples/soda_science/`
3. **Run validation** to identify specific issues
4. **Check the issue tracker** on GitHub
5. **Contact the maintainer** for complex problems

## Examples Directory

The `examples/` directory contains:

- **`soda_science/`**: 47 real-world CodeMeta files from SODA Science projects
- **`templates/`**: Template files for different project types
- **`individual_repos/`**: Examples for single repository processing

These examples demonstrate best practices and provide templates for your own projects.

---

*For more detailed API documentation, see [API Reference](api_reference.md)*

