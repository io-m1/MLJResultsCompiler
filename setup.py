#!/usr/bin/env python
"""Setup script for MLJ Results Compiler"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mlj-results-compiler",
    version="0.2.0",
    author="MLJ Results Compiler Contributors",
    description="AI-assisted Excel consolidation, grading, and reporting system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/io-m1/MLJResultsCompiler",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.11",
    install_requires=[
        "openpyxl==3.1.5",
        "python-telegram-bot==20.3",
        "python-dotenv==1.0.0",
        "fastapi==0.110.0",
        "uvicorn[standard]==0.23.2",
        "python-multipart==0.0.6",
        "Pillow==11.0.0",
        "aiohttp==3.9.1",
        "beautifulsoup4==4.12.2",
        "feedparser==6.0.10",
        "requests==2.31.0",
        "groq==0.4.2",
        "pandas==2.0.3",
        "numpy==1.24.3",
        "pydantic-settings>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest==7.4.3",
            "pytest-cov==4.1.0",
            "pytest-asyncio==0.21.1",
            "black==23.12.0",
            "flake8==6.1.0",
            "mypy==1.7.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "mlj-compiler=src.main:main",
        ],
    },
)
