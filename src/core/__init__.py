"""Core modules for the Codemeta generator."""

from .cache import Cache
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
from .rate_limiter import RateLimiter

__all__ = [
    "Cache",
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
    "RateLimiter",
]
