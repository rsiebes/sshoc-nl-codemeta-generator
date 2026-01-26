#!/usr/bin/env python3
"""
Auto-install dependencies and run the keywords extraction test.

This script automatically installs all required dependencies before running the test.
No manual pip install needed - just run this script!
"""

import subprocess
import sys
import os


def install_dependencies():
    """Install required dependencies from requirements.txt."""
    print("=" * 80)
    print("Installing required dependencies...")
    print("=" * 80)

    try:
        # Try to install with pip
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"]
        )
        print("✓ Dependencies installed successfully!\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        print("Please run manually: pip install -r requirements.txt")
        return False


def check_env_file():
    """Check if .env file exists with API key."""
    if not os.path.exists(".env"):
        print("⚠ WARNING: .env file not found!")
        print("Please create a .env file with your Gemini API key:")
        print("  GOOGLE_GEMINI_API_KEY=your_api_key_here")
        print()
        return False

    with open(".env", "r") as f:
        content = f.read()
        if "your_api_key_here" in content or not content.strip():
            print("⚠ WARNING: .env file exists but API key is not set!")
            print("Please update .env with your actual Gemini API key")
            print()
            return False

    return True


def run_test():
    """Run the keywords extraction test."""
    print("=" * 80)
    print("Running Keywords Extraction Test")
    print("=" * 80)
    print()

    try:
        subprocess.check_call([sys.executable, "test_keywords.py"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Test failed: {e}")
        return False


def main():
    """Main entry point."""
    print("\n" + "=" * 80)
    print("SSHOC CodeMeta Generator - Keywords Extraction Setup")
    print("=" * 80 + "\n")

    # Step 1: Install dependencies
    if not install_dependencies():
        sys.exit(1)

    # Step 2: Check .env file
    if not check_env_file():
        print("Please set up your .env file and try again.")
        sys.exit(1)

    # Step 3: Run test
    print()
    if not run_test():
        sys.exit(1)

    print("\n" + "=" * 80)
    print("✓ All done!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
