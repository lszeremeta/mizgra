#!/usr/bin/env python
"""The setup script."""

# TODO: Rewrite to newer pyproject.toml or setup.cfg

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mizgra",
    version="1.0.0",
    author="Łukasz Szeremeta",
    author_email="l.szeremeta.dev+mizgra@gmail.com",
    install_requires=["importlib-resources>=2.0.0", "lxml>=4.9.2", "rdflib>=6.2.0"],
    include_package_data=True,
    license="MIT License",
    description="Converts Mizar ESX MML mathematical data to property graph formats - GraphML, YARS-PG for Neo4j, and other graph databases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lszeremeta/mizgra",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: File Formats",
        "Topic :: Internet",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: General",
        "Topic :: Text Processing :: Markup",
        "Topic :: Text Processing :: Markup :: XML",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    keywords=[
        "mizgra",
        "mathematics",
        "parser",
        "CLI",
        "XML",
        "ESX",
        "RDF",
        "MML",
        "Mizar",
        "Mizar Mathematical Library",
        "Mizar Mathematical Library Knowledge Graph",
        "MMLKG",
        "CSV",
        "converter",
        "GraphML",
        "YARS-PG",
        "property graph",
        "graph",
        "graph database",
        "graph data",
        "Neo4j",
        "mathematical data",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "mizgra=mizgra.__main__:main",
        ]
    },
)
