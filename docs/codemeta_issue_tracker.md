# CodeMeta Issue Tracker Module

## Overview

The `codemeta_issue_tracker.py` module extracts the issue tracker information from a GitHub repository. It provides the URL to the repository's issue tracking system.

## Implementation Details

### Issue Tracker Information Extracted

The module extracts:
- **issueTracker**: The URL to the repository's issue tracker

### Data Source

The issue tracker URL is extracted from the GitHub API v3 repository endpoint:
- Repository metadata (`has_issues` field)
- Constructs the standard GitHub issues URL

### URL Format

- **Output**: GitHub issues URL (e.g., "https://github.com/owner/repo/issues")
- **Standard Format**: `https://github.com/{owner}/{repo}/issues`

## Function Reference

### `get_issue_tracker_url(owner: str, repo: str) -> Optional[str]`

Get issue tracker URL from GitHub repository.

**Parameters:**
- `owner` (str): Repository owner username
- `repo` (str): Repository name

**Returns:**
- str: Issue tracker URL if issues are enabled
- None: If issues are disabled or not found

### `get(repository_url: str) -> Dict`

Main entry point for extracting issue tracker information from a GitHub repository.

**Parameters:**
- `repository_url` (str): Full GitHub repository URL (e.g., "https://github.com/owner/repo")

**Returns:**
- Dict: Dictionary with "issueTracker" key if issue tracker is found, empty dict otherwise

**Example:**
```python
from src.modules import codemeta_issue_tracker

result = codemeta_issue_tracker.get("https://github.com/tensorflow/tensorflow")
# Returns: {"issueTracker": "https://github.com/tensorflow/tensorflow/issues"}
```

## Testing

The module includes comprehensive unit tests covering:

1. **Basic Extraction**: Verify correct extraction of issue tracker URL
2. **Issue Status Tests**: Test handling of enabled/disabled issues
3. **Error Handling Tests**: Test handling of missing or invalid data
4. **Real Repository Tests**: Test on actual repositories
5. **URL Format Tests**: Test URL construction with various names
6. **Content Validation Tests**: Ensure URL data is valid

**Run tests:**
```bash
python3 -m unittest tests.test_codemeta_issue_tracker -v
```

## Test Results

All 20 tests pass successfully:

```
Ran 20 tests in 0.008s
OK
```

### Coverage

- Basic issue tracker extraction: ✓
- Issue tracker enabled/disabled handling: ✓
- URL format validation: ✓
- Real repository testing: ✓
- URL construction with special characters: ✓
- Content validation: ✓
- Error handling: ✓

## Real Repository Examples

### TensorFlow
- **Repository**: https://github.com/tensorflow/tensorflow
- **Issue Tracker**: https://github.com/tensorflow/tensorflow/issues
- **Status**: Issues enabled

### Flask
- **Repository**: https://github.com/pallets/flask
- **Issue Tracker**: https://github.com/pallets/flask/issues
- **Status**: Issues enabled

### Rust
- **Repository**: https://github.com/rust-lang/rust
- **Issue Tracker**: https://github.com/rust-lang/rust/issues
- **Status**: Issues enabled

### Dryad
- **Repository**: https://github.com/Dryad-lang/Dryad
- **Issue Tracker**: https://github.com/Dryad-lang/Dryad/issues
- **Status**: Issues enabled

## Integration with CodeMeta Generator

The module integrates seamlessly with the main CodeMeta generator:

```python
from src.codemeta_generator import generate

result = generate("https://github.com/tensorflow/tensorflow")
# result["issueTracker"] == "https://github.com/tensorflow/tensorflow/issues"
```

## CodeMeta 3.1 Compliance

The module generates output fully compliant with CodeMeta 3.1 standard:

- ✅ Valid URL format
- ✅ Proper property naming
- ✅ Valid data type (string)
- ✅ No schema violations

## Error Handling

The module implements robust error handling:

- **Issues Disabled**: Returns empty dict when issues are disabled
- **Missing Data**: Gracefully handles missing issue tracker information
- **API Errors**: Handles GitHub API failures gracefully
- **Invalid URLs**: Skips invalid repository URLs

## Validation Rules

