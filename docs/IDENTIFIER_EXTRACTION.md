# Identifier Property Extraction Documentation

## Overview

The `identifier` property extracts persistent identifiers (DOI, ARK, PURL, SWHID, etc.) from software repositories. This document details the extraction logic for both GitHub and non-GitHub repositories.

## Supported Identifier Types

### 1. DOI (Digital Object Identifier)
- **Format**: `10.XXXX/suffix`
- **URL Format**: `https://doi.org/10.XXXX/suffix`
- **Example**: `https://doi.org/10.5281/zenodo.1234567`
- **Common Sources**: Zenodo, Figshare, DataCite

### 2. ARK (Archival Resource Key)
- **Format**: `ark:/NAAN/suffix`
- **URL Format**: `https://n2t.net/ark:/NAAN/suffix`
- **Example**: `https://n2t.net/ark:/12345/abc123`
- **Common Sources**: Archives, libraries

### 3. PURL (Persistent Uniform Resource Locator)
- **Format**: `http://purl.org/...`
- **Example**: `http://purl.org/example/software`
- **Common Sources**: PURL.org service

### 4. SWHID (Software Heritage Identifier)
- **Format**: `swh:1:TYPE:HASH`
- **URL Format**: `https://archive.softwareheritage.org/swh:1:TYPE:HASH`
- **Example**: `https://archive.softwareheritage.org/swh:1:dir:d198bc9d7a6bcf6db04f476d29314f157507d505`
- **Common Sources**: Software Heritage Archive

## Extraction Strategy

### Priority Order

1. **Direct metadata field** - `identifier` field in repository metadata
2. **CITATION.cff file** - Standard citation metadata file
3. **README content** - Badges, links, and text mentions
4. **Repository description** - About/description field
5. **Zenodo integration** - `.zenodo.json` file

### Extraction Logic by Repository Type

## GitHub Repositories

### 1. Direct Metadata Field
```python
# Check if identifier is explicitly provided in repository metadata
identifier = metadata.get('identifier')
```

### 2. CITATION.cff File
```yaml
# Example CITATION.cff structure
cff-version: 1.2.0
title: "My Software"
identifiers:
  - type: doi
    value: 10.5281/zenodo.1234567
```

**Extraction**: Parse CITATION.cff and extract DOI from `identifiers` field.

### 3. README Badges

**Common Badge Patterns**:

```markdown
# Zenodo DOI Badge
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1234567.svg)](https://doi.org/10.5281/zenodo.1234567)

# Direct DOI Badge
[![DOI](https://img.shields.io/badge/DOI-10.1234%2Fexample-blue)](https://doi.org/10.1234/example)

# Software Heritage Badge
[![SWH](https://archive.softwareheritage.org/badge/swh:1:dir:...)](https://archive.softwareheritage.org/swh:1:dir:...)
```

**Extraction**: Use regex patterns to find DOI, ARK, PURL, or SWHID in README content.

### 4. Repository Description
```
# GitHub "About" section may contain DOI
"A Python library for data analysis. DOI: 10.5281/zenodo.1234567"
```

**Extraction**: Search description text for identifier patterns.

### 5. Zenodo Integration
```json
// .zenodo.json file
{
  "title": "My Software",
  "doi": "10.5281/zenodo.1234567",
  "creators": [...]
}
```

**Extraction**: Parse `.zenodo.json` and extract DOI.

## Non-GitHub Repositories

### GitLab

**Extraction Sources**:
1. **Project metadata API** - `/api/v4/projects/:id`
2. **CITATION.cff** - Same as GitHub
3. **README** - Same pattern matching as GitHub
4. **Project description** - From project settings
5. **.gitlab-ci.yml** - May contain Zenodo integration

**Example API Call**:
```bash
curl "https://gitlab.com/api/v4/projects/PROJECT_ID"
```

**Extraction Logic**:
```python
# For GitLab repositories
if 'gitlab.com' in repo_url:
    # Extract project ID from URL
    project_id = extract_gitlab_project_id(repo_url)
    
    # Fetch project metadata
    api_url = f"https://gitlab.com/api/v4/projects/{project_id}"
    metadata = fetch_json(api_url)
    
    # Check for identifier in metadata
    identifier = metadata.get('identifier') or metadata.get('doi')
    
    # Fall back to README scanning
    if not identifier:
        identifier = extract_from_readme(metadata['readme_url'])
```

### Bitbucket

**Extraction Sources**:
1. **Repository API** - `/2.0/repositories/{workspace}/{repo_slug}`
2. **CITATION.cff** - If present in repository
3. **README** - Pattern matching
4. **Repository description** - From repository settings

**Example API Call**:
```bash
curl "https://api.bitbucket.org/2.0/repositories/WORKSPACE/REPO"
```

**Extraction Logic**:
```python
# For Bitbucket repositories
if 'bitbucket.org' in repo_url:
    # Extract workspace and repo slug
    workspace, repo_slug = extract_bitbucket_info(repo_url)
    
    # Fetch repository metadata
    api_url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}"
    metadata = fetch_json(api_url)
    
    # Check description for identifier
    description = metadata.get('description', '')
    identifier = extract_identifier_from_text(description)
    
    # Fall back to README
    if not identifier:
        identifier = extract_from_readme(repo_url)
```

