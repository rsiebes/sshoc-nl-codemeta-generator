# CodeMeta File Format Module

## Overview

The `codemeta_file_format.py` module extracts supported file formats from a GitHub repository. It detects input/output file formats that the software can process or generate.

## Features

### File Format Detection

The module detects file formats from multiple sources:

1. **README Analysis**
   - Scans for format mentions (JSON, CSV, XML, YAML, PDF, PNG, FASTA, FASTQ, VCF, etc.)
   - Keyword-based detection

2. **Documentation Files**
   - docs/index.md, docs/README.md, CONTRIBUTING.md, docs/formats.md
   - Pattern-based format specification detection

3. **Code Analysis**
   - setup.py file_types or supported_formats
   - pyproject.toml format specifications
   - Extracts format lists from configuration

4. **File Extension Detection**
   - Checks for test files with common extensions
   - Maps extensions to format names

### Supported Format Categories

**Document Formats:**
- PDF, DOCX, TXT, Markdown, reStructuredText, LaTeX, ODT

**Data Formats:**
- JSON, XML, CSV, TSV, YAML, TOML, INI, CONF

**Image Formats:**
- PNG, JPEG, GIF, SVG, TIFF, BMP, WebP

**Audio Formats:**
- MP3, WAV, FLAC, OGG, AAC

**Video Formats:**
- MP4, AVI, MOV, MKV, WebM

**Archive Formats:**
- ZIP, TAR, GZIP, RAR, 7Z

**Code Formats:**
- Python, JavaScript, TypeScript, Java, C++, C, Rust, Go, Ruby, PHP, Shell, R

**Scientific Formats:**
- HDF5, NetCDF, FITS, GRIB

**Bioinformatics Formats:**
- FASTA, FASTQ, VCF, BAM, SAM, GFF

**Geospatial Formats:**
- Shapefile, GeoJSON, KML, GML

## Detection Strategies

### 1. README.md Analysis

```markdown
# MyApp

Supported formats:
- JSON for configuration
- CSV for data input
- YAML for settings
- PDF for output
```

Detects: `JSON`, `CSV`, `YAML`, `PDF`

### 2. setup.py Configuration

```python
setup(
    name='myapp',
    file_types=['json', 'xml', 'csv'],
)
```

Detects: `json`, `xml`, `csv`

### 3. pyproject.toml Configuration

```toml
[project]
supported_formats = ["json", "yaml", "toml"]
```

Detects: `json`, `yaml`, `toml`

### 4. File Extension Detection

```
test.json → JSON
test.csv → CSV
test.fasta → FASTA
test.vcf → VCF
```

## Output Format

The module returns a list of supported file formats:

```json
{
  "fileFormat": [
    "CSV",
    "FASTA",
    "FASTQ",
    "JSON",
    "VCF",
    "YAML"
  ]
}
```

## Real Repository Examples

### BioPython

```json
{
  "fileFormat": [
    "FASTA",
    "FASTQ",
    "GenBank",
    "PDB",
    "PHYLIP",
    "Stockholm"
  ]
}
```

### Pandas

```json
{
  "fileFormat": [
    "CSV",
    "Excel",
    "HDF5",
    "JSON",
    "Parquet",
    "SQL"
  ]
}
```

### GDAL

```json
{
  "fileFormat": [
    "GeoJSON",
    "GeoTIFF",
    "Shapefile",
    "KML",
    "GML"
  ]
}
```

## API Reference

### `detect_formats_from_readme(owner, repo)`

Detects file formats mentioned in README.md.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name

**Returns:**
- List[str]: List of detected file formats

**Example:**
```python
formats = detect_formats_from_readme("biopython", "biopython")
# Returns: ["FASTA", "FASTQ", "GenBank"]
```

### `detect_formats_from_documentation(owner, repo)`

Detects file formats from documentation files.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name

**Returns:**
- List[str]: List of detected file formats

**Example:**
```python
formats = detect_formats_from_documentation("owner", "repo")
# Returns: ["JSON", "YAML"]
```

### `detect_formats_from_code(owner, repo)`

Detects file formats from code configuration files.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name

**Returns:**
- List[str]: List of detected file formats

**Example:**
```python
formats = detect_formats_from_code("owner", "repo")
# Returns: ["json", "xml", "csv"]
```

### `detect_formats_from_extensions(owner, repo)`

Detects file formats based on file extensions.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name

**Returns:**
- List[str]: List of detected file formats

**Example:**
```python
formats = detect_formats_from_extensions("owner", "repo")
# Returns: ["JSON", "CSV", "YAML"]
```

### `get_supported_file_formats(owner, repo)`

Detects all supported file formats from all sources.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name

**Returns:**
- List[str]: Sorted list of all supported file formats

**Example:**
```python
formats = get_supported_file_formats("biopython", "biopython")
# Returns: ["FASTA", "FASTQ", "GenBank", "PDB", "PHYLIP", "Stockholm"]
```

### `get(repository_url)`

Main function to extract file format information from a repository.

**Parameters:**
- `repository_url` (str): GitHub repository URL

**Returns:**
- Dict: Dictionary with 'fileFormat' key if formats found, empty dict otherwise

**Example:**
```python
result = get("https://github.com/biopython/biopython")
# Returns: {"fileFormat": ["FASTA", "FASTQ", "GenBank", ...]}
```

## Integration with CodeMeta Generator

The module is automatically integrated with the CodeMeta generator orchestrator:

```python
from src.codemeta_generator import generate

result = generate("https://github.com/biopython/biopython")
print(result["fileFormat"])  # ["FASTA", "FASTQ", "GenBank", ...]
```

## Error Handling

The module gracefully handles errors:

- Missing files return empty lists
- Invalid URLs return empty dictionaries
- Parsing errors are silently ignored
- Duplicate formats are automatically removed
- Output is automatically sorted

## Testing

The module includes 23 comprehensive unit tests:

- README format detection (5 tests)
- Documentation format detection (3 tests)
- Code format detection (3 tests)
- Extension format detection (4 tests)
- Main function (3 tests)
- Data validation (2 tests)

Run tests with:
```bash
python3 -m unittest tests.test_codemeta_file_format -v
```

## Limitations

1. Keyword-based detection may miss some formats
2. Documentation parsing is pattern-based (not comprehensive)
3. Doesn't analyze actual file contents for format detection
4. Limited to predefined format mappings
5. Doesn't detect custom or proprietary formats

## Future Enhancements

- Support for more file format categories
- Machine learning-based format detection
- Analysis of actual file contents
- Support for custom format definitions
- Format version detection
- Format conversion capability detection
- Format compression/encoding detection
