"""
CodeMeta File Format Module

This module extracts supported file formats from a GitHub repository.
It detects input/output file formats that the software can process.
"""

from typing import Dict, List, Optional
from src.github_api import parse_repository_url, fetch_file_content
import re


# Common file format mappings
FILE_FORMAT_MAPPINGS = {
    # Document formats
    r'\.pdf': 'PDF',
    r'\.doc[x]?': 'DOCX',
    r'\.txt': 'TXT',
    r'\.md': 'Markdown',
    r'\.rst': 'reStructuredText',
    r'\.tex': 'LaTeX',
    r'\.odt': 'ODT',
    
    # Data formats
    r'\.json': 'JSON',
    r'\.xml': 'XML',
    r'\.csv': 'CSV',
    r'\.tsv': 'TSV',
    r'\.yaml|\.yml': 'YAML',
    r'\.toml': 'TOML',
    r'\.ini': 'INI',
    r'\.conf': 'CONF',
    
    # Image formats
    r'\.png': 'PNG',
    r'\.jpg|\.jpeg': 'JPEG',
    r'\.gif': 'GIF',
    r'\.svg': 'SVG',
    r'\.tiff?': 'TIFF',
    r'\.bmp': 'BMP',
    r'\.webp': 'WebP',
    
    # Audio formats
    r'\.mp3': 'MP3',
    r'\.wav': 'WAV',
    r'\.flac': 'FLAC',
    r'\.ogg': 'OGG',
    r'\.aac': 'AAC',
    
    # Video formats
    r'\.mp4': 'MP4',
    r'\.avi': 'AVI',
    r'\.mov': 'MOV',
    r'\.mkv': 'MKV',
    r'\.webm': 'WebM',
    
    # Archive formats
    r'\.zip': 'ZIP',
    r'\.tar': 'TAR',
    r'\.gz': 'GZIP',
    r'\.rar': 'RAR',
    r'\.7z': '7Z',
    
    # Code formats
    r'\.py': 'Python',
    r'\.js': 'JavaScript',
    r'\.ts': 'TypeScript',
    r'\.java': 'Java',
    r'\.cpp|\.cc|\.cxx': 'C++',
    r'\.c': 'C',
    r'\.rs': 'Rust',
    r'\.go': 'Go',
    r'\.rb': 'Ruby',
    r'\.php': 'PHP',
    r'\.sh': 'Shell',
    r'\.r': 'R',
    
    # Scientific formats
    r'\.hdf5?': 'HDF5',
    r'\.nc': 'NetCDF',
    r'\.fits': 'FITS',
    r'\.grib': 'GRIB',
    
    # Bioinformatics formats
    r'\.fasta?': 'FASTA',
    r'\.fastq?': 'FASTQ',
    r'\.vcf': 'VCF',
    r'\.bam': 'BAM',
    r'\.sam': 'SAM',
    r'\.gff': 'GFF',
    
    # Geospatial formats
    r'\.shp': 'Shapefile',
    r'\.geojson': 'GeoJSON',
    r'\.kml': 'KML',
    r'\.gml': 'GML',
}


def detect_formats_from_readme(owner: str, repo: str) -> List[str]:
    """
    Detect file formats mentioned in README.md.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected file formats.
    """
    formats = set()
    
    try:
        readme = fetch_file_content(owner, repo, "README.md")
        if readme:
            readme_lower = readme.lower()
            
            # Check for format mentions
            format_keywords = {
                'json': 'JSON',
                'xml': 'XML',
                'csv': 'CSV',
                'yaml': 'YAML',
                'pdf': 'PDF',
                'png': 'PNG',
                'jpeg': 'JPEG',
                'jpg': 'JPEG',
                'mp4': 'MP4',
                'fasta': 'FASTA',
                'fastq': 'FASTQ',
                'vcf': 'VCF',
                'bam': 'BAM',
                'geojson': 'GeoJSON',
                'shapefile': 'Shapefile',
            }
            
            for keyword, format_name in format_keywords.items():
                if keyword in readme_lower:
                    formats.add(format_name)
    except Exception:
        pass
    
    return list(formats)


