# CodeMeta CLI - User Guide

## Overview

The CodeMeta Command-Line Interface (CLI) is a powerful tool for generating CodeMeta 3.1 metadata files from GitHub repositories. It provides an easy-to-use interface for extracting comprehensive software metadata and exporting it in standard JSON-LD format.

## Installation

The CLI is included in the CodeMeta Generator package. To use it, ensure you have Python 3.7+ installed and the required dependencies:

```bash
pip install requests
```

## Basic Usage

### Generate and Display CodeMeta

To generate CodeMeta for a GitHub repository and display it on the terminal:

```bash
python3 -m src.codemeta_cli https://github.com/tensorflow/tensorflow
```

### Save CodeMeta to a File

To save the generated CodeMeta to a file:

```bash
python3 -m src.codemeta_cli https://github.com/tensorflow/tensorflow -o codemeta.jsonld
```

### Pretty-Print the Output

To make the JSON output more readable with proper indentation:

```bash
python3 -m src.codemeta_cli https://github.com/tensorflow/tensorflow --pretty
```

### Enable Verbose Output

To see detailed progress information during generation:

```bash
python3 -m src.codemeta_cli https://github.com/tensorflow/tensorflow -v
```

## Advanced Options

### Using a GitHub Token

For higher API rate limits (5,000 requests/hour instead of 60), provide a GitHub personal access token:

```bash
python3 -m src.codemeta_cli https://github.com/tensorflow/tensorflow --token ghp_xxxxxxxxxxxxx
```

**How to create a GitHub token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token"
3. Select scopes: `public_repo` (minimum required)
4. Copy the token and use it with the `--token` option

### Validate Against Schema

To validate the generated CodeMeta against the CodeMeta 3.1 schema:

```bash
python3 -m src.codemeta_cli https://github.com/tensorflow/tensorflow --validate
```

### Combine Options

You can combine multiple options:

```bash
python3 -m src.codemeta_cli https://github.com/tensorflow/tensorflow \
  -o codemeta.jsonld \
  --pretty \
  --verbose \
  --token ghp_xxxxxxxxxxxxx \
  --validate
```

## Command-Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--help` | `-h` | Show help message and exit |
| `--version` | | Show version information |
| `--output FILE` | `-o FILE` | Save output to a file (default: stdout) |
| `--pretty` | `-p` | Pretty-print JSON with indentation |
| `--verbose` | `-v` | Enable verbose output with progress information |
| `--token TOKEN` | | GitHub personal access token for authentication |
| `--validate` | | Validate CodeMeta against the CodeMeta 3.1 schema |

## Examples

### Example 1: Generate CodeMeta for a Python Project

```bash
python3 -m src.codemeta_cli https://github.com/pallets/flask --pretty -o flask_codemeta.jsonld
```

### Example 2: Generate CodeMeta for a Rust Project with Validation

```bash
python3 -m src.codemeta_cli https://github.com/rust-lang/rust \
  --pretty \
  --validate \
  --token ghp_xxxxxxxxxxxxx
```

### Example 3: Generate CodeMeta with Verbose Output

```bash
python3 -m src.codemeta_cli https://github.com/vuejs/vue --verbose --pretty
```

### Example 4: Batch Process Multiple Repositories

```bash
#!/bin/bash

repositories=(
  "https://github.com/tensorflow/tensorflow"
  "https://github.com/rust-lang/rust"
  "https://github.com/kubernetes/kubernetes"
)

for repo in "${repositories[@]}"; do
  echo "Processing: $repo"
  python3 -m src.codemeta_cli "$repo" -o "codemeta_$(basename $repo).jsonld" --pretty
done
```

## Output Format

The CLI generates CodeMeta 3.1 compliant JSON-LD files with the following structure:

```json
{
  "@context": "https://codemeta.github.io/terms/",
  "@type": "SoftwareSourceCode",
  "name": "project-name",
  "description": "Project description",
  "license": {
    "@type": "CreativeWork",
    "name": "License Name",
    "@id": "https://spdx.org/licenses/LICENSE-ID"
  },
  "author": [
    {
      "name": "Author Name",
      "@type": "Person",
      "url": "https://github.com/username",
      "@id": "https://orcid.org/0000-0000-0000-0000"
    }
  ],
  "contributor": [...],
  "keywords": [...],
  "version": "1.0.0",
  "datePublished": "2025-01-01",
  "funder": [...]
}
```

## Supported Metadata Properties

The CLI extracts and includes the following CodeMeta properties:

1. **name** - Project name
2. **description** - Detailed project description
3. **license** - License information with SPDX identifier
4. **author** - Primary authors with ORCID enrichment
5. **contributor** - All contributors with ORCID enrichment
6. **keywords** - Relevant keywords and topics
7. **version** - Current software version
8. **datePublished** - Latest release or commit date
9. **funder** - Funding sources (when available)

## Error Handling

The CLI provides clear error messages for common issues:

### Invalid Repository URL

```
✗ Error: Invalid repository URL: Not a valid GitHub repository URL
```

**Solution:** Ensure you're using a valid GitHub repository URL (e.g., `https://github.com/owner/repo`)

### API Rate Limit Exceeded

```
⚠ Warning: GitHub API rate limit exceeded
```

**Solution:** Provide a GitHub token using the `--token` option

### Network Error

```
✗ Error: Failed to connect to GitHub API
```

**Solution:** Check your internet connection and try again

## Performance Tips

1. **Use a GitHub Token**: Increases API rate limit from 60 to 5,000 requests/hour
2. **Batch Processing**: Process multiple repositories in a single script
3. **Caching**: Results are cached within a single generation run
4. **Parallel Processing**: Use shell tools like `xargs` for parallel repository processing

## Troubleshooting

### Issue: "Module not found" error

```
ModuleNotFoundError: No module named 'src'
```

**Solution:** Run the CLI from the project root directory:
```bash
cd /path/to/sshoc-nl-codemeta-generator
python3 -m src.codemeta_cli https://github.com/owner/repo
```

### Issue: GitHub API errors

If you encounter GitHub API errors, ensure:
1. The repository URL is correct
2. The repository is public
3. Your GitHub token (if provided) is valid
4. You haven't exceeded the API rate limit

### Issue: Incomplete metadata

Some repositories may not have all metadata available. This is normal behavior:
- No funding information → `funder` field is omitted
- No releases → `version` field may be empty
- No ORCID identifiers → Authors listed without `@id`

## Integration with Other Tools

The generated CodeMeta files can be used with various tools and services:

### GitHub Pages

Add the CodeMeta file to your repository's documentation:
```bash
python3 -m src.codemeta_cli https://github.com/owner/repo -o docs/codemeta.jsonld
```

### Zenodo

Upload your CodeMeta file to Zenodo for research software registration

### Software Repositories

Use the CodeMeta file in software package managers and repositories

### Citation Tools

Generate citations from CodeMeta metadata using tools like CodeMeta-to-BibTeX converters

## Contributing

To contribute improvements to the CLI, please submit issues and pull requests to:
https://github.com/rsiebes/sshoc-nl-codemeta-generator

## License

This tool is released under the MIT License. See LICENSE file for details.

## Support

For questions, issues, or feature requests, please visit:
https://github.com/rsiebes/sshoc-nl-codemeta-generator/issues
