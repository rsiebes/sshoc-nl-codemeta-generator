"""
Issue Tracker property module for Codemeta 3.1 generator.

This module extracts the issue tracker URL from GitHub repositories.
"""

from typing import Dict, Optional
from src.base_metadata import BaseMetadata


class IssueTrackerMetadata(BaseMetadata):
    """Extract issue tracker URL from repository metadata."""
    
    PROPERTY_NAME = "issueTracker"
    SCHEMA_ORG_TYPE = "URL"
    
    def __init__(self, raw_data: Dict):
        """Initialize the IssueTrackerMetadata extractor.
        
        Args:
            raw_data: Raw repository metadata from scraper
        """
        super().__init__(raw_data)
    
    def extract(self) -> Dict:
        """
        Extract issue tracker URL from repository metadata.
        
        Returns:
            Dictionary with issueTracker URL or empty dict
        """
        issue_tracker_url = None
        
        # Try multiple sources in order of preference
        # 1. Direct 'issueTracker' field
        issue_tracker = self._get_value('issueTracker')
        if issue_tracker:
            issue_tracker_url = issue_tracker
        
        # 2. Construct from codeRepository URL (GitHub)
        elif self._get_value('codeRepository'):
            repo_url = self._get_value('codeRepository')
            if 'github.com' in repo_url:
                # Remove trailing slash and .git if present
                repo_url = repo_url.rstrip('/').replace('.git', '')
                issue_tracker_url = f"{repo_url}/issues"
        
        # 3. Construct from url field (GitHub)
        elif self._get_value('url'):
            repo_url = self._get_value('url')
            if 'github.com' in repo_url:
                repo_url = repo_url.rstrip('/').replace('.git', '')
                issue_tracker_url = f"{repo_url}/issues"
        
        # Store in metadata
        if issue_tracker_url:
            self.metadata[self.PROPERTY_NAME] = issue_tracker_url
        
        return self.metadata
    
    def _validate_metadata(self) -> None:
        """
        Validate the extracted issue tracker URL.
        
        Raises:
            ValueError: If issue tracker URL is invalid
        """
        if self.PROPERTY_NAME not in self.metadata:
            return
        
        issue_tracker = self.metadata[self.PROPERTY_NAME]
        
        # Check if it's a valid URL
        if not isinstance(issue_tracker, str):
            raise ValueError(f"Issue tracker must be a string, got {type(issue_tracker)}")
        
        if not issue_tracker.startswith(('http://', 'https://')):
            raise ValueError(f"Issue tracker must be a valid URL starting with http:// or https://")
        
        # Warn if it doesn't look like a typical issue tracker URL
        if not any(keyword in issue_tracker.lower() for keyword in ['issue', 'bug', 'tracker', 'jira', 'gitlab', 'github']):
            self.warnings.append(f"Issue tracker URL may not be valid: {issue_tracker}")
