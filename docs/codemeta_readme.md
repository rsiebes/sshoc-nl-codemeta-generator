# CodeMeta README Module

## Overview

The `codemeta_readme.py` module extracts the README content from a GitHub repository. It provides the raw README file content from the repository's root directory.

## Implementation Details

### README Information Extracted

The module extracts:
- **readme**: The raw content of the README file

### Data Source

The README content is extracted from the GitHub API v3 repository file endpoint:
- Attempts multiple README file formats
- Returns the first found README file

### Supported README Formats

The module tries to find README files in the following order:

1. **README.md** - Markdown format (most common)
2. **README.rst** - reStructuredText format
3. **README.txt** - Plain text format
4. **README** - No extension format

## Function Reference

### `get_readme_content(owner: str, repo: str) -> Optional[str]`

Get README content from GitHub repository.

**Parameters:**
- `owner` (str): Repository owner username
- `repo` (str): Repository name

**Returns:**
- str: README content if found
- None: If README not found

### `get_readme_url(owner: str, repo: str) -> Optional[str]`

Get README URL from GitHub repository.

**Parameters:**
- `owner` (str): Repository owner username
- `repo` (str): Repository name

**Returns:**
- str: README raw content URL
- None: If URL cannot be constructed

### `get(repository_url: str) -> Dict`

Main entry point for extracting README content from a GitHub repository.

**Parameters:**
- `repository_url` (str): Full GitHub repository URL (e.g., "https://github.com/owner/repo")

**Returns:**
- Dict: Dictionary with "readme" key if README is found, empty dict otherwise

**Example:**
```python
from src.modules import codemeta_readme

result = codemeta_readme.get("https://github.com/pallets/flask")
# Returns: {"readme": "# Flask\n\nThe Python micro framework..."}
```

## Testing

The module includes comprehensive unit tests covering:

1. **Basic Extraction**: Verify correct extraction of README content
2. **Format Priority**: Test README format priority (MD > RST > TXT > no extension)
3. **Fallback Tests**: Test fallback to alternative README formats
4. **Error Handling Tests**: Test handling of missing or invalid data
5. **Real Repository Tests**: Test on actual repositories
6. **Content Validation Tests**: Ensure README data is valid
7. **Size Tests**: Test small and large README files

**Run tests:**
```bash
python3 -m unittest tests.test_codemeta_readme -v
```

## Test Results

All 22 tests pass successfully:

```
Ran 22 tests in 0.009s
OK
```

### Coverage

- Basic README extraction: ✓
- README.md priority: ✓
- README format fallback: ✓
- Missing README handling: ✓
- API error handling: ✓
- Real repository testing: ✓
- Content validation: ✓
- Markdown formatting: ✓
- Special characters: ✓
- Large content handling: ✓

## Real Repository Examples

### Flask
- **Repository**: https://github.com/pallets/flask
- **README Found**: Yes (HTML/Markdown)
- **Content**: Flask framework documentation

### Dryad
- **Repository**: https://github.com/Dryad-lang/Dryad
- **README Found**: Yes (Markdown)
- **Content**: Dryad programming language documentation

### TensorFlow
- **Repository**: https://github.com/tensorflow/tensorflow
- **README Found**: Varies by branch
- **Content**: TensorFlow documentation

## Integration with CodeMeta Generator

The module integrates seamlessly with the main CodeMeta generator:

```python
from src.codemeta_generator import generate

result = generate("https://github.com/pallets/flask")
# result["readme"] contains the Flask README content
```

## CodeMeta 3.1 Compliance

The module generates output fully compliant with CodeMeta 3.1 standard:

- ✅ Valid content format
- ✅ Proper property naming
- ✅ Valid data type (string)
- ✅ No schema violations

## Error Handling

The module implements robust error handling:

- **Missing README**: Returns empty dict when README not found
- **API Errors**: Handles GitHub API failures gracefully
- **Invalid URLs**: Skips invalid repository URLs
- **Format Errors**: Tries multiple README formats

## Validation Rules

