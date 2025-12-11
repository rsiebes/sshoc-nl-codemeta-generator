# CodeMeta Author Module Implementation

## Overview

The `codemeta_author.py` module is responsible for extracting comprehensive author and contributor information from GitHub repositories. This module implements multiple extraction strategies and enriches author data with ORCID identifiers when available.

## Features

### Multi-Strategy Author Extraction

The module uses a prioritized approach to extract author information:

1. **GitHub API Contributors Endpoint** (Primary Strategy)
   - Fetches the contributors list from the GitHub API
   - Retrieves detailed user information including name, email, and affiliation
   - Limits to top 5 contributors by default
   - Most reliable and comprehensive source

2. **setup.py** (Python Projects)
   - Extracts `author` and `author_email` fields
   - Extracts `maintainer` field if available
   - Fallback for Python projects without modern configuration

3. **pyproject.toml** (Modern Python Projects)
   - Parses `[project]` section authors array
   - Supports multiple authors with name and email
   - Standard format for modern Python packaging

4. **package.json** (Node.js Projects)
   - Extracts `author` field (string or object format)
   - Extracts `contributors` array
   - Supports both "Name <email>" and object formats

### ORCID Identifier Enrichment

The module attempts to find ORCID identifiers for each author by:

1. Querying the ORCID public API with author name and email
2. Returning the ORCID identifier as an `@id` field in the author object
3. Gracefully handling cases where ORCID lookup fails or times out

**Note**: ORCID lookup is optional and does not block author extraction if unavailable.

## Author Data Structure

Each extracted author is represented as a CodeMeta Person object:

```json
{
  "name": "Author Name",
  "@type": "Person",
  "email": "author@example.com",
  "url": "https://github.com/username",
  "affiliation": "Organization Name",
  "@id": "https://orcid.org/0000-0001-2345-6789"
}
```

### Required Fields
- `name`: Author's name (required)
- `@type`: Always "Person" (required)

### Optional Fields
- `email`: Author's email address
- `url`: Author's GitHub profile URL
- `affiliation`: Author's organization or company
- `@id`: ORCID identifier (if found)

## Implementation Details

### Function: `get(repository_url: str) -> Dict`

Main entry point that orchestrates the author extraction process.

**Parameters:**
- `repository_url` (str): GitHub repository URL

**Returns:**
- Dictionary with `author` key containing list of author objects
- Empty dictionary if no authors found

**Example:**
```python
result = get("https://github.com/rsiebes/sshoc-nl-codemeta-generator")
# Returns:
# {
#   "author": [
#     {"name": "Ronald Siebes", "@type": "Person", "@id": "https://orcid.org/0000-0001-8772-7904"},
#     ...
#   ]
# }
```

### Function: `find_orcid_for_author(name: str, email: str = "") -> Optional[str]`

Searches the ORCID public registry for an author's ORCID identifier.

**Parameters:**
- `name` (str): Author's full name
- `email` (str, optional): Author's email address

**Returns:**
- ORCID identifier string (e.g., "0000-0001-2345-6789") if found
- None if not found or lookup fails

**Notes:**
- Uses ORCID public API (no authentication required)
- Searches by name and optionally by email
- Implements timeout and error handling
- Does not block author extraction if lookup fails

## Test Coverage

The module includes 15 comprehensive unit tests covering:

### Author Extraction Tests
- ✓ Extracting from GitHub API
- ✓ Extracting from setup.py
- ✓ Extracting from pyproject.toml
- ✓ Extracting from package.json (object and string formats)
- ✓ Handling missing files

### ORCID Lookup Tests
- ✓ Finding ORCID when available
- ✓ Handling ORCID not found
- ✓ Handling empty name

### Data Structure Tests
- ✓ Author has required fields (@type, name)
- ✓ Authors with ORCID have @id field
- ✓ Proper data structure validation

### Integration Tests
- ✓ get() returns dictionary
- ✓ get() with authors found
- ✓ get() with no authors found
- ✓ get() with invalid URL

**All 15 tests pass successfully.**

## Real Repository Examples

### Example 1: codemeta-generator

Repository: https://github.com/rsiebes/sshoc-nl-codemeta-generator

Generated authors:
```json
{
  "author": [
    {
      "name": "Jasen2009",
      "@type": "Person",
      "url": "https://github.com/Jasen2009"
    },
    {
      "name": "Ronald Siebes",
      "@type": "Person",
      "url": "https://github.com/rsiebes",
      "affiliation": "UCDS group, VU Amsterdam",
      "@id": "https://orcid.org/0000-0001-8772-7904"
    }
  ]
}
```

### Example 2: osmenrich

Repository: https://github.com/sodascience/osmenrich

Generated authors:
```json
{
  "author": [
    {
      "name": "Leonardo Vida",
      "@type": "Person",
      "url": "https://github.com/leonardovida",
      "affiliation": "@motherduckdb",
      "@id": "https://orcid.org/0000-0002-0461-016X"
    },
    {
      "name": "Jonathan de Bruin",
      "@type": "Person",
      "url": "https://github.com/J535D165",
      "affiliation": "Utrecht University",
      "@id": "https://orcid.org/0000-0002-4297-0502"
    },
    {
      "name": "Erik-Jan van Kesteren",
      "@type": "Person",
      "url": "https://github.com/vankesteren",
      "affiliation": "Assistant professor @UtrechtUniversity",
      "@id": "https://orcid.org/0000-0003-1548-1663"
    }
  ]
}
```

## Integration with Orchestrator

The `codemeta_author.py` module is automatically discovered and executed by the main orchestrator (`codemeta_generator.py`). The orchestrator:

1. Discovers the module in the `src/modules/` directory
2. Calls the `get()` function with the repository URL
3. Aggregates the returned author data into the final CodeMeta structure
4. Validates the complete metadata against the CodeMeta 3.1 schema

## Error Handling

The module implements robust error handling:

- **Missing files**: Gracefully falls back to next strategy
- **API failures**: Continues with next strategy if GitHub API is unavailable
- **Invalid data**: Filters out malformed author entries
- **ORCID lookup**: Silently fails without blocking author extraction
- **Network timeouts**: Implements 5-10 second timeouts on all API calls

## Performance Characteristics

- **GitHub API calls**: 1-2 calls per repository (contributors + user details)
- **ORCID lookups**: 1 call per author (optional, can be slow)
- **Typical execution time**: 2-5 seconds per repository
- **Rate limiting**: Respects GitHub API rate limits (60 requests/hour unauthenticated)

## Future Enhancements

Potential improvements for future versions:

1. **ORCID Caching**: Cache ORCID lookups to reduce API calls
2. **Email Resolution**: Attempt to find author emails from commit history
3. **Author Roles**: Distinguish between authors, contributors, and maintainers
4. **Affiliation Enrichment**: Look up author affiliations from ORCID
5. **Batch ORCID Lookup**: Implement batch ORCID API for efficiency
6. **GitHub Token Support**: Use authenticated API calls for higher rate limits

## Compliance

The module generates author information fully compliant with:

- **CodeMeta 3.1 Standard**: Uses Person schema with required and optional fields
- **JSON-LD Format**: Properly structured for JSON-LD serialization
- **ORCID Integration**: Uses standard ORCID URL format (https://orcid.org/{id})

## References

- [CodeMeta 3.1 Schema](https://raw.githubusercontent.com/codemeta/codemeta/3.1/codemeta.jsonld)
- [GitHub API Contributors](https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-repository-contributors)
- [ORCID Public API](https://github.com/ORCID/orcid-api-guide/blob/master/v3.0_read_only/public_api_guide.md)
