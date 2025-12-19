# Generic Organization URL Resolver

## Overview

The organization URL resolver is a generic, online-only service that resolves any organization name to its official website URL. It uses multiple online lookup strategies without relying on any hardcoded database, making it work with any GitHub repository and any organization name.

## Key Features

✅ **Generic Online Lookup**
- No hardcoded organization database
- Works with any organization name
- Uses multiple online sources for comprehensive coverage

✅ **Multiple Lookup Strategies**
1. **Wikidata** - For known organizations with structured data
2. **ROR (Research Organization Registry)** - For academic institutions
3. **Web Search** - DuckDuckGo and Bing for general organizations

✅ **Intelligent Domain Matching**
- Handles variations like "Axel Springer" → "axelspringer.com"
- Supports abbreviations and acronyms
- Strict matching mode to avoid false positives

✅ **Performance Optimization**
- In-memory caching to avoid repeated lookups
- Graceful error handling with fallback strategies

## How It Works

### Lookup Process

```
Organization Name Input
    ↓
[1] Wikidata Lookup
    - Exact match query
    - Fuzzy match with CONTAINS filter
    ↓ (if found)
Return URL
    ↓ (if not found)
[2] ROR API Lookup
    - Search Research Organization Registry
    - Extract organization website
    ↓ (if found)
Return URL
    ↓ (if not found)
[3] Web Search
    - Multiple search queries
    - DuckDuckGo search
    - Bing search (fallback)
    - Intelligent domain matching
    ↓ (if found)
Return URL
    ↓ (if not found)
Return None (cache failure)
```

### Domain Matching Algorithm

The resolver uses intelligent matching to identify the correct organization domain:

1. **Exact Match**: Organization name appears directly in domain
   - "Axel Springer" → "axelspringer.com" ✅

2. **Multi-Part Matching**: All parts of organization name in domain
   - "Max Planck" → "mpg.de" (via acronym detection)

3. **First-Part Matching**: Main organization name in domain
   - "University of Amsterdam" → "uva.nl"

4. **Acronym Detection**: Common patterns recognized
   - "Vrije Universiteit" → "vu.nl"
   - "Max Planck" → "mpg.de"

5. **Fuzzy Matching**: 60%+ character overlap
   - Handles typos and variations

## Supported Lookup Sources

### Wikidata
- **Endpoint**: https://query.wikidata.org/sparql
- **Query**: Searches for organizations (Q43229) with official websites (P856)
- **Coverage**: ~10 million organizations
- **Speed**: 1-2 seconds per lookup

### ROR (Research Organization Registry)
- **API**: https://api.ror.org/organizations
- **Coverage**: ~100,000 academic and research institutions
- **Speed**: <1 second per lookup
- **Specialization**: Academic institutions, research centers

### Web Search
- **Primary**: DuckDuckGo API (privacy-friendly)
- **Fallback**: Bing search
- **Query Strategies**:
  - `"{org_name}" official website`
  - `"{org_name}" homepage`
  - `{org_name} organization website`
- **Speed**: 1-2 seconds per lookup

## Usage Examples

### Basic Usage

```python
from src.organization_url_resolver import OrganizationURLResolver

resolver = OrganizationURLResolver()

# Resolve any organization name
url = resolver.resolve_organization_url("Axel Springer")
# Returns: https://www.axelspringer.com

url = resolver.resolve_organization_url("Max Planck")
# Returns: https://www.mpg.de

url = resolver.resolve_organization_url("VU")
# Returns: https://www.vu.nl
```

### Integration with Author Properties

```python
from src.properties.author import AuthorMetadata

raw_data = {
    'author': [
        {
            'name': 'Bo Liu',
            'organization': 'Axel Springer'
        }
    ]
}

author_metadata = AuthorMetadata(raw_data)
result = author_metadata.extract()

# Result includes:
# {
#   "author": [{
#     "name": "Bo Liu",
#     "affiliation": {
#       "@type": "Organization",
#       "name": "Axel Springer",
#       "url": "https://www.axelspringer.com"
#     }
#   }]
# }
```

### Caching

```python
resolver = OrganizationURLResolver()

# First lookup (slow, makes network requests)
url1 = resolver.resolve_organization_url("Axel Springer")  # ~1-2 seconds

# Second lookup (fast, from cache)
url2 = resolver.resolve_organization_url("Axel Springer")  # <1ms

# Clear cache if needed
resolver.clear_cache()
```

## Real-World Examples

### Example 1: OnlySwitch Repository
**Repository**: https://github.com/jacklandrin/OnlySwitch
**Author**: Bo Liu
**Affiliation**: Axel Springer

