"""
DatePublished property extractor for CodeMeta.
Extracts the date of first broadcast/publication of the software.
"""

from typing import Dict, Optional
from datetime import datetime
import re
from ..base_metadata import BaseMetadata


class DatePublishedMetadata(BaseMetadata):
    """Extract datePublished metadata."""
    
    PROPERTY_NAME = "datePublished"
    SCHEMA_ORG_TYPE = "Date"
    
    def __init__(self, raw_data: Dict):
        super().__init__(raw_data)
    
    def extract(self) -> Dict:
        """Extract datePublished from various sources."""
        # 1. Check for explicit datePublished field
        date_published = self._get_value('date_published')
        if date_published:
            formatted_date = self._format_date(date_published)
            if formatted_date:
                self.metadata['datePublished'] = formatted_date
                return self.metadata
        
        # 2. Get first release date from GitHub
        releases = self._get_value('releases')
        if releases and len(releases) > 0:
            # Releases are sorted newest first, so get the last one
            first_release = releases[-1]
            if first_release.get('date'):
                formatted_date = self._format_date(first_release['date'])
                if formatted_date:
                    self.metadata['datePublished'] = formatted_date
                    return self.metadata
        
        # 3. Check CITATION.cff for date-released
        # TODO: Add CITATION.cff parsing when scraper supports it
        
        # 4. Fallback: Use dateCreated if version indicates published software
        date_created = self._get_value('date_created')
        version = self._get_value('version')
        if date_created and version and self._is_stable_version(version):
            formatted_date = self._format_date(date_created)
            if formatted_date:
                self.metadata['datePublished'] = formatted_date
                return self.metadata
        
        return self.metadata
    
    def _format_date(self, date_value: str) -> Optional[str]:
        """
        Format date to ISO 8601 (YYYY-MM-DD).
        
        Args:
            date_value: Date string in various formats
            
        Returns:
            Formatted date string or None if invalid
        """
        if not date_value:
            return None
        
        # If already in YYYY-MM-DD format, validate and return
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_value):
            try:
                datetime.strptime(date_value, '%Y-%m-%d')
                return date_value
            except ValueError:
                return None
        
        # Try to parse various date formats
        date_formats = [
            '%Y-%m-%dT%H:%M:%SZ',  # ISO 8601 with time
            '%Y-%m-%dT%H:%M:%S',   # ISO 8601 with time (no Z)
            '%Y-%m-%d %H:%M:%S',   # Space-separated with time
            '%Y/%m/%d',            # Slash-separated
            '%d-%m-%Y',            # Day first
            '%m/%d/%Y',            # US format
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_value, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def _is_stable_version(self, version: str) -> bool:
        """
        Check if version indicates stable/published software.
        
        Args:
            version: Version string
            
        Returns:
            True if version >= 1.0.0, False otherwise
        """
        # Remove 'v' or 'V' prefix
        version = version.lstrip('vV')
        
        # Extract major version number
        match = re.match(r'^(\d+)', version)
        if match:
            major = int(match.group(1))
            return major >= 1
        
        return False
    
    def _validate_metadata(self) -> None:
        """Validate datePublished metadata."""
        if not self.metadata or 'datePublished' not in self.metadata:
            return
        
        date_value = self.metadata['datePublished']
        
        # Validate date format
        if not isinstance(date_value, str):
            self.add_warning(f"datePublished must be a string, got {type(date_value).__name__}")
            return
        
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_value):
            self.add_warning(f"datePublished should be in YYYY-MM-DD format: {date_value}")
            return
        
        # Parse the date
        try:
            date_published = datetime.strptime(date_value, '%Y-%m-%d')
        except ValueError:
            self.add_warning(f"datePublished is not a valid date: {date_value}")
            return
        
        # Check if date is not in the future
        if date_published > datetime.now():
            self.add_warning(f"datePublished is in the future: {date_value}")
        
        # Check if date is not before 1970 (reasonable lower bound)
        if date_published.year < 1970:
            self.add_warning(f"datePublished is before 1970: {date_value}")
        
        # Check if datePublished >= dateCreated
        date_created = self._get_value('date_created')
        if date_created:
            try:
                dt_created = datetime.strptime(date_created, '%Y-%m-%d')
                if date_published < dt_created:
                    self.add_warning(
                        f"datePublished ({date_value}) is before dateCreated ({date_created})"
                    )
            except ValueError:
                pass  # dateCreated format issue, skip validation
        
        # Check if datePublished == dateCreated (might indicate no releases)
        if date_created and date_value == date_created:
            # Only warn if there are no releases
            releases = self._get_value('releases')
            if not releases or len(releases) == 0:
                self.add_warning(
                    "datePublished equals dateCreated (no releases found, using repository creation date)"
                )
