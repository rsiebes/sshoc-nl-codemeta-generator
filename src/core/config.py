"""Configuration and CLI argument parsing for the Codemeta generator."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .errors import ConfigError
from .logger import get_logger

logger = get_logger(__name__)


class Config:
    """Configuration class for the Codemeta generator."""

    def __init__(
        self,
        repo_url: str,
        output_path: Optional[str] = None,
        verbose: bool = False,
        use_cache: bool = False,
        cache_ttl: int = 3600,
        wait_on_rate_limit: bool = True
    ):
        """
        Initialize configuration.

        Args:
            repo_url: GitHub repository URL
            output_path: Path where to save the codemeta.jsonld file (default: repository root)
            verbose: Enable verbose logging
            use_cache: Enable caching of API responses (default: False)
            cache_ttl: Cache time-to-live in seconds (default: 3600)
            wait_on_rate_limit: Wait when rate limit is hit instead of failing (default: True)

        Raises:
            ConfigError: If configuration is invalid
        """
        self.repo_url = repo_url
        self.verbose = verbose
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        self.wait_on_rate_limit = wait_on_rate_limit

        # Set output path
        if output_path:
            self.output_path = Path(output_path)
        else:
            # Default to codemeta.jsonld in current directory
            self.output_path = Path("codemeta.jsonld")

        # Validate configuration
        self._validate()

    def _validate(self) -> None:
        """Validate configuration."""
        if not self.repo_url:
            raise ConfigError("Repository URL is required")

        if not self.repo_url.startswith("https://github.com/"):
            raise ConfigError(
                f"Invalid GitHub URL: {self.repo_url}. "
                "URL must start with 'https://github.com/'"
            )

        if self.cache_ttl <= 0:
            raise ConfigError(
                f"Cache TTL must be positive, got: {self.cache_ttl}"
            )

    def __repr__(self) -> str:
        """String representation of configuration."""
        return (
            f"Config(repo_url={self.repo_url}, "
            f"output_path={self.output_path}, "
            f"verbose={self.verbose}, "
            f"use_cache={self.use_cache}, "
            f"cache_ttl={self.cache_ttl}, "
            f"wait_on_rate_limit={self.wait_on_rate_limit})"
        )


def parse_arguments(args: Optional[list] = None) -> Config:
    """
    Parse command-line arguments.

    Args:
        args: Command-line arguments (default: sys.argv[1:])

    Returns:
        Config object

    Raises:
        ConfigError: If arguments are invalid
    """
    parser = argparse.ArgumentParser(
        description="Generate Codemeta 3.1 metadata from a GitHub repository URL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main https://github.com/user/repo
  python -m src.main https://github.com/user/repo --output /path/to/codemeta.jsonld
  python -m src.main https://github.com/user/repo -v
        """
    )

    parser.add_argument(
        "repo_url",
        help="GitHub repository URL (e.g., https://github.com/user/repo)"
    )

    parser.add_argument(
        "-o", "--output",
        dest="output_path",
        default=None,
        help="Output path for codemeta.jsonld file (default: ./codemeta.jsonld)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "--use-cache",
        action="store_true",
        help="Enable caching of API responses (default: disabled)"
    )

    parser.add_argument(
        "--cache-ttl",
        type=int,
        default=3600,
        help="Cache time-to-live in seconds (default: 3600 = 1 hour)"
    )

    parser.add_argument(
        "--no-wait-on-rate-limit",
        dest="wait_on_rate_limit",
        action="store_false",
        default=True,
        help="Fail immediately when rate limit is hit instead of waiting"
    )

    try:
        parsed_args = parser.parse_args(args)
        config = Config(
            repo_url=parsed_args.repo_url,
            output_path=parsed_args.output_path,
            verbose=parsed_args.verbose,
            use_cache=parsed_args.use_cache,
            cache_ttl=parsed_args.cache_ttl,
            wait_on_rate_limit=parsed_args.wait_on_rate_limit
        )
        return config
    except ConfigError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
