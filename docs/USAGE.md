# Usage Guide

This guide provides detailed instructions on how to use the Codemeta 3.1 Generator.

## Installation

### System Requirements

- Python 3.11 or higher
- pip package manager
- Internet connection (for scraping GitHub repositories)

### Install Dependencies

```bash
cd sshoc-nl-codemeta-generator
pip install -r requirements.txt
```

Required packages:
- `requests` - For HTTP requests to GitHub
- `beautifulsoup4` - For HTML parsing
- `lxml` - For XML/HTML processing

## Basic Usage

### Generate Codemeta File

The simplest way to generate a Codemeta file:

```bash
python codemeta_gen.py https://github.com/owner/repo
```

This will:
1. Scrape the GitHub repository at the given URL
2. Extract all available metadata
3. Generate a `codemeta.json` file in the current directory

### Specify Output File

To save the output to a specific file:

```bash
python codemeta_gen.py https://github.com/owner/repo -o my_codemeta.json
```

or

```bash
python codemeta_gen.py https://github.com/owner/repo --output my_codemeta.json
```

### Verbose Output

For detailed information about the generation process:

```bash
python codemeta_gen.py https://github.com/owner/repo -v
```

This will show:
- Detailed scraping progress
- Validation errors and warnings
- Stack traces for any errors

## Command-Line Options

```
usage: codemeta_gen.py [-h] [-o OUTPUT] [-v] [--version] repo_url

positional arguments:
  repo_url              GitHub repository URL

optional arguments:
  -h, --help            Show help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file path (default: codemeta.json)
  -v, --verbose         Enable verbose output
  --version             Show version number and exit
```

## Examples

### Example 1: Simple Repository

```bash
python codemeta_gen.py https://github.com/requests/requests
```

Output:
```
======================================================================
Codemeta 3.1 Generator
======================================================================

Scraping repository: https://github.com/requests/requests
Extracted data for: requests

✅ Codemeta file generated: codemeta.json

======================================================================
✅ Generation completed successfully!
======================================================================
```

### Example 2: With Custom Output

```bash
python codemeta_gen.py https://github.com/pandas-dev/pandas -o pandas_codemeta.json
```

### Example 3: Verbose Mode

```bash
python codemeta_gen.py https://github.com/numpy/numpy -v
```

This will show detailed information including:
- Each metadata property being extracted
- Validation warnings for missing or incomplete data
- Any errors encountered during scraping

## Output Format

The generated Codemeta file is a JSON-LD file following the Codemeta 3.1 standard:

```json
{
  "@context": "https://w3id.org/codemeta/3.1",
  "@type": "SoftwareSourceCode",
  "name": "repository-name",
  "description": "Repository description",
  "url": "https://github.com/owner/repo",
  "version": "1.0.0",
  "codeRepository": "https://github.com/owner/repo",
  "license": {
    "@id": "https://spdx.org/licenses/MIT",
    "name": "MIT"
  },
  "keywords": ["keyword1", "keyword2"],
  "programmingLanguage": ["Python", "JavaScript"],
  "dateCreated": "2025-12-14T17:00:00.000000",
  "dateModified": "2025-12-14T17:00:00.000000"
}
```

## Currently Supported Properties

The generator currently extracts and validates the following properties:

### Core Properties
- **name** - Software name (from repository name)
- **description** - Software description (from repository description or README)
- **url** - Project website URL (from repository homepage or URL)
- **version** - Software version (from latest release/tag)
- **codeRepository** - Source code repository URL

### License
- **license** - Software license with automatic SPDX identifier mapping

### Additional Properties
- **keywords** - Repository topics/keywords
- **programmingLanguage** - Programming languages used in the repository
- **dateCreated** - Metadata creation date
- **dateModified** - Metadata modification date

## Validation

The generator includes built-in validation for all properties:

### Errors
Errors indicate critical issues that prevent proper metadata generation:
- Missing required fields
- Invalid data types
- Malformed URLs

### Warnings
Warnings indicate potential issues but don't prevent generation:
- Missing optional fields
- Incomplete data
- Data quality issues

Both errors and warnings are displayed after generation (use `-v` for details).

## Troubleshooting

### Common Issues

#### Issue: "Invalid GitHub repository URL"
**Solution**: Ensure the URL is a valid GitHub repository URL starting with `https://github.com/`

#### Issue: "Error fetching page"
**Solution**: 
- Check your internet connection
- Verify the repository exists and is public
- GitHub may be rate-limiting requests (wait a few minutes)

#### Issue: "No description found"
**Solution**: The repository may not have a description. The generator will try to extract from README.

### Getting Help

For additional help:
1. Use the `-v` flag for detailed error messages
2. Check the GitHub repository for issues and documentation
3. Review the generated file to see what data was extracted

## Advanced Usage

### Programmatic Usage

You can also use the generator programmatically in your Python code:

```python
from src.generator import CodemetaGenerator

# Create generator
generator = CodemetaGenerator()

# Generate metadata
codemeta = generator.generate("https://github.com/owner/repo")

# Save to file
generator.generate_to_file("https://github.com/owner/repo", "output.json")

# Get as JSON string
json_string = generator.generate_to_string("https://github.com/owner/repo")
```

### Batch Processing

To process multiple repositories:

```bash
#!/bin/bash
repos=(
  "https://github.com/owner/repo1"
  "https://github.com/owner/repo2"
  "https://github.com/owner/repo3"
)

for repo in "${repos[@]}"; do
  name=$(basename $repo)
  python codemeta_gen.py $repo -o "${name}_codemeta.json"
done
```

## Next Steps

- Review the generated Codemeta file
- Validate it against the Codemeta 3.1 schema
- Integrate it into your software documentation
- Submit it to software repositories and registries

## Resources

- [Codemeta Project](https://codemeta.github.io/)
- [Codemeta 3.1 Specification](https://w3id.org/codemeta/3.1)
- [SPDX License List](https://spdx.org/licenses/)