1. **Issues Enabled**: Only returns URL if `has_issues` is True
2. **URL Format**: URL must follow GitHub standard format
3. **String Type**: URL must be a string value
4. **Non-empty**: URL must not be empty

## Output Structure

```json
{
  "issueTracker": "https://github.com/owner/repo/issues"
}
```

## Issue Tracker Status

GitHub repositories can have issues enabled or disabled:

- **Enabled**: Repository has an active issue tracker
- **Disabled**: Repository does not have an issue tracker

The module only returns the issue tracker URL if issues are explicitly enabled.

## Dependencies

- `src.github_api`: Custom GitHub API utilities module

## Notes

- GitHub issues are enabled by default for new repositories
- The issue tracker URL is always the standard GitHub issues page
- Some repositories may use external issue trackers, but this module only detects GitHub's built-in tracker
- The URL is constructed from the owner and repository name
- All URLs are HTTPS protocol

## GitHub Issues Features

The GitHub issues tracker provides:

- **Issue Creation**: Users can create new issues
- **Issue Discussion**: Comments and discussion on issues
- **Issue Labels**: Categorization with labels
- **Issue Milestones**: Grouping by milestones
- **Issue Assignment**: Assignment to team members
- **Pull Request Integration**: Linking to pull requests

## Use Cases

1. **Software Metadata**: Include issue tracker in software metadata
2. **Project Discovery**: Find how to report issues for a project
3. **Community Engagement**: Direct users to report bugs
4. **Project Health**: Assess project maintenance through issue activity
5. **Integration**: Link to issue tracker from other systems

## Future Enhancements

Potential improvements for future versions:

1. **External Trackers**: Detect external issue trackers (Jira, Bugzilla, etc.)
2. **Issue Statistics**: Count open/closed issues
3. **Issue Activity**: Analyze issue creation/resolution rates
4. **Issue Labels**: Extract common issue labels
5. **Issue Templates**: Detect issue templates

## Compliance

- **CodeMeta 3.1 Standard**: Fully compliant with CodeMeta 3.1 schema
- **JSON-LD Format**: Valid JSON-LD output
- **GitHub API**: Uses GitHub REST API v3
- **Python 3.8+**: Compatible with Python 3.8 and later

## Performance

- **API Calls**: 1 call per repository
- **Response Time**: < 1 second typical
- **Caching**: No caching (fresh data on each call)
- **Rate Limiting**: Respects GitHub API rate limits

## Security

- **Token Support**: Uses GitHub token for authentication (if available)
- **HTTPS Only**: All URLs use HTTPS protocol
- **No Data Modification**: Read-only operation

## Examples

### Extract issue tracker from a single repository
```python
from src.modules import codemeta_issue_tracker

result = codemeta_issue_tracker.get("https://github.com/tensorflow/tensorflow")
print(result)
# Output: {"issueTracker": "https://github.com/tensorflow/tensorflow/issues"}
```

### Use with CodeMeta generator
```python
from src.codemeta_generator import generate

metadata = generate("https://github.com/pallets/flask")
print(f"Report issues at: {metadata.get('issueTracker', 'Not found')}")
# Output: Report issues at: https://github.com/pallets/flask/issues
```

### Check multiple repositories
```python
from src.modules import codemeta_issue_tracker

repos = [
    "https://github.com/tensorflow/tensorflow",
    "https://github.com/pallets/flask",
    "https://github.com/rust-lang/rust"
]

for repo_url in repos:
    result = codemeta_issue_tracker.get(repo_url)
    if result:
        print(f"Issues: {result['issueTracker']}")
    else:
        print(f"No issue tracker for {repo_url}")
```

### Generate issue tracker URLs for batch processing
```python
from src.modules import codemeta_issue_tracker

repo_list = [
    "https://github.com/owner1/repo1",
    "https://github.com/owner2/repo2",
    "https://github.com/owner3/repo3"
]

issue_trackers = {}
for repo_url in repo_list:
    result = codemeta_issue_tracker.get(repo_url)
    if result:
        issue_trackers[repo_url] = result["issueTracker"]

for repo, tracker in issue_trackers.items():
    print(f"{repo} -> {tracker}")
```