def detect_formats_from_documentation(owner: str, repo: str) -> List[str]:
    """
    Detect file formats from documentation files.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected file formats.
    """
    formats = set()
    
    doc_files = ["docs/index.md", "docs/README.md", "CONTRIBUTING.md", "docs/formats.md"]
    
    for doc_file in doc_files:
        try:
            content = fetch_file_content(owner, repo, doc_file)
            if content:
                # Look for file extension patterns
                pattern = r'(?:supports?|accepts?|processes?|handles?|converts?)\s+(?:the\s+)?([A-Z0-9\s,/\-]+)\s+(?:format|file|extension)'
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Parse format names
                    format_names = [f.strip() for f in match.split(',')]
                    formats.update(format_names)
        except Exception:
            pass
    
    return list(formats)


def detect_formats_from_code(owner: str, repo: str) -> List[str]:
    """
    Detect file formats from code analysis.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected file formats.
    """
    formats = set()
    
    # Check setup.py for file_types or supported_formats
    try:
        setup_py = fetch_file_content(owner, repo, "setup.py")
        if setup_py:
            # Look for file format specifications
            pattern = r'(?:file_types|supported_formats|formats)\s*=\s*\[(.*?)\]'
            matches = re.findall(pattern, setup_py, re.DOTALL)
            for match in matches:
                # Extract format names
                format_list = re.findall(r'["\']([^"\']+)["\']', match)
                formats.update(format_list)
    except Exception:
        pass
    
    # Check pyproject.toml
    try:
        pyproject = fetch_file_content(owner, repo, "pyproject.toml")
        if pyproject:
            pattern = r'(?:file_types|supported_formats|formats)\s*=\s*\[(.*?)\]'
            matches = re.findall(pattern, pyproject, re.DOTALL)
            for match in matches:
                format_list = re.findall(r'["\']([^"\']+)["\']', match)
                formats.update(format_list)
    except Exception:
        pass
    
    return list(formats)


def detect_formats_from_extensions(owner: str, repo: str) -> List[str]:
    """
    Detect file formats based on file extensions in the repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of detected file formats.
    """
    formats = set()
    
    # Common file extensions to check
    test_extensions = [
        'test.json', 'test.xml', 'test.csv', 'test.yaml',
        'test.pdf', 'test.png', 'test.jpg',
        'test.fasta', 'test.fastq', 'test.vcf',
        'test.geojson', 'test.shp'
    ]
    
    for ext_file in test_extensions:
        try:
            content = fetch_file_content(owner, repo, ext_file)
            if content:
                # Extract format from extension
                ext = ext_file.split('.')[-1]
                for pattern, format_name in FILE_FORMAT_MAPPINGS.items():
                    if re.search(pattern, f'.{ext}'):
                        formats.add(format_name)
                        break
        except Exception:
            pass
    
    return list(formats)


def get_supported_file_formats(owner: str, repo: str) -> List[str]:
    """
    Detect all supported file formats from a repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of supported file formats.
    """
    all_formats = set()
    
    # Detect from multiple sources
    readme_formats = detect_formats_from_readme(owner, repo)
    all_formats.update(readme_formats)
    
    doc_formats = detect_formats_from_documentation(owner, repo)
    all_formats.update(doc_formats)
    
    code_formats = detect_formats_from_code(owner, repo)
    all_formats.update(code_formats)
    
    ext_formats = detect_formats_from_extensions(owner, repo)
    all_formats.update(ext_formats)
    
    return sorted(list(all_formats))


def get(repository_url: str) -> Dict:
    """
    Extract file format information from a GitHub repository.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'fileFormat' key if formats found.
    """
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}
    
    formats = get_supported_file_formats(owner, repo)
    
    # Only return if we found something
    if formats:
        return {"fileFormat": formats}
    
    return {}
