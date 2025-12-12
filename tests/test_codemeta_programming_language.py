"""
Unit tests for the codemeta_programming_language module.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.modules import codemeta_programming_language


class TestLanguageNormalization(unittest.TestCase):
    """Test language name normalization."""

    def test_normalize_lowercase_python(self):
        """Test normalization of lowercase 'python'."""
        result = codemeta_programming_language.normalize_language("python")
        self.assertEqual(result, "Python")

    def test_normalize_uppercase_java(self):
        """Test normalization of uppercase 'JAVA'."""
        result = codemeta_programming_language.normalize_language("JAVA")
        self.assertEqual(result, "Java")

    def test_normalize_mixed_case_javascript(self):
        """Test normalization of mixed case 'javaScript'."""
        result = codemeta_programming_language.normalize_language("javaScript")
        self.assertEqual(result, "JavaScript")

    def test_normalize_c_plus_plus(self):
        """Test normalization of 'c++'."""
        result = codemeta_programming_language.normalize_language("c++")
        self.assertEqual(result, "C++")

    def test_normalize_c_sharp(self):
        """Test normalization of 'c#'."""
        result = codemeta_programming_language.normalize_language("c#")
        self.assertEqual(result, "C#")

    def test_normalize_with_whitespace(self):
        """Test normalization with leading/trailing whitespace."""
        result = codemeta_programming_language.normalize_language("  rust  ")
        self.assertEqual(result, "Rust")

    def test_normalize_empty_string(self):
        """Test normalization of empty string."""
        result = codemeta_programming_language.normalize_language("")
        self.assertEqual(result, "")

    def test_normalize_golang_to_go(self):
        """Test normalization of 'golang' to 'Go'."""
        result = codemeta_programming_language.normalize_language("golang")
        self.assertEqual(result, "Go")

    def test_normalize_fsharp(self):
        """Test normalization of 'fsharp' to 'F#'."""
        result = codemeta_programming_language.normalize_language("fsharp")
        self.assertEqual(result, "F#")

    def test_normalize_objective_c(self):
        """Test normalization of 'objective-c'."""
        result = codemeta_programming_language.normalize_language("objective-c")
        self.assertEqual(result, "Objective-C")


class TestGitHubAPIExtraction(unittest.TestCase):
    """Test extraction from GitHub API."""

    @patch('src.modules.codemeta_programming_language.fetch_repository_languages')
    def test_extract_from_github_api_single_language(self, mock_get_languages):
        """Test extraction of single language from GitHub API."""
        mock_get_languages.return_value = {"Python": 100}
        result = codemeta_programming_language.extract_from_github_api(
            "https://github.com/owner/repo"
        )
        self.assertEqual(result, ["Python"])

    @patch('src.modules.codemeta_programming_language.fetch_repository_languages')
    def test_extract_from_github_api_multiple_languages(self, mock_get_languages):
        """Test extraction of multiple languages from GitHub API."""
        mock_get_languages.return_value = {"Python": 50, "JavaScript": 30, "HTML": 20}
        result = codemeta_programming_language.extract_from_github_api(
            "https://github.com/owner/repo"
        )
        self.assertEqual(result, ["Python", "JavaScript", "HTML"])

    @patch('src.modules.codemeta_programming_language.fetch_repository_languages')
    def test_extract_from_github_api_empty(self, mock_get_languages):
        """Test extraction when no languages found."""
        mock_get_languages.return_value = {}
        result = codemeta_programming_language.extract_from_github_api(
            "https://github.com/owner/repo"
        )
        self.assertEqual(result, [])

    @patch('src.modules.codemeta_programming_language.fetch_repository_languages')
    def test_extract_from_github_api_error(self, mock_get_languages):
        """Test extraction when API raises error."""
        mock_get_languages.side_effect = Exception("API Error")
        result = codemeta_programming_language.extract_from_github_api(
            "https://github.com/owner/repo"
        )
        self.assertEqual(result, [])


class TestConfigFileExtraction(unittest.TestCase):
    """Test extraction from configuration files."""

    @patch('src.modules.codemeta_programming_language.fetch_file_content')
    def test_extract_from_setup_py(self, mock_fetch):
        """Test extraction from setup.py."""
        mock_fetch.return_value = "name='myproject'"
        result = codemeta_programming_language.extract_from_setup_py(
            "https://github.com/owner/repo"
        )
        self.assertEqual(result, ["Python"])

    @patch('src.modules.codemeta_programming_language.fetch_file_content')
    def test_extract_from_cargo_toml(self, mock_fetch):
        """Test extraction from Cargo.toml."""
        mock_fetch.return_value = "[package]\nname = 'myproject'"
        result = codemeta_programming_language.extract_from_cargo_toml(
            "https://github.com/owner/repo"
        )
        self.assertEqual(result, ["Rust"])

    @patch('src.modules.codemeta_programming_language.fetch_file_content')
    def test_extract_from_gemfile(self, mock_fetch):
        """Test extraction from Gemfile."""
        mock_fetch.return_value = "gem 'rails'"
        result = codemeta_programming_language.extract_from_gemfile(
            "https://github.com/owner/repo"
        )
        self.assertEqual(result, ["Ruby"])

    @patch('src.modules.codemeta_programming_language.fetch_file_content')
    def test_extract_from_composer_json(self, mock_fetch):
        """Test extraction from composer.json."""
        mock_fetch.return_value = '{"name": "myproject"}'
        result = codemeta_programming_language.extract_from_composer_json(
            "https://github.com/owner/repo"
        )
        self.assertEqual(result, ["PHP"])

    @patch('src.modules.codemeta_programming_language.fetch_file_content')
    def test_extract_from_pom_xml(self, mock_fetch):
        """Test extraction from pom.xml."""
        mock_fetch.return_value = "<project></project>"
        result = codemeta_programming_language.extract_from_pom_xml(
            "https://github.com/owner/repo"
        )
        self.assertEqual(result, ["Java"])

    @patch('src.modules.codemeta_programming_language.fetch_file_content')
    def test_extract_from_go_mod(self, mock_fetch):
        """Test extraction from go.mod."""
        mock_fetch.return_value = "module github.com/owner/repo"
        result = codemeta_programming_language.extract_from_go_mod(
            "https://github.com/owner/repo"
        )
        self.assertEqual(result, ["Go"])

    @patch('src.modules.codemeta_programming_language.fetch_file_content')
    def test_extract_from_package_json(self, mock_fetch):
        """Test extraction from package.json."""
        mock_fetch.return_value = '{"name": "myproject", "engines": {"node": ">=14"}}'
        result = codemeta_programming_language.extract_from_package_json(
            "https://github.com/owner/repo"
        )
        self.assertEqual(result, ["JavaScript"])


class TestGetFunction(unittest.TestCase):
    """Test the main get() function."""

    @patch('src.modules.codemeta_programming_language.extract_from_github_api')
    def test_get_returns_dict(self, mock_extract_api):
        """Test that get() returns a dictionary."""
        mock_extract_api.return_value = ["Python"]
        result = codemeta_programming_language.get("https://github.com/owner/repo")
        self.assertIsInstance(result, dict)

    @patch('src.modules.codemeta_programming_language.extract_from_github_api')
    def test_get_returns_programming_language_key(self, mock_extract_api):
        """Test that get() returns 'programmingLanguage' key."""
        mock_extract_api.return_value = ["Python"]
        result = codemeta_programming_language.get("https://github.com/owner/repo")
        self.assertIn("programmingLanguage", result)

    @patch('src.modules.codemeta_programming_language.extract_from_github_api')
    def test_get_single_language_as_string(self, mock_extract_api):
        """Test that single language is returned as string."""
        mock_extract_api.return_value = ["Python"]
        result = codemeta_programming_language.get("https://github.com/owner/repo")
        self.assertEqual(result["programmingLanguage"], "Python")
        self.assertIsInstance(result["programmingLanguage"], str)

    @patch('src.modules.codemeta_programming_language.extract_from_github_api')
    def test_get_multiple_languages_as_list(self, mock_extract_api):
        """Test that multiple languages are returned as list."""
        mock_extract_api.return_value = ["Python", "JavaScript"]
        result = codemeta_programming_language.get("https://github.com/owner/repo")
        self.assertEqual(result["programmingLanguage"], ["Python", "JavaScript"])
        self.assertIsInstance(result["programmingLanguage"], list)

    @patch('src.modules.codemeta_programming_language.extract_from_github_api')
    def test_get_no_languages(self, mock_extract_api):
        """Test that empty dict is returned when no languages found."""
        mock_extract_api.return_value = []
        result = codemeta_programming_language.get("https://github.com/owner/repo")
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_programming_language.extract_from_github_api')
    def test_get_removes_duplicates(self, mock_extract_api):
        """Test that duplicate languages are removed."""
        mock_extract_api.return_value = ["Python", "Python", "JavaScript"]
        result = codemeta_programming_language.get("https://github.com/owner/repo")
        self.assertEqual(result["programmingLanguage"], ["Python", "JavaScript"])


class TestLanguageContent(unittest.TestCase):
    """Test the content quality of extracted languages."""

    @patch('src.modules.codemeta_programming_language.extract_from_github_api')
    def test_language_is_string_or_list(self, mock_extract_api):
        """Test that language is either string or list."""
        mock_extract_api.return_value = ["Python", "JavaScript"]
        result = codemeta_programming_language.get("https://github.com/owner/repo")
        prog_lang = result.get("programmingLanguage")
        self.assertTrue(isinstance(prog_lang, (str, list)))

    @patch('src.modules.codemeta_programming_language.extract_from_github_api')
    def test_language_not_empty_string(self, mock_extract_api):
        """Test that language is not empty string."""
        mock_extract_api.return_value = ["Python"]
        result = codemeta_programming_language.get("https://github.com/owner/repo")
        if isinstance(result.get("programmingLanguage"), str):
            self.assertTrue(len(result["programmingLanguage"]) > 0)

    @patch('src.modules.codemeta_programming_language.extract_from_github_api')
    def test_language_list_not_empty(self, mock_extract_api):
        """Test that language list is not empty."""
        mock_extract_api.return_value = ["Python", "JavaScript"]
        result = codemeta_programming_language.get("https://github.com/owner/repo")
        if isinstance(result.get("programmingLanguage"), list):
            self.assertTrue(len(result["programmingLanguage"]) > 0)

    @patch('src.modules.codemeta_programming_language.extract_from_github_api')
    def test_language_list_no_empty_strings(self, mock_extract_api):
        """Test that language list contains no empty strings."""
        mock_extract_api.return_value = ["Python", "JavaScript"]
        result = codemeta_programming_language.get("https://github.com/owner/repo")
        if isinstance(result.get("programmingLanguage"), list):
            for lang in result["programmingLanguage"]:
                self.assertTrue(len(lang) > 0)


class TestRealRepositories(unittest.TestCase):
    """Test extraction from real repositories."""

    @patch('src.modules.codemeta_programming_language.extract_from_github_api')
    def test_tensorflow_languages(self, mock_extract_api):
        """Test language extraction from TensorFlow."""
        mock_extract_api.return_value = ["Python", "C++", "CUDA"]
        result = codemeta_programming_language.get(
            "https://github.com/tensorflow/tensorflow"
        )
        self.assertIn("programmingLanguage", result)
        self.assertIsInstance(result["programmingLanguage"], list)

    @patch('src.modules.codemeta_programming_language.extract_from_github_api')
    def test_rust_languages(self, mock_extract_api):
        """Test language extraction from Rust."""
        mock_extract_api.return_value = ["Rust"]
        result = codemeta_programming_language.get("https://github.com/rust-lang/rust")
        self.assertEqual(result["programmingLanguage"], "Rust")

    @patch('src.modules.codemeta_programming_language.extract_from_github_api')
    def test_flask_languages(self, mock_extract_api):
        """Test language extraction from Flask."""
        mock_extract_api.return_value = ["Python"]
        result = codemeta_programming_language.get("https://github.com/pallets/flask")
        self.assertEqual(result["programmingLanguage"], "Python")


if __name__ == "__main__":
    unittest.main()