1. **Content Required**: README content must not be empty
2. **String Type**: README must be a string value
3. **Format Priority**: Tries multiple README formats in order
4. **Encoding**: Handles UTF-8 and special characters

## Output Structure

```json
{
  "readme": "# Project Title\n\nProject description..."
}
```

## README Format Priority

The module uses a priority-based strategy:

1. **README.md** (Highest Priority)
   - Most common format
   - Markdown syntax
   - Best for GitHub rendering

2. **README.rst** (Fallback)
   - reStructuredText format
   - Common in Python projects
   - Sphinx documentation compatible

3. **README.txt** (Fallback)
   - Plain text format
   - Simple format
   - Universal compatibility

4. **README** (Lowest Priority)
   - No extension
   - Fallback option
   - Legacy format

## Dependencies

- `src.github_api`: Custom GitHub API utilities module

## Notes

- GitHub API returns raw file content
- README is typically in the repository root directory
- Multiple README formats are supported
- Content is returned as-is without modification
- Large README files are handled correctly
- Special characters and Unicode are supported

## README Content Types

README files can contain:

- **Markdown**: Formatted text, code blocks, links
- **HTML**: Direct HTML markup
- **Plain Text**: Simple text content
- **reStructuredText**: Sphinx-compatible format
- **Mixed Content**: Combination of formats

## Use Cases

1. **Software Metadata**: Include README in software metadata
2. **Project Discovery**: Find project information
3. **Documentation**: Extract project documentation
4. **Content Analysis**: Analyze project descriptions
5. **Metadata Enrichment**: Enrich metadata with README content

## Future Enhancements

Potential improvements for future versions:

1. **Content Parsing**: Parse README structure
2. **Markdown Conversion**: Convert to other formats
3. **Content Summary**: Generate summary from README
4. **Link Extraction**: Extract links from README
5. **Section Detection**: Detect README sections

## Compliance

- **CodeMeta 3.1 Standard**: Fully compliant with CodeMeta 3.1 schema
- **JSON-LD Format**: Valid JSON-LD output
- **GitHub API**: Uses GitHub REST API v3
- **Python 3.8+**: Compatible with Python 3.8 and later

## Performance

- **API Calls**: 1-4 calls per repository (depends on README format found)
- **Response Time**: < 1 second typical
- **Content Size**: Varies (typically 1-50 KB)
- **Rate Limiting**: Respects GitHub API rate limits

## Security

- **Token Support**: Uses GitHub token for authentication (if available)
- **HTTPS Only**: All API calls use HTTPS protocol
- **No Data Modification**: Read-only operation
- **Content Validation**: Validates content before returning

## Examples

### Extract README from a single repository
```python
from src.modules import codemeta_readme

result = codemeta_readme.get("https://github.com/pallets/flask")
if result:
    print(result["readme"][:200])  # Print first 200 chars
```

### Use with CodeMeta generator
```python
from src.codemeta_generator import generate

metadata = generate("https://github.com/pallets/flask")
if "readme" in metadata:
    print(f"README length: {len(metadata['readme'])} characters")
```

### Extract README from multiple repositories
```python
from src.modules import codemeta_readme

repos = [
    "https://github.com/tensorflow/tensorflow",
    "https://github.com/pallets/flask",
    "https://github.com/rust-lang/rust"
]

for repo_url in repos:
    result = codemeta_readme.get(repo_url)
    if result:
        print(f"Found README: {len(result['readme'])} chars")
    else:
        print(f"No README for {repo_url}")
```

### Get README URL
```python
from src.modules import codemeta_readme

url = codemeta_readme.get_readme_url("pallets", "flask")
print(f"README URL: {url}")
# Output: README URL: https://raw.githubusercontent.com/pallets/flask/main/README.md
```

### Search for specific content in README
```python
from src.modules import codemeta_readme

result = codemeta_readme.get("https://github.com/pallets/flask")
if result:
    readme = result["readme"]
    if "installation" in readme.lower():
        print("Found installation instructions")
    if "license" in readme.lower():
        print("Found license information")
```
