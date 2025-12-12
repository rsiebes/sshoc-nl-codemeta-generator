# CodeMeta Date Created Module

## Overview

The `codemeta_date_created.py` module extracts the creation date of a GitHub repository. It provides the date when the repository was first created in ISO 8601 format (YYYY-MM-DD).

## Implementation Details

### Date Information Extracted

The module extracts:
- **dateCreated**: The date when the repository was created (ISO 8601 format: YYYY-MM-DD)

### Data Source

The creation date is extracted from the GitHub API v3 repository endpoint:
- Repository metadata (`created_at` field)
- Converted from GitHub's ISO 8601 format with timezone to date-only format

### Date Format

- **Input**: GitHub API format with timezone (e.g., "2022-07-12T18:34:47Z")
- **Output**: ISO 8601 date format (e.g., "2022-07-12")

## Function Reference

### `get_creation_date_from_api(owner: str, repo: str) -> Optional[str]`

Get repository creation date from GitHub API.

**Parameters:**
- `owner` (str): Repository owner username
- `repo` (str): Repository name

**Returns:**
- str: ISO 8601 formatted creation date (YYYY-MM-DD)
- None: If creation date cannot be determined

### `get(repository_url: str) -> Dict`

Main entry point for extracting creation date from a GitHub repository.

**Parameters:**
- `repository_url` (str): Full GitHub repository URL (e.g., "https://github.com/owner/repo")

**Returns:**
- Dict: Dictionary with "dateCreated" key if date is found, empty dict otherwise

**Example:**
```python
from src.modules import codemeta_date_created

result = codemeta_date_created.get("https://github.com/tensorflow/tensorflow")
# Returns: {"dateCreated": "2015-11-07"}
```

## Testing

The module includes comprehensive unit tests covering:

1. **Basic Date Extraction**: Verify correct extraction of creation date
2. **Date Format Conversion**: Test conversion from GitHub format to ISO 8601
3. **Date Range Tests**: Test old and recent dates
4. **Error Handling Tests**: Test handling of missing or invalid data
5. **Real Repository Tests**: Test on actual repositories (TensorFlow, Flask, Rust, Dryad, osmenrich)
6. **Date Parsing Tests**: Test various date formats and edge cases
7. **Content Validation Tests**: Ensure date data is valid

**Run tests:**
```bash
python3 -m unittest tests.test_codemeta_date_created -v
```

## Test Results

All 19 tests pass successfully:

```
Ran 19 tests in 0.008s
OK
```

### Coverage

- Basic date extraction: ✓
- Date format conversion: ✓
- Recent date extraction: ✓
- Old date extraction: ✓
- Missing date handling: ✓
- API error handling: ✓
- Real repository testing: ✓
- Date parsing edge cases: ✓
- Content validation: ✓

## Real Repository Examples

### TensorFlow
- **Repository**: https://github.com/tensorflow/tensorflow
- **Date Created**: 2015-11-07
- **Age**: ~10 years

### Flask
- **Repository**: https://github.com/pallets/flask
- **Date Created**: 2010-04-06
- **Age**: ~15 years

### Rust
- **Repository**: https://github.com/rust-lang/rust
- **Date Created**: 2010-06-16
- **Age**: ~15 years

### Dryad
- **Repository**: https://github.com/Dryad-lang/Dryad
- **Date Created**: 2022-07-12
- **Age**: ~3 years

### osmenrich
- **Repository**: https://github.com/sodascience/osmenrich
- **Date Created**: 2021-02-09
- **Age**: ~4 years

## Integration with CodeMeta Generator

The module integrates seamlessly with the main CodeMeta generator:

```python
from src.codemeta_generator import generate

result = generate("https://github.com/tensorflow/tensorflow")
# result["dateCreated"] == "2015-11-07"
```

## CodeMeta 3.1 Compliance

The module generates output fully compliant with CodeMeta 3.1 standard:

- ✅ Valid ISO 8601 date format
- ✅ Proper property naming
- ✅ Valid data type (string)
- ✅ No schema violations

## Error Handling

The module implements robust error handling:

- **Invalid URLs**: Returns empty dict for invalid repository URLs
- **Missing Data**: Gracefully handles missing creation date
- **API Errors**: Handles GitHub API failures gracefully
- **Invalid Dates**: Skips invalid date formats

## Validation Rules

1. **Required Format**: Date must be in ISO 8601 format (YYYY-MM-DD)
2. **Valid Range**: Date must be after GitHub was founded (2008)
3. **Not Future**: Date must not be in the future
4. **String Type**: Date must be a string value
5. **Non-empty**: Date must not be empty

## Output Structure

```json
{
  "dateCreated": "2022-07-12"
}
```

## Dependencies

- `datetime`: For date parsing and formatting
- `src.github_api`: Custom GitHub API utilities module

## Notes

- GitHub API returns creation date in ISO 8601 format with timezone
- Module converts to date-only format for CodeMeta compliance
- Creation date is immutable (never changes after repository creation)
- All dates are in UTC timezone
- Leap years are handled correctly

## Future Enhancements

Potential improvements for future versions:

1. **Timezone Support**: Include timezone information
2. **Time Information**: Include creation time (not just date)
3. **Age Calculation**: Calculate repository age
4. **Date Range Filtering**: Filter repositories by creation date
5. **Statistics**: Generate statistics on repository creation trends

## Compliance

- **CodeMeta 3.1 Standard**: Fully compliant with CodeMeta 3.1 schema
- **JSON-LD Format**: Valid JSON-LD output
- **GitHub API**: Uses GitHub REST API v3
- **Python 3.8+**: Compatible with Python 3.8 and later
- **ISO 8601**: Compliant with ISO 8601 date standard

## Performance

- **API Calls**: 1 call per repository
- **Response Time**: < 1 second typical
- **Caching**: No caching (fresh data on each call)
- **Rate Limiting**: Respects GitHub API rate limits

## Security

- **Token Support**: Uses GitHub token for authentication (if available)
- **HTTPS Only**: All API calls use HTTPS protocol
- **No Data Modification**: Read-only operation

## Examples

### Extract creation date from a single repository
```python
from src.modules import codemeta_date_created

result = codemeta_date_created.get("https://github.com/pallets/flask")
print(result)
# Output: {"dateCreated": "2010-04-06"}
```

### Use with CodeMeta generator
```python
from src.codemeta_generator import generate

metadata = generate("https://github.com/tensorflow/tensorflow")
print(f"Project created: {metadata['dateCreated']}")
# Output: Project created: 2015-11-07
```

### Calculate repository age
```python
from src.modules import codemeta_date_created
from datetime import datetime

result = codemeta_date_created.get("https://github.com/rust-lang/rust")
if result:
    created_date = datetime.strptime(result["dateCreated"], "%Y-%m-%d")
    age = (datetime.now() - created_date).days / 365.25
    print(f"Repository age: {age:.1f} years")
```
