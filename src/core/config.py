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
        verbose: bool = False
    ):
        """
        Initialize configuration.

        Args:
            repo_url: GitHub repository URL
            output_path: Path where to save the codemeta.jsonld file (default: repository root)
            verbose: Enable verbose logging

        Raises:
            ConfigError: If configuration is invalid
        """
        self.repo_url = repo_url
        self.verbose = verbose

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

    def __repr__(self) -> str:
        """String representation of configuration."""
        return (
            f"Config(repo_url={self.repo_url}, "
            f"output_path={self.output_path}, "
            f"verbose={self.verbose})"
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

    try:
        parsed_args = parser.parse_args(args)
        config = Config(
            repo_url=parsed_args.repo_url,
            output_path=parsed_args.output_path,
            verbose=parsed_args.verbose
        )
        return config
    except ConfigError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
