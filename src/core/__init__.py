"""Core modules for the Codemeta generator."""

from .config import Config, parse_arguments
from .errors import (
    CodemetaError,
    ConfigError,
    GitHubAPIError,
    InvalidRepositoryError,
    RepositoryNotFoundError,
    CodemetaGenerationError,
    OutputError,
)
from .github_api import GitHubAPI
from .logger import setup_logger, get_logger

__all__ = [
    "Config",
    "parse_arguments",
    "CodemetaError",
    "ConfigError",
    "GitHubAPIError",
    "InvalidRepositoryError",
    "RepositoryNotFoundError",
    "CodemetaGenerationError",
    "OutputError",
    "GitHubAPI",
    "setup_logger",
    "get_logger",
]
