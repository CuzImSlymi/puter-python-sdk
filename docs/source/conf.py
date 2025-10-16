"""Sphinx configuration file."""

# Configuration file for the Sphinx documentation builder.
import os
import sys

sys.path.insert(0, os.path.abspath("../../"))

project = "Puter Python SDK"
copyright = "2025, Puter"
author = "Puter"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns: list = []

html_theme = "alabaster"
html_static_path = ["_static"]
