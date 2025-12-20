#!/usr/bin/env python3
"""
Codemeta Generator CLI

Command-line tool to generate Codemeta 3.1 metadata from GitHub repositories.

Usage:
    python codemeta_gen.py <github_repo_url> [options]

Examples:
    python codemeta_gen.py https://github.com/owner/repo
    python codemeta_gen.py https://github.com/owner/repo -o codemeta.json
    python codemeta_gen.py https://github.com/owner/repo --output my_codemeta.json
"""

import argparse
import sys
import os
import subprocess

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_and_install_dependencies():
    """Check for and install missing dependencies."""
    required_packages = {
        'requests': 'requests>=2.28.0',
        'bs4': 'beautifulsoup4>=4.11.0',
        'playwright': 'playwright>=1.40.0',
        'lxml': 'lxml>=4.9.0',
        'nltk': 'nltk>=3.8.0',
        'sklearn': 'scikit-learn>=1.3.0'
    }
    
    missing_packages = []
    
    # Check which packages are missing
    for module_name, package_spec in required_packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_packages.append(package_spec)
    
    # Install missing packages
    if missing_packages:
        print("📦 Installing missing dependencies...")
        print(f"   Missing: {', '.join(missing_packages)}")
        print()
        
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', '--quiet'] + missing_packages,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            print("✅ Dependencies installed successfully")
            print()
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            print("   Please install manually: pip install -r requirements.txt")
            sys.exit(1)
    
    # Download NLTK data if needed
    try:
        import nltk
        
        # Check if NLTK data is available
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            print("📚 Downloading NLTK data...")
            
            import ssl
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                pass
            else:
                ssl._create_default_https_context = _create_unverified_https_context
            
            # Download required NLTK data quietly
            for dataset in ['stopwords', 'punkt', 'punkt_tab', 'averaged_perceptron_tagger', 'wordnet']:
                try:
                    nltk.download(dataset, quiet=True)
                except:
                    pass  # Some datasets might not be needed
            
            print("✅ NLTK data downloaded successfully")
            print()
    except Exception as e:
        print(f"⚠️  Warning: Could not download NLTK data: {e}")
        print()
    
    # Install Playwright browsers if needed
    try:
        import playwright
        
        print("🌐 Checking Playwright browsers...")
        
        # Check if browsers are installed by trying to launch
        try:
            import asyncio
            from playwright.async_api import async_playwright
            
            async def check_browsers():
                try:
                    async with async_playwright() as p:
                        browser = await p.chromium.launch(headless=True)
                        await browser.close()
                        return True
                except Exception:
                    return False
            
            browsers_installed = asyncio.run(check_browsers())
            
            if not browsers_installed:
                print("   Installing Playwright browsers (this may take a minute)...")
                try:
                    subprocess.check_call(
                        [sys.executable, '-m', 'playwright', 'install', 'chromium'],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.PIPE
                    )
                    print("✅ Playwright browsers installed successfully")
                    print()
                except subprocess.CalledProcessError as e:
                    print(f"⚠️  Warning: Could not install Playwright browsers: {e}")
                    print("   The scraper will fall back to HTTP requests without JavaScript rendering")
                    print()
            else:
                print("✅ Playwright browsers already installed")
                print()
        except Exception as e:
            print(f"⚠️  Warning: Could not check Playwright browsers: {e}")
            print()
    except ImportError:
        # Playwright not installed, will be installed by pip
        pass
    except Exception as e:
        print(f"⚠️  Warning: Could not setup Playwright: {e}")
        print()


from src.execution_profiler import get_profiler
from src.generator import CodemetaGenerator


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Generate Codemeta 3.1 metadata from GitHub repositories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://github.com/owner/repo
  %(prog)s https://github.com/owner/repo -o codemeta.json
  %(prog)s https://github.com/owner/repo --output my_codemeta.json

For more information, visit: https://codemeta.github.io/
        """
    )
    
    parser.add_argument(
        'repo_url',
        help='GitHub repository URL (e.g., https://github.com/owner/repo)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='codemeta.json',
        help='Output file path (default: codemeta.json)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0 (Codemeta 3.1)'
    )
    
    parser.add_argument(
        '--no-install',
        action='store_true',
        help='Skip automatic dependency installation'
    )
    
    args = parser.parse_args()
    
    # Check and install dependencies unless --no-install is specified
    if not args.no_install:
        check_and_install_dependencies()
    
    # Validate repository URL
    if not args.repo_url.startswith('http'):
        print(f"Error: Invalid repository URL: {args.repo_url}")
        print("URL must start with 'http://' or 'https://'")
        sys.exit(1)
    
    if 'github.com' not in args.repo_url:
        print(f"Error: Not a GitHub repository URL: {args.repo_url}")
        print("URL must contain 'github.com'")
        sys.exit(1)
    
    # Print header
    print("=" * 70)
    print("Codemeta 3.1 Generator")
    print("=" * 70)
    print()
    
    try:
        profiler = get_profiler(verbose=True)
        profiler.start()
        
        # Create generator
        generator = CodemetaGenerator()
        
        # Generate Codemeta
        generator.generate_to_file(args.repo_url, args.output)
        
        profiler.end_with_detailed_summary()
        
        print()
        print("=" * 70)
        print("✅ Generation completed successfully!")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
