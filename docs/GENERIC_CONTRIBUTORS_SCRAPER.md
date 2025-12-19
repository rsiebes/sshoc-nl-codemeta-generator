# Generic GitHub Contributors Scraper

## Overview

The Generic GitHub Contributors Scraper is a web scraping-based solution that extracts contributor information from any GitHub repository without relying on the GitHub API. It uses multiple extraction strategies to ensure maximum coverage of contributors across different types of contributions.

## Features

### ✅ Generic and Scalable
- Works with **any** GitHub repository
- No API authentication required
- No rate limiting concerns
- Pure web scraping approach

### ✅ Multiple Extraction Strategies
The scraper uses 5 complementary strategies to capture contributors from different sources:

1. **Main Repository Page Sidebar**
   - Extracts prominent contributors shown on the main page
   - Uses `data-hovercard-type="user"` attributes
   - Captures quick access contributor links

2. **Contributors Graph Page**
   - Scrapes the dedicated contributors visualization page
   - Extracts contributor links and names
   - Handles dynamically rendered content

3. **Commit History** (Most Reliable)
   - Parses the commits page to find all committers
   - Extracts author information from commit history
   - Most comprehensive source of actual code contributors

4. **Pull Request History**
   - Identifies contributors who submitted pull requests
   - Captures PR authors even if PRs weren't merged
   - Includes community contributors

5. **Issues Page**
   - Finds contributors who opened or commented on issues
   - Captures non-code contributors
   - Includes bug reporters and feature requesters

### ✅ Deduplication
- Automatically merges duplicate entries from multiple sources
- Uses username-based deduplication (case-insensitive)
- Preserves the most complete information for each contributor

### ✅ Profile Enrichment
- Fetches full GitHub profiles for each contributor
- Extracts additional information:
  - Full name
  - Bio/description
  - Email (if public)
  - Company/organization
  - Location

## Architecture

### GitHubContributorsScraper Class

```python
from src.github_contributors_scraper import GitHubContributorsScraper

scraper = GitHubContributorsScraper(timeout=10)
contributors = scraper.scrape_contributors(owner="sodascience", repo_name="artscraper")
```

#### Methods

**`scrape_contributors(owner, repo_name) -> List[Dict]`**
- Main entry point for contributor extraction
- Combines all 5 strategies
- Returns list of contributor dictionaries

**`_scrape_main_page(owner, repo_name) -> List[Dict]`**
- Extracts contributors from main repository page
- Looks for user hover cards and links

**`_scrape_contributors_graph(owner, repo_name) -> List[Dict]`**
- Parses the contributors graph page
- Handles both link-based and data attribute-based extraction

**`_scrape_commit_history(owner, repo_name) -> List[Dict]`**
- Extracts committers from the commits page
- Most reliable source of actual contributors

**`_scrape_pull_requests(owner, repo_name) -> List[Dict]`**
- Identifies PR authors and reviewers
- Captures external contributors

**`_scrape_issues(owner, repo_name) -> List[Dict]`**
- Finds issue creators and commenters
- Includes community engagement contributors

**`scrape_user_profile(username) -> Optional[Dict]`**
- Fetches detailed profile information
- Extracts name, bio, email, company, location

## Data Structure

Each contributor is returned as a dictionary:

```python
{
    'username': 'jgarciab',           # GitHub username
    'name': 'Javier Garcia-Bernardo', # Full name or display name
    'url': 'https://github.com/jgarciab',  # GitHub profile URL
    'source': 'commit_history',       # Where it was found
    'email': 'user@example.com',      # If public (optional)
    'company': 'Organization Name',   # If available (optional)
    'location': 'City, Country',      # If available (optional)
    'bio': 'User bio text'            # If available (optional)
}
```

## Integration with Codemeta Generator

The scraper is integrated into the main `GitHubScraper` class and automatically used when generating Codemeta metadata:

```python
from src.generator import CodemetaGenerator

generator = CodemetaGenerator()
codemeta = generator.generate("https://github.com/sodascience/artscraper")

# Contributors are automatically extracted and included
if 'contributor' in codemeta:
    for contributor in codemeta['contributor']:
        print(f"{contributor['name']} ({contributor['email']})")
```

## Example: artscraper Repository

For the repository `https://github.com/sodascience/artscraper`, the scraper extracts:

```
1. sodascience (organization account)
   - Source: Issues page
   - URL: https://github.com/sodascience

2. jgarciab (Javier Garcia-Bernardo)
   - Source: Commit history
   - URL: https://github.com/jgarciab
   - Affiliation: Utrecht University

3. modhurita (Modhurita Mitra)
   - Source: Commit history
   - URL: https://github.com/modhurita
   - Affiliation: Utrecht University

4. qubixes
   - Source: Commit history
   - URL: https://github.com/qubixes
```

## Advantages Over API-Based Approach

| Aspect | API | Web Scraping |
|--------|-----|--------------|
| **Authentication** | Required | Not required |
| **Rate Limiting** | Yes (60-5000 req/hr) | No |
| **Setup** | Token needed | Works out of the box |
| **Reliability** | Dependent on API availability | Resilient to API changes |
| **Scope** | Limited to API endpoints | Can access any public page |
| **Cost** | Free tier limited | Unlimited |

## Performance Considerations

- **Timeout**: Default 10 seconds per request
- **Requests per repository**: 5-8 HTTP requests (one per strategy + profile enrichment)
- **Caching**: Implement caching for repeated lookups
- **Rate limiting**: Respectful delays between requests
- **Concurrency**: Can be parallelized for multiple repositories

## Error Handling

The scraper gracefully handles errors:

- Network timeouts → Returns empty list
- Invalid HTML → Continues with other strategies
- Missing pages → Skips that strategy
- Profile fetch failures → Uses scraped data without profile

## Limitations

1. **Dynamic Content**: Pages rendered entirely with JavaScript may not be fully scraped
2. **Private Repositories**: Only works with public repositories
3. **Archived Repositories**: May have limited contributor information
4. **Rate Limiting**: GitHub may rate limit excessive scraping
5. **HTML Changes**: Updates to GitHub's HTML structure may require adjustments

## Future Improvements

1. **JavaScript Rendering**: Use Selenium or Playwright for dynamic content
2. **Caching Layer**: Implement Redis or file-based caching
3. **Parallel Scraping**: Concurrent requests for multiple repositories
4. **Contributor Roles**: Detect maintainers, reviewers, etc.
5. **Contribution Metrics**: Extract contribution counts and activity levels
6. **Social Profiles**: Link to ORCID, personal websites, etc.

## Testing

Test the scraper with various repositories:

```bash
python3 test_contributors_improved.py
```

This will test:
- Direct scraper functionality
- Integration with Codemeta generator
- Profile enrichment
- Deduplication

## License

Part of the SSHOC NL Codemeta Generator project. See LICENSE file for details.
