"""
DevelopmentStatus property extractor for CodeMeta.
Extracts or infers the development status of the software.
"""

from typing import Dict, Optional
from datetime import datetime, timezone
import re
from ..base_metadata import BaseMetadata


class DevelopmentStatusMetadata(BaseMetadata):
    """Extract developmentStatus metadata."""
    
    PROPERTY_NAME = "developmentStatus"
    SCHEMA_ORG_TYPE = "URL"
    
    # Repostatus.org base URL
    REPOSTATUS_BASE = "https://www.repostatus.org/#"
    
    # Valid status values
    VALID_STATUSES = [
        "active", "inactive", "wip", "concept",
        "suspended", "abandoned", "unsupported", "moved"
    ]
    
    def __init__(self, raw_data: Dict):
        super().__init__(raw_data)
    
    def extract(self) -> Dict:
        """Extract or infer developmentStatus."""
        # 1. Check for explicit developmentStatus field
        dev_status = self._get_value('development_status')
        if dev_status:
            status = self._normalize_status(dev_status)
            if status:
                self.metadata['developmentStatus'] = f"{self.REPOSTATUS_BASE}{status}"
                return self.metadata
        
        # 2. Check for repostatus badge in README
        readme_content = self._get_value('readme_content')
        if readme_content:
            badge_status = self._extract_badge_status(readme_content)
            if badge_status:
                self.metadata['developmentStatus'] = f"{self.REPOSTATUS_BASE}{badge_status}"
                return self.metadata
        
        # 3. Infer from repository activity
        inferred_status = self._infer_status()
        if inferred_status:
            self.metadata['developmentStatus'] = f"{self.REPOSTATUS_BASE}{inferred_status}"
            # Add note about inference
            self.add_warning(
                f"Development status inferred as '{inferred_status}' based on repository activity"
            )
            return self.metadata
        
        return self.metadata
    
    def _extract_badge_status(self, readme: str) -> Optional[str]:
        """
        Extract status from repostatus.org badge in README.
        
        Args:
            readme: README content
            
        Returns:
            Status string or None
        """
        # Pattern 1: Badge URL
        pattern1 = r'repostatus\.org/badges/latest/(\w+)\.svg'
        match = re.search(pattern1, readme, re.IGNORECASE)
        if match:
            status = match.group(1).lower()
            if status in self.VALID_STATUSES:
                return status
        
        # Pattern 2: Direct link
        pattern2 = r'repostatus\.org/#(\w+)'
        match = re.search(pattern2, readme, re.IGNORECASE)
        if match:
            status = match.group(1).lower()
            if status in self.VALID_STATUSES:
                return status
        
        # Pattern 3: Badge alt text
        pattern3 = r'Project Status:\s*(\w+)'
        match = re.search(pattern3, readme, re.IGNORECASE)
        if match:
            status = match.group(1).lower()
            if status in self.VALID_STATUSES:
                return status
        
        return None
    
    def _infer_status(self) -> Optional[str]:
        """
        Infer development status from repository activity.
        
        Returns:
            Inferred status string or None
        """
        # Get required data
        date_modified = self._get_value('date_modified')
        if not date_modified:
            return None
        
        version = self._get_value('version')
        releases = self._get_value('releases') or []
        
        # Calculate days since last commit
        try:
            days_since_last_commit = self._days_since_date(date_modified)
        except Exception:
            return None
        
        # Check if version indicates stable software
        is_stable = self._is_stable_version(version) if version else False
        has_releases = len(releases) > 0
        
        # Apply inference rules
        if days_since_last_commit <= 90:  # Active within 3 months
            if is_stable and has_releases:
                return "active"
            else:
                return "wip"
        
        elif days_since_last_commit <= 365:  # 3-12 months
            if is_stable:
                return "inactive"
            else:
                return "wip"  # Might still resume
        
        else:  # > 12 months
            if is_stable:
                return "unsupported"
            elif has_releases:
                return "abandoned"
            else:
                return "concept"  # Never progressed far
    
    def _days_since_date(self, date_str: str) -> int:
        """
        Calculate days since a given date.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Number of days since the date
        """
        # Try to parse the date
        date_formats = [
            '%Y-%m-%dT%H:%M:%S.%f%z',  # With milliseconds and timezone
            '%Y-%m-%dT%H:%M:%S.%fZ',    # With milliseconds and Z
            '%Y-%m-%dT%H:%M:%S%z',      # Without milliseconds
            '%Y-%m-%dT%H:%M:%SZ',        # Without milliseconds, Z
            '%Y-%m-%d',                  # Date only
        ]
        
        last_date = None
        for fmt in date_formats:
            try:
                # Handle 'Z' timezone
                date_to_parse = date_str.replace('Z', '+00:00') if 'Z' in date_str else date_str
                last_date = datetime.strptime(date_to_parse, fmt)
                break
            except ValueError:
                continue
        
        if not last_date:
            raise ValueError(f"Could not parse date: {date_str}")
        
        # Make timezone-aware if not already
        if last_date.tzinfo is None:
            last_date = last_date.replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        return (now - last_date).days
    
    def _is_stable_version(self, version: str) -> bool:
        """
        Check if version indicates stable software (>= 1.0.0).
        
        Args:
            version: Version string
            
        Returns:
            True if stable, False otherwise
        """
        # Remove v/V prefix
        version = version.lstrip('vV')
        
        # Extract major version
        match = re.match(r'^(\d+)', version)
        if match:
            major = int(match.group(1))
            return major >= 1
        
        return False
    
    def _normalize_status(self, status: str) -> Optional[str]:
        """
        Normalize status string to valid repostatus value.
        
        Args:
            status: Status string
            
        Returns:
            Normalized status or None
        """
        # Extract status from URL if provided
        if 'repostatus.org' in status:
            match = re.search(r'#(\w+)', status)
            if match:
                status = match.group(1)
        
        status = status.lower().strip()
        
        # Map common variations
        status_map = {
            'active': 'active',
            'inactive': 'inactive',
            'wip': 'wip',
            'work-in-progress': 'wip',
            'concept': 'concept',
            'suspended': 'suspended',
            'abandoned': 'abandoned',
            'unsupported': 'unsupported',
            'moved': 'moved',
        }
        
        return status_map.get(status)
    
    def _validate_metadata(self) -> None:
        """Validate developmentStatus metadata."""
        if not self.metadata or 'developmentStatus' not in self.metadata:
            return
        
        status_url = self.metadata['developmentStatus']
        
        # Validate URL format
        if not isinstance(status_url, str):
            self.add_warning(f"developmentStatus must be a string, got {type(status_url).__name__}")
            return
        
        if not status_url.startswith(self.REPOSTATUS_BASE):
            self.add_warning(f"developmentStatus should use repostatus.org URL format: {status_url}")
            return
        
        # Extract and validate status
        status = status_url.replace(self.REPOSTATUS_BASE, '')
        if status not in self.VALID_STATUSES:
            self.add_warning(f"Invalid development status: {status}")
