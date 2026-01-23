"""Command-line interface entry point for the Codemeta generator."""

import sys

from .core import (
    parse_arguments,
    setup_logger,
    get_logger,
    CodemetaError,
)
from .codemeta_generator import CodemetaGenerator

logger = get_logger(__name__)


def main(args=None):
    """
    Main entry point for the CLI.

    Args:
        args: Command-line arguments (default: sys.argv[1:])
    """
    try:
        # Parse command-line arguments
        config = parse_arguments(args)

        # Set up logging
        setup_logger("src", verbose=config.verbose)
        logger.debug(f"Configuration: {config}")

        # Create and run generator
        generator = CodemetaGenerator(config)
        codemeta = generator.generate()

        # Save to file
        generator.save_to_file(codemeta)

        logger.info("Codemeta generation completed successfully")
        return 0

    except CodemetaError as e:
        logger.error(f"Error: {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.debug(f"Exception details:", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
