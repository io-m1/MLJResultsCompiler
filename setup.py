#!/usr/bin/env python3
"""
Setup script for MLJ Results Compiler
Temporary fallback to avoid PEP 517 isolation issues on Render
"""

from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    with open(req_path, 'r', encoding='utf-8') as f:
        requirements = []
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('setuptools') and not line.startswith('wheel') and not line.startswith('pip'):
                requirements.append(line)
        return requirements

setup(
    name="mlj-results-compiler",
    version="0.2.0",
    description="AI-assisted Excel consolidation, grading, and reporting system with Telegram bot and web interface",
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    author="MLJ Results Compiler Contributors",
    url="https://github.com/io-m1/MLJResultsCompiler",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=read_requirements(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Utilities",
    ],
    include_package_data=True,
    zip_safe=False,
)