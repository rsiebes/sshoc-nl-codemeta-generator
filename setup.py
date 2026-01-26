"""Setup script for SSHOC CodeMeta Generator with automatic dependency installation."""

from setuptools import setup, find_packages

setup(
    name="sshoc-codemeta-generator",
    version="6.0.0",
    description="SSHOC CodeMeta Generator with Gemini API Integration",
    author="rsiebes",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "google-genai>=0.3.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "codemeta-generator=src.main:main",
        ],
    },
)