**Result**:
```json
{
  "affiliation": {
    "@type": "Organization",
    "name": "Axel Springer",
    "url": "https://www.axelspringer.com"
  }
}
```

### Example 2: Amalgame Repository
**Repository**: https://github.com/jrvosse/amalgame
**Author**: Jacco van Ossenbruggen
**Affiliation**: VU

**Result**:
```json
{
  "affiliation": {
    "@type": "Organization",
    "name": "VU",
    "url": "https://www.vu.nl"
  }
}
```

## Performance Characteristics

| Scenario | Time | Notes |
|----------|------|-------|
| First lookup (Wikidata hit) | 1-2s | Network request + parsing |
| First lookup (ROR hit) | <1s | Faster API response |
| First lookup (Web search) | 1-2s | Search engine query |
| Cached lookup | <1ms | In-memory dictionary |
| Failed lookup (cached) | <1ms | Cached None result |
| Batch (5 authors, same org) | ~2s | First lookup + 4 cached |

## Error Handling

The resolver gracefully handles all error scenarios:

```python
resolver = OrganizationURLResolver()

# Returns None if not found (no exception)
url = resolver.resolve_organization_url("Unknown Organization XYZ")
# Returns: None

# Returns None for invalid input (no exception)
url = resolver.resolve_organization_url(None)
# Returns: None

url = resolver.resolve_organization_url("")
# Returns: None

# Returns None for network errors (no exception)
# (continues processing without disruption)
```

## Configuration

### Timeout

```python
# Default timeout: 5 seconds
resolver = OrganizationURLResolver()

# Custom timeout: 10 seconds
resolver = OrganizationURLResolver(timeout=10)
```

### Strict Matching

```python
# Used internally for web search to avoid false positives
# Requires at least 2 parts to match for multi-word organization names
# Automatically used in search results filtering
```

## Advantages Over Hardcoded Database

| Aspect | Hardcoded DB | Online Lookup |
|--------|--------------|---------------|
| **Coverage** | Limited (50-100 orgs) | Unlimited (millions) |
| **Maintenance** | Manual updates needed | Automatic (uses live data) |
| **Accuracy** | Fixed, may become outdated | Current, always up-to-date |
| **Genericity** | Works only for known orgs | Works for any organization |
| **Scalability** | Doesn't scale | Scales to any repository |
| **New Organizations** | Requires code changes | Automatic support |

## Limitations

1. **Network Dependency**: Requires internet connection
2. **Search Engine Variations**: Results may vary by search engine
3. **Ambiguous Names**: Very short names (e.g., "AI") may have false positives
4. **Rate Limiting**: Search engines may rate-limit requests
5. **Timeout**: Network requests have 5-second timeout

## Future Enhancements

1. **Persistent Cache**: Database or file-based caching
2. **Confidence Scoring**: Return confidence level with URL
3. **Batch Resolution**: Parallel requests for multiple organizations
4. **URL Validation**: Verify resolved URLs are still active
5. **Organization Hierarchy**: Support department/sub-organization resolution
6. **Custom Resolvers**: Pluggable resolver strategies

## Testing

### Unit Tests
```bash
python test_org_resolver.py
```

### Integration Tests
```bash
python test_improved_resolver.py
```

### Real Repository Tests
```bash
python test_onlyswitch_debug.py
python test_amalgame.py
```

## Implementation Details

### File Location
`src/organization_url_resolver.py`

### Class
`OrganizationURLResolver`

### Main Method
```python
def resolve_organization_url(self, organization_name: Optional[str]) -> Optional[str]:
    """
    Resolve an organization name to its URL using multiple strategies.
    
    Args:
        organization_name: Name of the organization
        
    Returns:
        URL of the organization or None if not found
    """
```

### Integration Points
- `src/properties/author.py` - Author affiliation resolution
- `src/properties/contributor.py` - Contributor affiliation resolution
- `src/properties/maintainer.py` - Maintainer affiliation resolution

## References

- [Wikidata](https://www.wikidata.org/)
- [Wikidata SPARQL Query Service](https://query.wikidata.org/)
- [ROR (Research Organization Registry)](https://ror.org/)
- [DuckDuckGo API](https://duckduckgo.com/api)
- [Bing Search](https://www.bing.com/)
- [Codemeta 3.1 Specification](https://codemeta.github.io/)
- [Schema.org Organization](https://schema.org/Organization)

## Author

Ronald Siebes (r.m.siebes@vu.nl)
ORCID: 0000-0001-8772-7904

## Date

December 2025
