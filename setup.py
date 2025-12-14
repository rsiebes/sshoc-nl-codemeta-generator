from setuptools import setup, find_packages

setup(
    name="codemeta-generator",
    version="3.0.0",
    description="A Python-based Codemeta 3.1 metadata generator for GitHub repositories",
    author="Ronald Siebes",
    author_email="r.m.siebes@vu.nl",
    url="https://github.com/rsiebes/sshoc-nl-codemeta-generator",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "selenium>=4.8.0",
        "lxml>=4.9.0",
        "jsonschema>=4.16.0",
        "python-dateutil>=2.8.2",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
