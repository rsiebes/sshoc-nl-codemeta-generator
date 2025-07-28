#!/usr/bin/env python3
"""
Command Line Interface for CodeMeta Generator

Provides command-line access to CodeMeta generation and enhancement functionality.

Author: Ronald Siebes (UCDS Group, VU Amsterdam)
ORCID: 0000-0001-8772-7904
"""

import argparse
import json
import os
import sys
from typing import List, Dict

from .codemeta_generator import CodeMetaGenerator, create_soda_science_organization
from .enhancer import CodeMetaEnhancer
from .bulk_processor import BulkProcessor


def generate_command(args):
    """Handle the generate command."""
    generator = CodeMetaGenerator(args.schema)
    
    try:
        print(f"Generating CodeMeta for: {args.repo}")
        codemeta = generator.generate_from_github(args.repo)
        
        # Add organizational context if specified
        if args.organization == "soda":
            soda_org = create_soda_science_organization()
            generator.add_organizational_context(codemeta, soda_org)
        
        # Save the file
        generator.save_codemeta(codemeta, args.output)
        
        # Validate
        warnings = generator.validate_codemeta(codemeta)
        if warnings:
            print("Validation warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        
        print(f"✅ CodeMeta file generated: {args.output}")
        
    except Exception as e:
        print(f"❌ Error generating CodeMeta: {e}")
        sys.exit(1)


def enhance_command(args):
    """Handle the enhance command."""
    enhancer = CodeMetaEnhancer(args.schema)
    
    try:
        print(f"Enhancing CodeMeta file: {args.input}")
        enhanced = enhancer.enhance_file(args.input, args.output)
        
        # Add organizational context if specified
        if args.organization == "soda":
            soda_org = create_soda_science_organization()
            enhancer.add_organizational_context(enhanced, soda_org)
            
            # Save again with organizational context
            output_file = args.output or args.input
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced, f, indent=2, ensure_ascii=False)
        
        # Validate enhancement
        messages = enhancer.validate_enhancement(enhanced)
        for message in messages:
            print(f"  {message}")
        
        output_file = args.output or args.input
        print(f"✅ CodeMeta file enhanced: {output_file}")
        
    except Exception as e:
        print(f"❌ Error enhancing CodeMeta: {e}")
        sys.exit(1)


