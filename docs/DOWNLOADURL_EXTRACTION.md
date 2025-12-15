# Download URL Property Extraction Documentation

## Overview

The `downloadUrl` property extracts URLs where users can download software binaries, executables, or packages. This document details the extraction logic for both GitHub and non-GitHub repositories.

## Property Specification

- **Property**: downloadUrl
- **Type**: URL
- **Namespace**: schema.org
- **Description**: URL to download the binary/executable/package

## Extraction Strategy

### Priority Order

1. **Direct metadata field** - `downloadUrl` field in repository metadata
2. **Latest release assets** - Binary/package files from releases
3. **Package registry** - PyPI, npm, Maven, RubyGems, CRAN
4. **Archive download** - Source code archives (zip/tar.gz)
5. **Releases page** - General releases page URL

## GitHub Repositories

### 1. Latest Release Assets

**Source**: GitHub Releases API `/repos/{owner}/{repo}/releases/latest`

**Extraction Logic**:
```python
# Check if releases data is available
releases = metadata.get('releases', [])
if releases and len(releases) > 0:
    latest_release = releases[0]
    assets = latest_release.get('assets', [])
    if assets:
        # Return first asset download URL
        return assets[0]['browser_download_url']
```

**Example URLs**:
- `https://github.com/owner/repo/releases/download/v1.0.0/app.exe`
- `https://github.com/owner/repo/releases/download/v1.0.0/package.tar.gz`

### 2. Constructed Release URL

If version is known but assets aren't available:
```python
repo_url = "https://github.com/owner/repo"
version = "v1.0.0"
download_url = f"{repo_url}/releases/download/{version}"
```

### 3. Latest Release Page

Fallback to latest release page:
```
https://github.com/owner/repo/releases/latest
```

### 4. Archive Download

Source code archive:
```python
# With version tag
f"{repo_url}/archive/refs/tags/{version}.zip"

# Default branch
f"{repo_url}/archive/refs/heads/main.zip"
```

**Examples**:
- `https://github.com/owner/repo/archive/refs/tags/v1.0.0.zip`
- `https://github.com/owner/repo/archive/refs/heads/main.zip`

### 5. Releases Page

General releases page:
```
https://github.com/owner/repo/releases
```

## Non-GitHub Repositories

### GitLab

#### Release Assets

**API**: `/api/v4/projects/:id/releases`

**Extraction Logic**:
```python
if 'gitlab' in repo_url:
    # Extract project ID or path
    project_path = extract_gitlab_project_path(repo_url)
    
    # Fetch releases
    api_url = f"{instance_url}/api/v4/projects/{quote(project_path)}/releases"
    releases = fetch_json(api_url)
    
    if releases and len(releases) > 0:
        latest = releases[0]
        # Check for release links
        links = latest.get('assets', {}).get('links', [])
        if links:
            return links[0]['url']
```

#### Archive Download

```python
# With version and name
f"{repo_url}/-/archive/{version}/{name}-{version}.tar.gz"

# Example
"https://gitlab.com/owner/project/-/archive/v1.0.0/project-v1.0.0.tar.gz"
```

#### Releases Page

```
https://gitlab.com/owner/project/-/releases
```

### Bitbucket

#### Downloads Section

**API**: `/2.0/repositories/{workspace}/{repo_slug}/downloads`

**Extraction Logic**:
```python
if 'bitbucket.org' in repo_url:
    workspace, repo_slug = extract_bitbucket_info(repo_url)
    
    # Fetch downloads
    api_url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/downloads"
    downloads = fetch_json(api_url)
    
    if downloads and 'values' in downloads:
        files = downloads['values']
        if files:
            return files[0]['links']['self']['href']
```

#### Archive Download

```python
# With version tag
f"{repo_url}/get/{version}.zip"

# Example
"https://bitbucket.org/owner/repo/get/v1.0.0.zip"
```

#### Downloads Page

```
https://bitbucket.org/owner/repo/downloads/
```

### SourceForge

#### Files API

**API**: `/rest/p/{project}/files`

**Extraction Logic**:
```python
if 'sourceforge.net' in repo_url:
    project_name = extract_sourceforge_project(repo_url)
    
    # Fetch files
    api_url = f"https://sourceforge.net/rest/p/{project_name}/files"
    files = fetch_json(api_url)
    
    # Find latest release
    if files and 'files' in files:
        # Navigate to latest version folder
        latest_folder = find_latest_version_folder(files['files'])
        # Get download URL for main file
        return construct_sourceforge_download_url(project_name, latest_folder)
```

**Download URL Format**:
```
https://sourceforge.net/projects/{project}/files/latest/download
https://sourceforge.net/projects/{project}/files/{version}/{file}/download
```

### Package Registries

Package registries provide distribution packages rather than source archives.

#### PyPI (Python)

**Detection**: `programmingLanguage` contains "Python"

**URL Format**:
```python
package_name = metadata['name']
download_url = f"https://pypi.org/project/{package_name}/"
```

**Example**: `https://pypi.org/project/requests/`

**Direct Package Download**:
```
https://pypi.org/project/{name}/#files
```

#### npm (JavaScript/Node.js)

