# Configuration file for the Sphinx documentation builder.
# see https://www.sphinx-doc.org/en/master/usage/configuration.html for more details

# SPHINX BUG?: cannot find a way to place conf.py outside source dir without making templates throw warnings

import os
import sys

SOURCE_HOME = os.path.dirname(os.path.abspath(__file__))
DOCS_HOME = os.path.join(SOURCE_HOME, os.pardir)
# DOCS_HOME = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(DOCS_HOME, os.pardir)
LOGO = os.path.join(ROOT, "src", "thtools", "app", "web", "favicon.png")

sys.path.insert(0, os.path.join(ROOT, "src"))
import thtools

project = "ToeholdTools"
copyright = "2021, Lucas Ng"
author = "Lucas Ng"
version = thtools.__version__
release = version

html_theme = "sphinx_book_theme"
html_title = "ToeholdTools " + version
html_logo = LOGO
html_favicon = LOGO
templates_path = ["_templates"]
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# exclude_patterns = [os.path.join(templates_path[0], "*.rst")]

pygments_style = "xcode"
bibtex_bibfiles = [os.path.join(ROOT, "refs.bib")]

numpydoc_show_class_members = False
autosummary_generate = True
autoclass_content = "class"
autodoc_typehints = "none"

copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

extensions = [
    "sphinx.ext.coverage",
    "sphinx.ext.intersphinx",
    "numpydoc",
    "matplotlib.sphinxext.plot_directive",
    "sphinx_copybutton",
    "sphinxcontrib.bibtex",
    # "sphinx_inline_tabs",
]
html_theme_options = {
    "repository_url": "https://github.com/lkn849/thtools",
    "use_repository_button": True,
    "repository_branch": "master",
    "use_issues_button": True,
    "use_edit_page_button": True,
    "show_prev_next": False,
    "path_to_docs": "docs",
    "use_download_button": True,
    "use_fullscreen_button": True,
    "home_page_in_toc": False,
}
html_context = {
    "github_user": "https://github.com/lkn849",
    "github_repo": "https://github.com/lkn849/thtools",
    "github_version": "master",
    "doc_path": "docs/source",
}
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pathos": ("https://pathos.readthedocs.io/en/latest/", None),
    # "nupack": ("https://docs.nupack.org/", None), # not supported :(
}

if __name__ == "__main__":
    os.system(
        f"cd {DOCS_HOME} && python3 -m sphinx.cmd.build -b html source build && open "
        + os.path.join("build", "index.html")
    )
