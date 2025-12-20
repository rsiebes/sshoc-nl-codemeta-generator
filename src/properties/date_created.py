"""
DateCreated Property Module

Handles extraction and validation of the 'dateCreated' Codemeta property.
The dateCreated specifies when the software was created (first commit date).
"""

from datetime import datetime
from typing import Dict, Any, Optional
from src.base_metadata import BaseMetadata
from src.execution_profiler import profile


class DateCreatedMetadata(BaseMetadata):
    """Handles dateCreated metadata extraction and validation."""

    CODEMETA_PROPERTY = 'dateCreated'
    CODEMETA_TYPE = 'Date'
    REQUIRED = False

    def extract(self) -> Dict[str, Any]:
        """
        Extract dateCreated from raw data.

        Priority:
        1. date_created field (from scraper)
        2. created_at field
        3. creation_date field
        4. createdAt field

        Returns:
            Dictionary with 'dateCreated' key containing ISO 8601 date string
        """
        # Try different sources for the creation date
        date_value = self._get_value('date_created')
        
        if not date_value:
            date_value = self._get_value('created_at')
        
        if not date_value:
            date_value = self._get_value('creation_date')
        
        if not date_value:
            date_value = self._get_value('createdAt')

        if not date_value:
            self.add_warning("Repository creation date could not be extracted")
            return {}

        # Process and normalize the date
        processed_date = self._process_date(date_value)
        
        if not processed_date:
            self.add_warning(f"Could not process date value: {date_value}")
            return {}

        self.metadata['dateCreated'] = processed_date
        return self.metadata

    def _process_date(self, date_value: Any) -> Optional[str]:
        """
        Process and normalize date value to ISO 8601 format.

        Args:
            date_value: Date value in various formats

        Returns:
            ISO 8601 formatted date string or None
        """
        if not date_value:
            return None

        # If already a string in ISO format, validate and return
        if isinstance(date_value, str):
            # Try to parse and reformat
            try:
                # Handle various date formats
                dt = None

                # Try ISO 8601 format first
                try:
                    dt = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                except:
                    pass

                # Try common formats
                if not dt:
                    formats = [
                        '%Y-%m-%dT%H:%M:%S.%fZ',
                        '%Y-%m-%dT%H:%M:%SZ',
                        '%Y-%m-%d %H:%M:%S',
                        '%Y-%m-%d',
                        '%Y/%m/%d',
                        '%d-%m-%Y',
                        '%d/%m/%Y',
                    ]

                    for fmt in formats:
                        try:
                            dt = datetime.strptime(date_value, fmt)
                            break
                        except:
                            continue

                if dt:
                    # Return in ISO 8601 format
                    return dt.isoformat()

            except Exception as e:
                self.add_warning(f"Could not parse date '{date_value}': {e}")
                return None

        # If datetime object
        elif isinstance(date_value, datetime):
            return date_value.isoformat()

        return None

    def _validate_metadata(self) -> None:
        """Validate the extracted dateCreated metadata."""
        if not self.metadata.get('dateCreated'):
            return

        date_value = self.metadata['dateCreated']

        # Type check
        if not isinstance(date_value, str):
            self.add_error(f"dateCreated must be a string, got {type(date_value).__name__}")
            return

        # Try to parse the date to ensure it's valid
        try:
            dt = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            
            # Check if date is not in the future
            # Make datetime.now() timezone-aware for comparison
            from datetime import timezone
            now = datetime.now(timezone.utc)
            # Remove timezone info for comparison if dt has it
            if dt.tzinfo is not None:
                dt_naive = dt.replace(tzinfo=None)
                now_naive = now.replace(tzinfo=None)
                if dt_naive > now_naive:
                    self.add_warning("Creation date is in the future")
            else:
                if dt > datetime.now():
                    self.add_warning("Creation date is in the future")
                
        except Exception as e:
            self.add_error(f"Invalid date format: {e}")

    def to_codemeta_dict(self) -> Dict[str, Any]:
        """
        Convert to Codemeta format.

        Returns:
            Dictionary with dateCreated in Codemeta format
        """
        if not self.metadata.get('dateCreated'):
            return {}

        return {
            self.CODEMETA_PROPERTY: self.metadata['dateCreated']
        }
