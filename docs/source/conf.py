import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

project = "pycrockford_msgspec"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]
html_theme = "alabaster"
