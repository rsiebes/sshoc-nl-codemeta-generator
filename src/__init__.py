"""Codemeta generator package."""

__version__ = "0.1.0"
__author__ = "Codemeta Generator Contributors"

from .core import (
    Config,
    parse_arguments,
    setup_logger,
    get_logger,
)
from .codemeta_generator import CodemetaGenerator

__all__ = [
    "Config",
    "parse_arguments",
    "setup_logger",
    "get_logger",
    "CodemetaGenerator",
]
