"""Codemeta generator package."""

import sys
import subprocess


def _ensure_dependencies():
    """
    Automatically install missing dependencies on package import.
    
    This runs before any other imports to ensure all dependencies are available.
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
_ensure_dependencies()

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
