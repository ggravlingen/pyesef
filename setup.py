#!/usr/bin/env python3
"""Set up pyesef."""

from pathlib import Path

from setuptools import find_packages, setup

PROJECT_DIR = Path(__file__).parent.resolve()
README_FILE = PROJECT_DIR / "README.md"
LONG_DESCRIPTION = README_FILE.read_text(encoding="utf-8")

VERSION = (PROJECT_DIR / "pyesef" / "VERSION").read_text().strip()

GITHUB_URL = "https://github.com/ggravlingen/pyesef"
DOWNLOAD_URL = f"{GITHUB_URL}/archive/{VERSION}.zip"

PACKAGES = find_packages(exclude=["tests", "tests.*"])

setup(
    name="pyesef",
    packages=PACKAGES,
    python_requires=">=3.9",
    version=VERSION,
    long_description=LONG_DESCRIPTION,
    author='ggravlingen',
    author_email="no@email.com",
    long_description_content_type="text/markdown",
    url=GITHUB_URL,
    include_package_data=True,
    license="MIT",
    keywords='esef financial statement',
    download_url=DOWNLOAD_URL,
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Intended Audience :: Financial and Insurance Industry",
    ],
)
