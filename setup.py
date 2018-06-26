#! /usr/bin/env python3

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pseudo_jsonrpc",
    version="0.0.1",
    author="Salt Ho",
    author_email="asche34@outlook.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/saltb0rn/pseudo_jsonrpc",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python ::3",
        "Operating System :: OS Independent",
    ),
)