**Detection**: `programmingLanguage` contains "JavaScript", "TypeScript", or "Node"

**URL Format**:
```python
package_name = metadata['name']
download_url = f"https://www.npmjs.com/package/{package_name}"
```

**Example**: `https://www.npmjs.com/package/express`

#### Maven Central (Java)

**Detection**: `programmingLanguage` contains "Java"

**URL Format**:
```python
# Requires group ID and artifact ID
group_id = metadata.get('maven_group_id', 'unknown')
artifact_id = metadata['name']
download_url = f"https://search.maven.org/artifact/{group_id}/{artifact_id}"
```

**Example**: `https://search.maven.org/artifact/org.apache.commons/commons-lang3`

#### RubyGems (Ruby)

**Detection**: `programmingLanguage` contains "Ruby"

**URL Format**:
```python
gem_name = metadata['name']
download_url = f"https://rubygems.org/gems/{gem_name}"
```

**Example**: `https://rubygems.org/gems/rails`

#### CRAN (R)

**Detection**: `programmingLanguage` is "R"

**URL Format**:
```python
package_name = metadata['name']
download_url = f"https://cran.r-project.org/package={package_name}"
```

**Example**: `https://cran.r-project.org/package=ggplot2`

#### Cargo (Rust)

**Detection**: `programmingLanguage` contains "Rust"

**URL Format**:
```python
crate_name = metadata['name']
download_url = f"https://crates.io/crates/{crate_name}"
```

**Example**: `https://crates.io/crates/serde`

#### Go Packages

**Detection**: `programmingLanguage` contains "Go"

**URL Format**:
```python
# Go packages are typically downloaded via go get
# Use pkg.go.dev for documentation and discovery
module_path = metadata.get('go_module_path', metadata['name'])
download_url = f"https://pkg.go.dev/{module_path}"
```

**Example**: `https://pkg.go.dev/github.com/gin-gonic/gin`

### Institutional Repositories

#### Institutional GitLab

Same as GitLab, but with custom instance URL:

```python
if 'gitlab' in repo_url and 'gitlab.com' not in repo_url:
    instance_url = extract_instance_url(repo_url)
    # Use GitLab API with custom instance
    api_url = f"{instance_url}/api/v4/projects/{project_id}/releases"
```

**Examples**:
- `https://gitlab.inria.fr/owner/project/-/releases`
- `https://git.rwth-aachen.de/owner/project/-/releases`

#### Gitea Instances

**API**: Similar to GitHub API

```python
if is_gitea_instance(repo_url):
    instance_url = extract_instance_url(repo_url)
    owner, repo = extract_owner_repo(repo_url)
    
    # Gitea releases API
    api_url = f"{instance_url}/api/v1/repos/{owner}/{repo}/releases"
    releases = fetch_json(api_url)
    
    if releases:
        return releases[0]['assets'][0]['browser_download_url']
```

### Generic Git Repositories

For repositories without a web interface:

1. **Clone and check for distribution files**:
```python
repo_path = clone_repository(repo_url, depth=1)
dist_files = find_distribution_files(repo_path)
# Look for: *.tar.gz, *.zip, *.exe, *.dmg in dist/ or build/
```

2. **Construct archive URL if hosted**:
```python
# Some Git servers support archive downloads
f"{repo_url}/archive/HEAD.tar.gz"
```

## Validation

The downloadUrl module validates:

1. **Format**: Must be a string
2. **URL structure**: Must start with `http://` or `https://`
3. **Direct download vs. page**: Warns if URL points to a page rather than direct download

**Warning issued for**:
- `/releases` pages without file extension
- `/downloads` pages without file extension
- Package registry pages (which require additional clicks)

**No warning for**:
- Direct file URLs (`.zip`, `.tar.gz`, `.exe`, `.dmg`, etc.)
- Package registry URLs (expected behavior)

## Testing

### Test Cases

1. **GitHub repository with releases** - Extract latest release asset
2. **GitHub repository without releases** - Fall back to archive URL
3. **Python package** - Extract PyPI URL
4. **JavaScript package** - Extract npm URL
5. **GitLab repository** - Extract release or archive
6. **Bitbucket repository** - Extract downloads or archive

### Example Test Repositories

- **With releases**: `https://github.com/atom/atom` (has release assets)
- **Python package**: `https://github.com/psf/requests` (on PyPI)
- **JavaScript package**: `https://github.com/expressjs/express` (on npm)

## Future Enhancements

1. **GitHub API integration** - Fetch actual release assets
2. **Package registry APIs** - Get direct download links
3. **Multiple download URLs** - Support array of download options
4. **Platform-specific downloads** - Separate URLs for Windows/Mac/Linux
5. **Checksum validation** - Include checksums for downloads
6. **File size information** - Include download size

## References

- [GitHub Releases API](https://docs.github.com/en/rest/releases)
- [GitLab Releases API](https://docs.gitlab.com/ee/api/releases/)
- [Bitbucket Downloads API](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-downloads/)
- [PyPI JSON API](https://warehouse.pypa.io/api-reference/json.html)
- [npm Registry API](https://github.com/npm/registry/blob/master/docs/REGISTRY-API.md)
- [Codemeta Specification](https://codemeta.github.io/)
