#!/usr/bin/env python3
"""
CodeMeta Command-Line Interface (CLI)

A comprehensive command-line tool for generating CodeMeta 3.1 metadata files
from GitHub repositories.

Usage:
    codemeta-cli <repository_url> [options]
    codemeta-cli --help
    codemeta-cli --version

Examples:
    # Generate and print CodeMeta to stdout
    codemeta-cli https://github.com/tensorflow/tensorflow

    # Save CodeMeta to a file
    codemeta-cli https://github.com/tensorflow/tensorflow -o codemeta.jsonld

    # Pretty-print the output
    codemeta-cli https://github.com/tensorflow/tensorflow --pretty

    # Verbose output with progress information
    codemeta-cli https://github.com/tensorflow/tensorflow -v

    # Specify GitHub token for higher API rate limits
    codemeta-cli https://github.com/tensorflow/tensorflow --token ghp_xxxxx

    # Validate the generated CodeMeta against the schema
    codemeta-cli https://github.com/tensorflow/tensorflow --validate
"""

import sys
import argparse
import json
import os
from pathlib import Path
from typing import Optional

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.codemeta_generator import generate
from src.schema_validator import validate_metadata
from src.utils import normalize_url


# Create __main__ block for module execution
if __name__ == "__main__":
    pass


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for the CLI.

    Returns:
        argparse.ArgumentParser: The configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="codemeta-cli",
        description="Generate CodeMeta 3.1 metadata files from GitHub repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate and print CodeMeta to stdout
  codemeta-cli https://github.com/tensorflow/tensorflow

  # Save CodeMeta to a file
  codemeta-cli https://github.com/tensorflow/tensorflow -o codemeta.jsonld

  # Pretty-print the output
  codemeta-cli https://github.com/tensorflow/tensorflow --pretty

  # Verbose output with progress information
  codemeta-cli https://github.com/tensorflow/tensorflow -v

  # Specify GitHub token for higher API rate limits
  codemeta-cli https://github.com/tensorflow/tensorflow --token ghp_xxxxx

  # Validate the generated CodeMeta against the schema
  codemeta-cli https://github.com/tensorflow/tensorflow --validate

For more information, visit: https://github.com/rsiebes/sshoc-nl-codemeta-generator
        """,
    )

    # Positional arguments
    parser.add_argument(
        "repository",
        metavar="REPOSITORY",
        help="GitHub repository URL (e.g., https://github.com/owner/repo)",
    )

    # Optional arguments
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="Output file path (default: stdout)",
    )

    parser.add_argument(
        "-p",
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON output with indentation",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output with progress information",
    )

    parser.add_argument(
        "--token",
        metavar="TOKEN",
        help="GitHub personal access token for higher API rate limits",
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate the generated CodeMeta against the CodeMeta 3.1 schema",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
        help="Show version information",
    )

    return parser


def print_header():
    """Print the CLI header with version and information."""
    print("=" * 80)
    print("CodeMeta 3.1 Generator - Command Line Interface")
    print("=" * 80)


def print_progress(message: str, verbose: bool = False):
    """
    Print a progress message if verbose mode is enabled.

    Args:
        message (str): The message to print.
        verbose (bool): Whether verbose mode is enabled.
    """
    if verbose:
        print(f"[INFO] {message}")


def print_success(message: str):
    """
    Print a success message.

    Args:
        message (str): The message to print.
    """
    print(f"✓ {message}")


def print_error(message: str):
    """
    Print an error message and exit.

    Args:
        message (str): The error message to print.
    """
    print(f"✗ Error: {message}", file=sys.stderr)
    sys.exit(1)


def print_warning(message: str):
    """
    Print a warning message.

    Args:
        message (str): The warning message to print.
    """
    print(f"⚠ Warning: {message}", file=sys.stderr)


def validate_repository_url(url: str) -> str:
    """
    Validate and normalize a GitHub repository URL.

    Args:
        url (str): The repository URL to validate.

    Returns:
        str: The normalized repository URL.

    Raises:
        ValueError: If the URL is not a valid GitHub repository URL.
    """
    try:
        normalized = normalize_url(url)
        if not normalized or "github.com" not in normalized:
            raise ValueError("Not a valid GitHub repository URL")
        return normalized
    except Exception as e:
        raise ValueError(f"Invalid repository URL: {str(e)}")


def format_output(data: dict, pretty: bool = False) -> str:
    """
    Format the CodeMeta data as JSON.

    Args:
        data (dict): The CodeMeta data to format.
        pretty (bool): Whether to pretty-print the output.

    Returns:
        str: The formatted JSON string.
    """
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    else:
        return json.dumps(data, ensure_ascii=False)


def save_to_file(content: str, filepath: str):
    """
    Save the CodeMeta content to a file.

    Args:
        content (str): The content to save.
        filepath (str): The path to the output file.

    Raises:
        IOError: If the file cannot be written.
    """
    try:
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print_success(f"CodeMeta saved to {filepath}")
    except IOError as e:
        print_error(f"Failed to write output file: {str(e)}")


def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # Print header
    print_header()
    print()

    # Validate repository URL
    try:
        repository_url = validate_repository_url(args.repository)
        print_progress(f"Repository URL: {repository_url}", args.verbose)
    except ValueError as e:
        print_error(str(e))

    # Set GitHub token if provided
    if args.token:
        os.environ["GITHUB_TOKEN"] = args.token
        print_progress("GitHub token set for authentication", args.verbose)

    # Generate CodeMeta
    print_progress("Generating CodeMeta metadata...", args.verbose)
    try:
        codemeta = generate(repository_url, verbose=args.verbose)
        print_success("CodeMeta generated successfully")
    except Exception as e:
        print_error(f"Failed to generate CodeMeta: {str(e)}")

    # Validate if requested
    if args.validate:
        print_progress("Validating CodeMeta against schema...", args.verbose)
        is_valid, errors = validate_metadata(codemeta)
        if is_valid:
            print_success("CodeMeta is valid according to the CodeMeta 3.1 schema")
        else:
            print_warning("CodeMeta validation errors:")
            for error in errors:
                print(f"  - {error}")

    # Format output
    output_content = format_output(codemeta, args.pretty)

    # Save or print
    if args.output:
        save_to_file(output_content, args.output)
    else:
        print()
        print("=" * 80)
        print("Generated CodeMeta:")
        print("=" * 80)
        print(output_content)

    print()
    print("=" * 80)
    print("✓ CodeMeta generation completed successfully")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
