# Author Affiliation URL Resolution

## Overview

The Codemeta generator now automatically resolves organization affiliations to their official URLs. This enhancement enriches author metadata by adding semantic links to organizations, improving metadata completeness and enabling better knowledge graph integration.

## Feature Description

When extracting author information, the generator now:

1. **Identifies organization affiliations** from author metadata
2. **Resolves organization names to URLs** using multiple strategies
3. **Enriches affiliation objects** with official website URLs
4. **Caches results** for performance optimization

## Example

### Before
```json
{
  "author": [
    {
      "@type": "Person",
      "name": "Jacco van Ossenbruggen",
      "affiliation": {
        "@type": "Organization",
        "name": "VU"
      }
    }
  ]
}
```

### After
```json
{
  "author": [
    {
      "@type": "Person",
      "name": "Jacco van Ossenbruggen",
      "affiliation": {
        "@type": "Organization",
        "name": "VU",
        "url": "https://www.vu.nl"
      }
    }
  ]
}
```

## Implementation Details

### OrganizationURLResolver Class

Located in `src/organization_url_resolver.py`, this service provides organization URL resolution with the following strategies:

#### 1. Known Organizations Database
A curated list of common organizations with their official URLs:
- Universities: MIT, Stanford, Harvard, Oxford, Cambridge, VU, UvA, etc.
- Research institutions: Max Planck, CERN, NASA, etc.
- Technology companies: IBM, Microsoft, Google, Apple, Amazon, etc.
- Open source organizations: Apache, Mozilla, Linux Foundation, etc.

#### 2. Wikidata Lookup
For organizations not in the known database, the resolver queries Wikidata:
- Searches for the organization entity in Wikidata
- Extracts the official website (P856 property)
- Validates the URL format

#### 3. Web Search Fallback
If Wikidata lookup fails, the resolver performs a web search:
- Uses DuckDuckGo API for privacy-respecting search
- Extracts URLs from search results
- Validates that the domain matches the organization name
- Normalizes URLs to HTTPS with consistent formatting

#### 4. Caching
All resolved URLs are cached in memory to avoid repeated lookups:
- Improves performance for repositories with multiple authors from the same organization
- Cache can be cleared with `clear_cache()` method

### Integration with Author Property

The `AuthorMetadata` class (`src/properties/author.py`) has been enhanced to:

1. Initialize an `OrganizationURLResolver` instance
2. Call the resolver when creating affiliation objects
3. Add the resolved URL to the affiliation object if found

## Supported Organizations

### Universities
- VU (Vrije Universiteit Amsterdam) → https://www.vu.nl
- UvA (University of Amsterdam) → https://www.uva.nl
- MIT → https://www.mit.edu
- Stanford → https://www.stanford.edu
- Harvard → https://www.harvard.edu
- University of Oxford → https://www.ox.ac.uk
- University of Cambridge → https://www.cam.ac.uk
- ETH Zurich → https://www.ethz.ch

### Research Institutions
- Max Planck Society → https://www.mpg.de
- CERN → https://www.cern.ch
- NASA → https://www.nasa.gov

### Technology Companies
- IBM → https://www.ibm.com
- Microsoft → https://www.microsoft.com
- Google → https://www.google.com
- Apple → https://www.apple.com
- Amazon → https://www.amazon.com
- Meta (Facebook) → https://www.meta.com

### Open Source Organizations
- Apache Software Foundation → https://www.apache.org
- Mozilla Foundation → https://www.mozilla.org
- Linux Foundation → https://www.linuxfoundation.org
- Python Software Foundation → https://www.python.org
- W3C → https://www.w3.org
- IETF → https://www.ietf.org

## Usage

### Command Line
The feature is automatically applied when generating Codemeta:

```bash
python codemeta_gen.py https://github.com/jrvosse/amalgame
```

### Programmatic
```python
from src.generator import CodemetaGenerator

generator = CodemetaGenerator()
codemeta = generator.generate("https://github.com/jrvosse/amalgame")

# Author affiliations now include URLs
for author in codemeta.get('author', []):
    if 'affiliation' in author:
        print(f"Organization: {author['affiliation']['name']}")
        if 'url' in author['affiliation']:
            print(f"URL: {author['affiliation']['url']}")
```

### Direct Usage
```python
from src.organization_url_resolver import OrganizationURLResolver

resolver = OrganizationURLResolver()
url = resolver.resolve_organization_url("VU")
# Returns: "https://www.vu.nl"
```

## Configuration

### Adding Known Organizations
To add more organizations to the known database, edit the `KNOWN_ORGANIZATIONS` dictionary in `src/organization_url_resolver.py`:

```python
KNOWN_ORGANIZATIONS = {
    'organization_name': 'https://official.url',
    'vu': 'https://www.vu.nl',
    # ... more organizations
}
```

### Adjusting Timeout
The resolver has a configurable timeout for network requests (default: 5 seconds):

```python
resolver = OrganizationURLResolver(timeout=10)
```

## Performance Considerations

- **First lookup**: May take 1-2 seconds per organization (includes network requests)
- **Cached lookups**: Instant (in-memory cache)
- **Batch processing**: For repositories with many authors from the same organization, caching provides significant speedup

## Error Handling

The resolver gracefully handles failures:
- If a URL cannot be resolved, the affiliation object is created without a URL
- No exceptions are raised; the process continues
- Failed lookups are cached to avoid repeated attempts

## Testing

Test scripts are provided:

### Unit Tests
```bash
python test_org_resolver.py
```

Tests the resolver with known organizations and verifies URL resolution.

### Integration Tests
```bash
python test_amalgame.py
```

Tests the complete Codemeta generation pipeline with the amalgame repository, verifying that author affiliations include resolved URLs.

## Future Enhancements

Potential improvements:
1. **ROR (Research Organization Registry)** integration for academic institutions
2. **Configurable URL sources** (e.g., custom organization databases)
3. **Confidence scoring** for resolved URLs
4. **Batch resolution** with parallel requests
5. **URL validation** to verify resolved URLs are still active
6. **Organization disambiguation** for ambiguous names

## References

- [Codemeta 3.1 Specification](https://codemeta.github.io/)
- [Schema.org Person](https://schema.org/Person)
- [Schema.org Organization](https://schema.org/Organization)
- [Wikidata](https://www.wikidata.org/)
- [Research Organization Registry (ROR)](https://ror.org/)

## Author

Ronald Siebes (r.m.siebes@vu.nl)
ORCID: 0000-0001-8772-7904
