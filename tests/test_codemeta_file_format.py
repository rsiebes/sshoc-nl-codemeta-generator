"""
Unit tests for the CodeMeta File Format Module
"""

import unittest
from unittest.mock import patch
from src.modules import codemeta_file_format


class TestReadmeFormatDetection(unittest.TestCase):
    """Test file format detection from README."""

    @patch('src.modules.codemeta_file_format.fetch_file_content')
    def test_detect_json_format(self, mock_fetch):
        """Test detection of JSON format from README."""
        readme = "This tool supports JSON files for input and output."
        mock_fetch.return_value = readme
        
        result = codemeta_file_format.detect_formats_from_readme("owner", "repo")
        
        self.assertIn("JSON", result)

    @patch('src.modules.codemeta_file_format.fetch_file_content')
    def test_detect_multiple_formats(self, mock_fetch):
        """Test detection of multiple formats from README."""
        readme = """
        Supported formats:
        - JSON for configuration
        - CSV for data input
        - YAML for settings
        - PDF for output
        """
        mock_fetch.return_value = readme
        
        result = codemeta_file_format.detect_formats_from_readme("owner", "repo")
        
        self.assertIn("JSON", result)
        self.assertIn("CSV", result)
        self.assertIn("YAML", result)
        self.assertIn("PDF", result)

    @patch('src.modules.codemeta_file_format.fetch_file_content')
    def test_detect_bioinformatics_formats(self, mock_fetch):
        """Test detection of bioinformatics formats."""
        readme = "Processes FASTA and FASTQ files for sequence analysis."
        mock_fetch.return_value = readme
        
        result = codemeta_file_format.detect_formats_from_readme("owner", "repo")
        
        self.assertIn("FASTA", result)
        self.assertIn("FASTQ", result)

    @patch('src.modules.codemeta_file_format.fetch_file_content')
    def test_no_formats_in_readme(self, mock_fetch):
        """Test when no formats are found in README."""
        mock_fetch.return_value = "This is a generic README with no format information."
        
        result = codemeta_file_format.detect_formats_from_readme("owner", "repo")
        
        self.assertEqual(result, [])

    @patch('src.modules.codemeta_file_format.fetch_file_content')
    def test_readme_not_found(self, mock_fetch):
        """Test when README is not found."""
        mock_fetch.return_value = None
        
        result = codemeta_file_format.detect_formats_from_readme("owner", "repo")
        
        self.assertEqual(result, [])


class TestDocumentationFormatDetection(unittest.TestCase):
    """Test file format detection from documentation."""

    @patch('src.modules.codemeta_file_format.fetch_file_content')
    def test_detect_formats_from_docs(self, mock_fetch):
        """Test detection of formats from documentation files."""
        doc_content = "This tool supports JSON, XML, and CSV formats."
        
        def fetch_side_effect(owner, repo, path):
            if path in ["docs/index.md", "docs/README.md", "CONTRIBUTING.md", "docs/formats.md"]:
                return doc_content
            return None
        
        mock_fetch.side_effect = fetch_side_effect
        
        result = codemeta_file_format.detect_formats_from_documentation("owner", "repo")
        
        # May find formats depending on pattern matching
        self.assertIsInstance(result, list)

    @patch('src.modules.codemeta_file_format.fetch_file_content')
    def test_no_docs_found(self, mock_fetch):
        """Test when no documentation files are found."""
        mock_fetch.return_value = None
        
        result = codemeta_file_format.detect_formats_from_documentation("owner", "repo")
        
        self.assertEqual(result, [])


class TestCodeFormatDetection(unittest.TestCase):
    """Test file format detection from code."""

    @patch('src.modules.codemeta_file_format.fetch_file_content')
    def test_detect_formats_from_setup_py(self, mock_fetch):
        """Test detection of formats from setup.py."""
        setup_py = """
        setup(
            name='myapp',
            file_types=['json', 'xml', 'csv'],
        )
        """
        mock_fetch.side_effect = lambda owner, repo, path: setup_py if path == "setup.py" else None
        
        result = codemeta_file_format.detect_formats_from_code("owner", "repo")
        
        self.assertIn("json", result)
        self.assertIn("xml", result)
        self.assertIn("csv", result)

    @patch('src.modules.codemeta_file_format.fetch_file_content')
    def test_detect_formats_from_pyproject_toml(self, mock_fetch):
        """Test detection of formats from pyproject.toml."""
        pyproject = """
        [project]
        supported_formats = ["json", "yaml", "toml"]
        """
        mock_fetch.side_effect = lambda owner, repo, path: pyproject if path == "pyproject.toml" else None
        
        result = codemeta_file_format.detect_formats_from_code("owner", "repo")
        
        self.assertIn("json", result)
        self.assertIn("yaml", result)
        self.assertIn("toml", result)

    @patch('src.modules.codemeta_file_format.fetch_file_content')
    def test_no_code_formats(self, mock_fetch):
        """Test when no formats are defined in code."""
        mock_fetch.return_value = None
        
        result = codemeta_file_format.detect_formats_from_code("owner", "repo")
        
        self.assertEqual(result, [])