### SourceForge

**Extraction Sources**:
1. **Project API** - `/rest/p/{project}/`
2. **Project metadata** - From project page
3. **README files** - In file listings
4. **Project description** - From summary

**Example API Call**:
```bash
curl "https://sourceforge.net/rest/p/PROJECT_NAME/"
```

**Extraction Logic**:
```python
# For SourceForge repositories
if 'sourceforge.net' in repo_url:
    # Extract project name
    project_name = extract_sourceforge_project(repo_url)
    
    # Fetch project metadata
    api_url = f"https://sourceforge.net/rest/p/{project_name}/"
    metadata = fetch_json(api_url)
    
    # Check short_description for identifier
    description = metadata.get('short_description', '')
    identifier = extract_identifier_from_text(description)
```

### Institutional GitLab/Gitea Instances

**Extraction Sources**:
1. **API endpoints** - Similar to GitLab
2. **CITATION.cff** - Standard location
3. **README** - Pattern matching
4. **Repository metadata** - From API

**Example**:
```python
# For institutional GitLab (e.g., gitlab.inria.fr)
if 'gitlab' in repo_url and 'gitlab.com' not in repo_url:
    # Parse instance URL
    instance_url = extract_instance_url(repo_url)
    project_path = extract_project_path(repo_url)
    
    # Try GitLab API
    api_url = f"{instance_url}/api/v4/projects/{quote(project_path)}"
    metadata = fetch_json(api_url)
    
    # Extract identifier from metadata or README
    identifier = metadata.get('identifier') or extract_from_readme(repo_url)
```

### Generic Git Repositories

**Extraction Sources**:
1. **CITATION.cff** - Clone and check for file
2. **README** - Clone and scan
3. **Root directory files** - Check for identifier files

**Extraction Logic**:
```python
# For generic Git repositories
if repo_url.endswith('.git') or 'git://' in repo_url:
    # Clone repository (shallow)
    repo_path = clone_repository(repo_url, depth=1)
    
    # Check for CITATION.cff
    citation_path = os.path.join(repo_path, 'CITATION.cff')
    if os.path.exists(citation_path):
        identifier = extract_from_citation_cff(citation_path)
    
    # Check README
    if not identifier:
        readme_path = find_readme(repo_path)
        if readme_path:
            identifier = extract_from_readme_file(readme_path)
```

## Regular Expression Patterns

### DOI Pattern
```python
DOI_PATTERN = r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+'
```

**Matches**:
- `10.5281/zenodo.1234567`
- `10.1234/example-software.v1.0`
- `10.1109/ACCESS.2021.1234567`

### ARK Pattern
```python
ARK_PATTERN = r'ark:/\d{5,}/[A-Za-z0-9]+'
```

**Matches**:
- `ark:/12345/abc123`
- `ark:/99999/fk4test`

### PURL Pattern
```python
PURL_PATTERN = r'http://purl\.org/[A-Za-z0-9/_-]+'
```

**Matches**:
- `http://purl.org/example/software`
- `http://purl.org/dc/terms/`

### SWHID Pattern
```python
SWHID_PATTERN = r'swh:1:(cnt|dir|rel|rev|snp):[0-9a-f]{40}'
```

**Matches**:
- `swh:1:dir:d198bc9d7a6bcf6db04f476d29314f157507d505`
- `swh:1:rev:309cf2674ee7a0749978cf8265ab91a60aea0f7d`

## Normalization

All extracted identifiers are normalized to URL format:

```python
# DOI normalization
"10.5281/zenodo.1234567" → "https://doi.org/10.5281/zenodo.1234567"

# ARK normalization
"ark:/12345/abc123" → "https://n2t.net/ark:/12345/abc123"

# SWHID normalization
"swh:1:dir:..." → "https://archive.softwareheritage.org/swh:1:dir:..."
```

## Validation

The identifier module validates:

1. **Format**: Must be a string
2. **URL structure**: Should start with `http://`, `https://`, or `urn:`
3. **DOI validity**: If DOI URL, check for valid DOI pattern
4. **Warnings**: Issues warnings for potentially invalid identifiers

## Testing

### Test Cases

1. **Repository with Zenodo DOI badge**
2. **Repository with CITATION.cff**
3. **Repository with DOI in description**
4. **Repository without identifier** (should return empty)
5. **Non-GitHub repository** (GitLab, Bitbucket)

### Example Test Repository

A good test case is a repository with a Zenodo DOI badge in the README, such as scientific software repositories that have been archived on Zenodo.

## Future Enhancements

1. **GitHub API integration** - Fetch CITATION.cff via API
2. **Zenodo API** - Query Zenodo for repository DOIs
3. **Software Heritage API** - Query for SWHID
4. **CITATION.cff parser** - Full YAML parsing
5. **Multiple identifiers** - Support array of identifiers
6. **Identifier validation** - Verify DOI resolution

## References

- [DOI Handbook](https://www.doi.org/doi_handbook/)
- [ARK Specification](https://arks.org/)
- [Software Heritage](https://www.softwareheritage.org/)
- [CITATION.cff Format](https://citation-file-format.github.io/)
- [Codemeta Specification](https://codemeta.github.io/)
