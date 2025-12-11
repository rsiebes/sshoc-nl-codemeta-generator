# GitHub Token Setup Guide

## Overview

The CodeMeta generator uses the GitHub API to extract metadata from repositories. By default, unauthenticated requests are limited to **60 requests per hour**, which may be insufficient for processing multiple repositories or large projects.

To increase the rate limit and enable full metadata extraction, you should set up a GitHub personal access token.

## Why Use a GitHub Token?

- **Higher Rate Limit**: Authenticated requests allow up to **5,000 requests per hour** (vs. 60 for unauthenticated)
- **Better Reliability**: More stable API access, especially for popular repositories
- **Full Metadata Access**: Some endpoints require authentication for complete data access
- **No Rate Limiting Issues**: Avoid "rate limit exceeded" errors when processing multiple repositories

## Creating a GitHub Personal Access Token

### Step 1: Go to GitHub Settings

1. Log in to your GitHub account
2. Click your profile icon in the top-right corner
3. Select **Settings**

### Step 2: Create a New Token

1. In the left sidebar, click **Developer settings**
2. Click **Personal access tokens**
3. Click **Generate new token**

### Step 3: Configure Token Permissions

1. Give your token a descriptive name (e.g., "CodeMeta Generator")
2. Set an expiration date (or no expiration)
3. Select the following scopes:
   - ✓ `public_repo` - Access to public repositories
   - ✓ `read:user` - Read user profile data
   - ✓ `read:org` - Read organization data

### Step 4: Generate and Copy Token

1. Click **Generate token**
2. **Copy the token immediately** - you won't be able to see it again
3. Store it securely (e.g., in a password manager)

## Setting Up the Environment Variable

### Option 1: Export in Shell Session

```bash
export GITHUB_TOKEN="your_token_here"
```

Then run the CodeMeta generator:

```bash
python3 -c "from src.codemeta_generator import generate; generate('https://github.com/owner/repo')"
```

### Option 2: Set in .bashrc or .zshrc

Add to your shell configuration file:

```bash
export GITHUB_TOKEN="your_token_here"
```

Then reload your shell:

```bash
source ~/.bashrc  # or source ~/.zshrc
```

### Option 3: Create a .env File (Recommended for Development)

Create a `.env` file in the project root:

```
GITHUB_TOKEN=your_token_here
```

Then load it before running the generator:

```bash
set -a
source .env
set +a
python3 -c "from src.codemeta_generator import generate; generate('https://github.com/owner/repo')"
```

### Option 4: Set in Python Script

```python
import os
os.environ["GITHUB_TOKEN"] = "your_token_here"

from src.codemeta_generator import generate
result = generate("https://github.com/owner/repo")
```

## Verifying Your Token Setup

To verify that your GitHub token is properly configured:

```bash
export GITHUB_TOKEN="your_token_here"
python3 << 'EOF'
import os
from src.github_api import get_github_token
import requests

token = get_github_token()
if token:
    print("✓ GitHub token is set")
    
    # Check rate limit
    response = requests.get(
        "https://api.github.com/rate_limit",
        headers={"Authorization": f"token {token}"}
    )
    if response.status_code == 200:
        data = response.json()
        core_limit = data['resources']['core']
        print(f"✓ Rate limit: {core_limit['remaining']}/{core_limit['limit']} requests remaining")
    else:
        print("✗ Failed to check rate limit")
else:
    print("✗ GitHub token is not set")
EOF
```

## Security Best Practices

1. **Never commit tokens**: Add `.env` to `.gitignore`
2. **Use limited scopes**: Only grant necessary permissions
3. **Rotate tokens regularly**: Regenerate tokens periodically
4. **Monitor usage**: Check GitHub's token activity logs
5. **Revoke unused tokens**: Delete tokens you no longer need

## Troubleshooting

### "Rate limit exceeded" error

- Verify your token is set: `echo $GITHUB_TOKEN`
- Check token is valid: Run the verification script above
- Ensure token hasn't expired
- Wait for rate limit reset (usually 1 hour)

### "Bad credentials" error

- Token may be invalid or expired
- Regenerate a new token
- Ensure no extra spaces in token value

### Token not being recognized

- Verify environment variable name is exactly `GITHUB_TOKEN`
- Check token is exported: `export GITHUB_TOKEN="..."`
- Restart your shell session
- Try setting in Python script directly

## Token Scope Explanation

| Scope | Purpose | Required |
|-------|---------|----------|
| `public_repo` | Access public repositories | ✓ Yes |
| `read:user` | Read user profile information | ✓ Yes |
| `read:org` | Read organization information | ✓ Yes |
| `repo` | Full repository access | ✗ No (only public_repo needed) |
| `admin:repo_hook` | Manage webhooks | ✗ No |
| `admin:org_hook` | Manage organization webhooks | ✗ No |

## Rate Limits Comparison

| Type | Limit | Duration |
|------|-------|----------|
| Unauthenticated | 60 | 1 hour |
| Authenticated | 5,000 | 1 hour |
| GraphQL (authenticated) | 5,000 | 1 hour |

## Advanced: Using GitHub CLI Token

If you have GitHub CLI installed, you can use its token:

```bash
export GITHUB_TOKEN=$(gh auth token)
python3 -c "from src.codemeta_generator import generate; generate('https://github.com/owner/repo')"
```

## References

- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub API Rate Limiting](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)
- [GitHub API Authentication](https://docs.github.com/en/rest/overview/authenticating-to-the-rest-api)

