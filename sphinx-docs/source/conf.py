# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys
from datetime import datetime

# -- Project Path Setup ------------------------------------------------------
# adding the root of the project (assumed 2 folders up)
sys.path.insert(0, os.path.abspath('../..'))                # insert the initial root path
sys.path.insert(0, os.path.abspath('../../docs'))           # insert the path for folders to be seen
sys.path.insert(0, os.path.abspath('../../Outputs'))        # | | |
sys.path.insert(0, os.path.abspath('../../Scripts'))        # v v v


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'BorisPusher'
copyright = f'{datetime.now().year}, Frank Wessel, Yoon Seong Roh'
author = 'Frank Wessel, Yoon Seong Roh, Andrew Egly, Robert Terry, Joel Rogers'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",       # build the docs from docstrings
    "sphinx.ext.napoleon",      # Google/numpy style docstrings
    "sphinx.ext.viewcode",      # link to source
    "sphinx.ext.todo"
]

templates_path = ['_templates']
exclude_patterns = []

# Napoleon Settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
