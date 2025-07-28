"""
CodeMeta Generator - A comprehensive toolkit for generating and enhancing CodeMeta files

This package provides tools for creating standardized metadata for research software,
with support for CodeMeta 2.0 and 3.0 schemas.

Author: Ronald Siebes (UCDS Group, VU Amsterdam)
ORCID: 0000-0001-8772-7904
"""

__version__ = "1.0.0"
__author__ = "Ronald Siebes"
__email__ = "r.siebes@vu.nl"

from .codemeta_generator import CodeMetaGenerator, create_soda_science_organization, create_publication_reference
from .enhancer import CodeMetaEnhancer
from .bulk_processor import BulkProcessor

__all__ = [
    "CodeMetaGenerator",
    "CodeMetaEnhancer", 
    "BulkProcessor",
    "create_soda_science_organization",
    "create_publication_reference"
]