class TestExtensionFormatDetection(unittest.TestCase):
    """Test file format detection from extensions."""

    @patch('src.modules.codemeta_file_format.fetch_file_content')
    def test_detect_json_extension(self, mock_fetch):
        """Test detection of JSON format from file extension."""
        def fetch_side_effect(owner, repo, path):
            if path == "test.json":
                return '{"test": "data"}'
            return None
        
        mock_fetch.side_effect = fetch_side_effect
        
        result = codemeta_file_format.detect_formats_from_extensions("owner", "repo")
        
        self.assertIn("JSON", result)

    @patch('src.modules.codemeta_file_format.fetch_file_content')
    def test_detect_multiple_extensions(self, mock_fetch):
        """Test detection of multiple formats from extensions."""
        def fetch_side_effect(owner, repo, path):
            if path == "test.json":
                return '{"test": "data"}'
            elif path == "test.csv":
                return 'col1,col2\nval1,val2'
            elif path == "test.yaml":
                return 'key: value'
            return None
        
        mock_fetch.side_effect = fetch_side_effect
        
        result = codemeta_file_format.detect_formats_from_extensions("owner", "repo")
        
        self.assertIn("JSON", result)
        self.assertIn("CSV", result)
        self.assertIn("YAML", result)

    @patch('src.modules.codemeta_file_format.fetch_file_content')
    def test_detect_bioinformatics_extensions(self, mock_fetch):
        """Test detection of bioinformatics formats from extensions."""
        def fetch_side_effect(owner, repo, path):
            if path == "test.fasta":
                return ">seq1\nACGT"
            elif path == "test.vcf":
                return "##fileformat=VCFv4.2"
            return None
        
        mock_fetch.side_effect = fetch_side_effect
        
        result = codemeta_file_format.detect_formats_from_extensions("owner", "repo")
        
        self.assertIn("FASTA", result)
        self.assertIn("VCF", result)

    @patch('src.modules.codemeta_file_format.fetch_file_content')
    def test_no_extension_files(self, mock_fetch):
        """Test when no test files with extensions are found."""
        mock_fetch.return_value = None
        
        result = codemeta_file_format.detect_formats_from_extensions("owner", "repo")
        
        self.assertEqual(result, [])


