#!/usr/bin/env python3
"""
Common utility functions for CodeMeta generation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import re

def camel_to_snake(name: str) -> str:
    """
    Convert camelCase to snake_case.

    Args:
        name (str): The camelCase string.

    Returns:
        str: The snake_case string.
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def snake_to_camel(name: str) -> str:
    """
    Convert snake_case to camelCase.

    Args:
        name (str): The snake_case string.

    Returns:
        str: The camelCase string.
    """
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def is_url(value: str) -> bool:
    """
    Check if a string is a valid URL.

    Args:
        value (str): The string to check.

    Returns:
        bool: True if the string is a valid URL, False otherwise.
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(value) is not None

def is_email(value: str) -> bool:
    """
    Check if a string is a valid email address.

    Args:
        value (str): The string to check.

    Returns:
        bool: True if the string is a valid email, False otherwise.
    """
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return email_pattern.match(value) is not None

def is_date(value: str) -> bool:
    """
    Check if a string is a valid date in ISO 8601 format (YYYY-MM-DD).

    Args:
        value (str): The string to check.

    Returns:
        bool: True if the string is a valid date, False otherwise.
    """
    try:
        datetime.strptime(value, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def ensure_list(value: Any) -> List[Any]:
    """
    Ensure a value is a list. If it's not, wrap it in a list.

    Args:
        value (Any): The value to ensure is a list.

    Returns:
        List[Any]: The value as a list.
    """
    if isinstance(value, list):
        return value
    else:
        return [value]

def merge_dicts(*dicts: Dict) -> Dict:
    """
    Merge multiple dictionaries into one.

    Args:
        *dicts: Variable number of dictionaries to merge.

    Returns:
        Dict: The merged dictionary.
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result

def filter_empty_values(data: Dict) -> Dict:
    """
    Remove empty values from a dictionary.

    Args:
        data (Dict): The dictionary to filter.

    Returns:
        Dict: The filtered dictionary.
    """
    return {k: v for k, v in data.items() if v not in [None, "", [], {}]}

def get_nested_value(data: Dict, path: str, default: Any = None) -> Any:
    """
    Get a value from a nested dictionary using dot notation.

    Args:
        data (Dict): The dictionary to search.
        path (str): The path to the value (e.g., 'owner.login').
        default (Any): The default value if the path is not found.

    Returns:
        Any: The value at the path or the default value.
    """
    keys = path.split('.')
    value = data
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default
    return value if value is not None else default

def format_date(date_obj: Union[str, datetime]) -> Optional[str]:
    """
    Format a date object to ISO 8601 format (YYYY-MM-DD).

    Args:
        date_obj (Union[str, datetime]): The date object to format.

    Returns:
        Optional[str]: The formatted date or None if invalid.
    """
    if isinstance(date_obj, str):
        if is_date(date_obj):
            return date_obj
        try:
            # Try to parse and reformat
            parsed = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
            return parsed.strftime('%Y-%m-%d')
        except (ValueError, AttributeError):
            return None
    elif isinstance(date_obj, datetime):
        return date_obj.strftime('%Y-%m-%d')
    return None

def normalize_url(url: str) -> str:
    """
    Normalize a URL by removing trailing slashes and standardizing the format.

    Args:
        url (str): The URL to normalize.

    Returns:
        str: The normalized URL.
    """
    return url.rstrip('/') if url else url

def extract_github_username(github_url: str) -> Optional[str]:
    """
    Extract the GitHub username from a GitHub profile URL.

    Args:
        github_url (str): The GitHub profile URL.

    Returns:
        Optional[str]: The GitHub username or None if invalid.
    """
    match = re.match(r'https://github\.com/([a-zA-Z0-9-]+)/?$', github_url)
    return match.group(1) if match else None

def extract_doi(text: str) -> Optional[str]:
    """
    Extract a DOI from text.

    Args:
        text (str): The text to search.

    Returns:
        Optional[str]: The DOI or None if not found.
    """
    # DOI pattern: 10.xxxx/xxxxx
    match = re.search(r'10\.\d{4,}/\S+', text)
    return match.group(0) if match else None

def extract_orcid(text: str) -> Optional[str]:
    """
    Extract an ORCID from text.

    Args:
        text (str): The text to search.

    Returns:
        Optional[str]: The ORCID or None if not found.
    """
    # ORCID pattern: XXXX-XXXX-XXXX-XXXX
    match = re.search(r'\d{4}-\d{4}-\d{4}-\d{3}[0-9X]', text)
    return match.group(0) if match else None
