#!/usr/bin/env python3
"""
Setup script for CodeMeta Generator

Author: Ronald Siebes (UCDS Group, VU Amsterdam)
ORCID: 0000-0001-8772-7904
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="codemeta-generator",
    version="1.0.0",
    author="Ronald Siebes",
    author_email="r.siebes@vu.nl",
    description="A comprehensive toolkit for generating and enhancing CodeMeta files for research software",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/codemeta-generator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "codemeta-generator=src.cli:main",
        ],
    },
    keywords=[
        "codemeta",
        "metadata",
        "research software",
        "software citation",
        "FAIR software",
        "software discovery",
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-username/codemeta-generator/issues",
        "Source": "https://github.com/your-username/codemeta-generator",
        "Documentation": "https://github.com/your-username/codemeta-generator/blob/main/docs/",
    },
)

