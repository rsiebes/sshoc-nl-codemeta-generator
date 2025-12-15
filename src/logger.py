"""
Logging utility module for the Codemeta Generator.

Provides centralized logging configuration and utilities for the application.
"""

import logging
import sys
from typing import Optional


class CodemetaLogger:
    """Centralized logging configuration for Codemeta Generator."""

    _logger: Optional[logging.Logger] = None
    _initialized = False

    @classmethod
    def get_logger(cls, name: str = "codemeta_generator", verbose: bool = False) -> logging.Logger:
        """
        Get or create the logger instance.

        Args:
            name: Logger name
            verbose: Enable verbose logging (DEBUG level)

        Returns:
            Configured logger instance
        """
        if cls._logger is None:
            cls._logger = logging.getLogger(name)
            cls._setup_logger(cls._logger, verbose)
            cls._initialized = True

        return cls._logger

    @classmethod
    def _setup_logger(cls, logger: logging.Logger, verbose: bool = False) -> None:
        """
        Configure the logger with appropriate handlers and formatters.

        Args:
            logger: Logger instance to configure
            verbose: Enable verbose logging
        """
        # Set log level
        log_level = logging.DEBUG if verbose else logging.INFO
        logger.setLevel(log_level)

        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        # Create formatter
        if verbose:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            formatter = logging.Formatter('%(levelname)s: %(message)s')

        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    @classmethod
    def reset(cls) -> None:
        """Reset the logger instance."""
        cls._logger = None
        cls._initialized = False


def get_logger(name: str = "codemeta_generator", verbose: bool = False) -> logging.Logger:
    """
    Convenience function to get a logger instance.

    Args:
        name: Logger name
        verbose: Enable verbose logging

    Returns:
        Configured logger instance
    """
    return CodemetaLogger.get_logger(name, verbose)
