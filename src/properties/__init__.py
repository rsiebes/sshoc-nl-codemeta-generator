"""
Codemeta 3.1 Property Modules

This package contains individual modules for each Codemeta 3.1 property.
Each module handles extraction, validation, and conversion of a specific property.

Core properties are implemented first, followed by additional properties.
"""

# Import core property modules
from .name import NameMetadata
from .description import DescriptionMetadata
from .url import UrlMetadata
from .version import VersionMetadata
from .code_repository import CodeRepositoryMetadata

__all__ = [
    'NameMetadata',
    'DescriptionMetadata',
    'UrlMetadata',
    'VersionMetadata',
    'CodeRepositoryMetadata',
]