def bulk_command(args):
    """Handle the bulk command."""
    processor = BulkProcessor(args.schema, args.workers)
    
    try:
        if args.repos_file:
            # Process repositories from file
            with open(args.repos_file, 'r') as f:
                repo_urls = [line.strip() for line in f if line.strip()]
            
            print(f"Processing {len(repo_urls)} repositories...")
            
            # Add organizational context if specified
            org_info = None
            if args.organization == "soda":
                org_info = create_soda_science_organization()
            
            results = processor.process_repository_list(repo_urls, args.output, org_info)
            
        elif args.directory:
            # Enhance files in directory
            print(f"Enhancing CodeMeta files in: {args.directory}")
            
            # Add organizational context if specified
            org_info = None
            if args.organization == "soda":
                org_info = create_soda_science_organization()
            
            results = processor.enhance_directory(args.directory, args.output, org_info)
        
        else:
            print("❌ Error: Must specify either --repos-file or --directory")
            sys.exit(1)
        
        # Print summary
        successful = len([r for r in results.values() if not r.startswith("Error")])
        failed = len([r for r in results.values() if r.startswith("Error")])
        
        print(f"\n📊 Summary:")
        print(f"  Total: {len(results)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        
        if failed > 0:
            print(f"\n❌ Failed files:")
            for file_path, result in results.items():
                if result.startswith("Error"):
                    print(f"  {file_path}: {result}")
        
        # Generate report if requested
        if args.report:
            processor.generate_report(results, args.report)
            print(f"📄 Report saved: {args.report}")
        
    except Exception as e:
        print(f"❌ Error in bulk processing: {e}")
        sys.exit(1)


def validate_command(args):
    """Handle the validate command."""
    processor = BulkProcessor(args.schema)
    
    try:
        if os.path.isfile(args.path):
            # Validate single file
            generator = CodeMetaGenerator(args.schema)
            enhancer = CodeMetaEnhancer(args.schema)
            
            with open(args.path, 'r', encoding='utf-8') as f:
                codemeta = json.load(f)
            
            warnings = generator.validate_codemeta(codemeta)
            messages = enhancer.validate_enhancement(codemeta)
            
            print(f"Validating: {args.path}")
            all_messages = warnings + messages
            
            if not warnings:
                print("✅ Validation passed")
            else:
                print("⚠️  Validation issues:")
                
            for message in all_messages:
                print(f"  {message}")
                
        elif os.path.isdir(args.path):
            # Validate directory
            print(f"Validating CodeMeta files in: {args.path}")
            results = processor.validate_directory(args.path)
            
            total_files = len(results)
            files_with_issues = len([r for r in results.values() if any("Error" in msg or "Warning" in msg for msg in r)])
            
            print(f"\n📊 Validation Summary:")
            print(f"  Total files: {total_files}")
            print(f"  Files with issues: {files_with_issues}")
            print(f"  Clean files: {total_files - files_with_issues}")
            
            if args.verbose:
                print(f"\n📋 Detailed Results:")
                for filepath, messages in results.items():
                    filename = os.path.basename(filepath)
                    print(f"\n{filename}:")
                    for message in messages:
                        print(f"  {message}")
        
        else:
            print(f"❌ Error: Path not found: {args.path}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error validating: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CodeMeta Generator - Generate and enhance CodeMeta files for research software",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate CodeMeta for a repository
  python -m src.cli generate --repo https://github.com/owner/repo --output codemeta.json
  
  # Enhance existing CodeMeta file
  python -m src.cli enhance --input codemeta.json --schema 3.0
  
  # Bulk process repositories
  python -m src.cli bulk --repos-file repos.txt --output ./output/
  
  # Bulk enhance directory
  python -m src.cli bulk --directory ./codemeta_files/ --organization soda
  
  # Validate CodeMeta files
  python -m src.cli validate ./codemeta_files/ --verbose
        """
    )
    
    parser.add_argument('--schema', choices=['2.0', '3.0'], default='3.0',
                       help='CodeMeta schema version (default: 3.0)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate CodeMeta from repository')
    generate_parser.add_argument('--repo', required=True, help='GitHub repository URL')
    generate_parser.add_argument('--output', required=True, help='Output CodeMeta file path')
    generate_parser.add_argument('--organization', choices=['soda'], 
                                help='Add organizational context')
    
    # Enhance command
    enhance_parser = subparsers.add_parser('enhance', help='Enhance existing CodeMeta file')
    enhance_parser.add_argument('--input', required=True, help='Input CodeMeta file path')
    enhance_parser.add_argument('--output', help='Output file path (overwrites input if not specified)')
    enhance_parser.add_argument('--organization', choices=['soda'], 
                               help='Add organizational context')
    
    # Bulk command
    bulk_parser = subparsers.add_parser('bulk', help='Bulk process repositories or files')
    bulk_group = bulk_parser.add_mutually_exclusive_group(required=True)
    bulk_group.add_argument('--repos-file', help='File containing repository URLs (one per line)')
    bulk_group.add_argument('--directory', help='Directory containing CodeMeta files to enhance')
    bulk_parser.add_argument('--output', required=True, help='Output directory')
    bulk_parser.add_argument('--organization', choices=['soda'], 
                            help='Add organizational context')
    bulk_parser.add_argument('--workers', type=int, default=4, 
                            help='Number of concurrent workers (default: 4)')
    bulk_parser.add_argument('--report', help='Generate processing report file')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate CodeMeta files')
    validate_parser.add_argument('path', help='File or directory to validate')
    validate_parser.add_argument('--verbose', action='store_true', 
                                help='Show detailed validation results')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Route to appropriate command handler
    if args.command == 'generate':
        generate_command(args)
    elif args.command == 'enhance':
        enhance_command(args)
    elif args.command == 'bulk':
        bulk_command(args)
    elif args.command == 'validate':
        validate_command(args)


if __name__ == '__main__':
    main()

