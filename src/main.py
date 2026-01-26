"""Command-line interface entry point for the Codemeta generator."""

import sys
import subprocess


def ensure_dependencies():
    """
    Automatically install missing dependencies.
    
    This function checks for required packages and installs them if missing.
    It runs before any other imports to ensure all dependencies are available.
    """
    required_packages = [
        ("google.genai", "google-genai>=0.3.0"),
        ("pydantic", "pydantic>=2.0.0"),
        ("dotenv", "python-dotenv>=1.0.0"),
        ("requests", "requests>=2.28.0"),
        ("typing_extensions", "typing-extensions>=4.0.0"),
        ("anyio", "anyio>=3.0.0"),
        ("distro", "distro>=1.5.0"),
        ("google.auth", "google-auth>=2.0.0"),
        ("httpx", "httpx>=0.23.0"),
        ("sniffio", "sniffio>=1.2.0"),
        ("tenacity", "tenacity>=8.0.0"),
        ("websockets", "websockets>=10.0"),
    ]

    missing = []

    for import_name, package_spec in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_spec)

    if missing:
        print("Installing missing dependencies:", ", ".join(missing))
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q"] + missing
            )
            print("✓ Dependencies installed successfully!\n")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install dependencies: {e}")
            print("Please run manually: pip install -r requirements.txt")
            sys.exit(1)


# Ensure dependencies are installed before importing anything else
ensure_dependencies()

# Now import the rest of the modules
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
