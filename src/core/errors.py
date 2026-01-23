"""Custom exception classes for the Codemeta generator."""


class CodemetaError(Exception):
    """Base exception class for all Codemeta generator errors."""
    pass


class ConfigError(CodemetaError):
    """Raised when there is an error in configuration or command-line arguments."""
    pass


class GitHubAPIError(CodemetaError):
    """Raised when there is an error communicating with the GitHub API."""
    pass


class InvalidRepositoryError(CodemetaError):
    """Raised when the provided GitHub repository URL is invalid."""
    pass


class RepositoryNotFoundError(CodemetaError):
    """Raised when the GitHub repository cannot be found."""
    pass


class CodemetaGenerationError(CodemetaError):
    """Raised when there is an error generating the Codemeta metadata."""
    pass


class OutputError(CodemetaError):
    """Raised when there is an error writing the output file."""
    pass