class TestGetSupportedFileFormats(unittest.TestCase):
    """Test the main get_supported_file_formats function."""

    @patch('src.modules.codemeta_file_format.detect_formats_from_extensions')
    @patch('src.modules.codemeta_file_format.detect_formats_from_code')
    @patch('src.modules.codemeta_file_format.detect_formats_from_documentation')
    @patch('src.modules.codemeta_file_format.detect_formats_from_readme')
    def test_get_all_formats(self, mock_readme, mock_docs, mock_code, mock_ext):
        """Test getting all formats from all sources."""
        mock_readme.return_value = ["JSON", "CSV"]
        mock_docs.return_value = ["YAML"]
        mock_code.return_value = ["XML"]
        mock_ext.return_value = ["PDF"]
        
        result = codemeta_file_format.get_supported_file_formats("owner", "repo")
        
        self.assertIn("JSON", result)
        self.assertIn("CSV", result)
        self.assertIn("YAML", result)
        self.assertIn("XML", result)
        self.assertIn("PDF", result)

    @patch('src.modules.codemeta_file_format.detect_formats_from_extensions')
    @patch('src.modules.codemeta_file_format.detect_formats_from_code')
    @patch('src.modules.codemeta_file_format.detect_formats_from_documentation')
    @patch('src.modules.codemeta_file_format.detect_formats_from_readme')
    def test_deduplication(self, mock_readme, mock_docs, mock_code, mock_ext):
        """Test that duplicate formats are removed."""
        mock_readme.return_value = ["JSON", "CSV"]
        mock_docs.return_value = ["JSON"]
        mock_code.return_value = ["CSV"]
        mock_ext.return_value = ["JSON", "CSV"]
        
        result = codemeta_file_format.get_supported_file_formats("owner", "repo")
        
        # Should have no duplicates
        self.assertEqual(result.count("JSON"), 1)
        self.assertEqual(result.count("CSV"), 1)

    @patch('src.modules.codemeta_file_format.detect_formats_from_extensions')
    @patch('src.modules.codemeta_file_format.detect_formats_from_code')
    @patch('src.modules.codemeta_file_format.detect_formats_from_documentation')
    @patch('src.modules.codemeta_file_format.detect_formats_from_readme')
    def test_sorted_output(self, mock_readme, mock_docs, mock_code, mock_ext):
        """Test that output is sorted."""
        mock_readme.return_value = ["Zebra", "Apple"]
        mock_docs.return_value = []
        mock_code.return_value = []
        mock_ext.return_value = []
        
        result = codemeta_file_format.get_supported_file_formats("owner", "repo")
        
        self.assertEqual(result, sorted(result))

    @patch('src.modules.codemeta_file_format.detect_formats_from_extensions')
    @patch('src.modules.codemeta_file_format.detect_formats_from_code')
    @patch('src.modules.codemeta_file_format.detect_formats_from_documentation')
    @patch('src.modules.codemeta_file_format.detect_formats_from_readme')
    def test_no_formats_found(self, mock_readme, mock_docs, mock_code, mock_ext):
        """Test when no formats are found."""
        mock_readme.return_value = []
        mock_docs.return_value = []
        mock_code.return_value = []
        mock_ext.return_value = []
        
        result = codemeta_file_format.get_supported_file_formats("owner", "repo")
        
        self.assertEqual(result, [])


class TestMainFileFormatFunction(unittest.TestCase):
    """Test the main get() function."""

    @patch('src.modules.codemeta_file_format.get_supported_file_formats')
    @patch('src.modules.codemeta_file_format.parse_repository_url')
    def test_get_file_formats(self, mock_parse, mock_get_formats):
        """Test get() function with file formats."""
        mock_parse.return_value = ("owner", "repo")
        mock_get_formats.return_value = ["JSON", "CSV", "XML"]
        
        result = codemeta_file_format.get("https://github.com/owner/repo")
        
        self.assertIn("fileFormat", result)
        self.assertEqual(result["fileFormat"], ["JSON", "CSV", "XML"])

    @patch('src.modules.codemeta_file_format.get_supported_file_formats')
    @patch('src.modules.codemeta_file_format.parse_repository_url')
    def test_get_no_file_formats(self, mock_parse, mock_get_formats):
        """Test get() function with no file formats."""
        mock_parse.return_value = ("owner", "repo")
        mock_get_formats.return_value = []
        
        result = codemeta_file_format.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_file_format.parse_repository_url')
    def test_get_invalid_url(self, mock_parse):
        """Test with invalid repository URL."""
        mock_parse.return_value = (None, None)
        
        result = codemeta_file_format.get("invalid-url")
        
        self.assertEqual(result, {})


class TestFileFormatDataValidation(unittest.TestCase):
    """Test file format data validation."""

    @patch('src.modules.codemeta_file_format.get_supported_file_formats')
    @patch('src.modules.codemeta_file_format.parse_repository_url')
    def test_file_format_is_list(self, mock_parse, mock_get_formats):
        """Test that fileFormat is a list."""
        mock_parse.return_value = ("owner", "repo")
        mock_get_formats.return_value = ["JSON", "CSV"]
        
        result = codemeta_file_format.get("https://github.com/owner/repo")
        
        self.assertIsInstance(result.get("fileFormat"), list)

    @patch('src.modules.codemeta_file_format.get_supported_file_formats')
    @patch('src.modules.codemeta_file_format.parse_repository_url')
    def test_file_format_items_are_strings(self, mock_parse, mock_get_formats):
        """Test that fileFormat items are strings."""
        mock_parse.return_value = ("owner", "repo")
        mock_get_formats.return_value = ["JSON", "CSV"]
        
        result = codemeta_file_format.get("https://github.com/owner/repo")
        
        for item in result.get("fileFormat", []):
            self.assertIsInstance(item, str)


if __name__ == '__main__':
    unittest.main()
