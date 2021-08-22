"""
This is the setup.py for ToeholdTools.

If you wish to use the app demo, you must also run ./src/thtools/app/build.sh
"""

import os
import shutil
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def mkdir(path):
    """Force the clearing and creation of a directory."""
    try:
        os.mkdir(path)
    except FileExistsError:
        shutil.rmtree(path, ignore_errors=True)
        os.mkdir(path)


#######################################################################

# save miRBase

import gzip
import re
import urllib.request

print("Downloading miRBase...")
mkdir("src/thtools/miRBase/")
with urllib.request.urlopen(
    "ftp://mirbase.org/pub/mirbase/CURRENT/mature.fa.gz"
) as miRBase_url:
    with gzip.GzipFile(fileobj=miRBase_url, mode="rb") as gzipped_f:
        txt = gzipped_f.read()
lines = txt.splitlines()
chunks = [b"\n".join(lines[n : n + 2]) for n in range(0, len(lines), 2)]
sorted_chunks = sorted(
    chunks,
    key=lambda x: [
        int(group) if group.isdigit() else group for group in re.split(rb"([0-9]+)", x)
    ],
)  # https://stackoverflow.com/a/2669120/13712044
miRNA_by_species = {}
for chunk in sorted_chunks:
    species = b" ".join(chunk.split()[2:4])
    if species in miRNA_by_species:
        miRNA_by_species[species].append(chunk)
    else:
        miRNA_by_species[species] = [chunk]
for species, species_chunks in miRNA_by_species.items():
    with open(b"src/thtools/miRBase/" + species + b".fa", "wb") as f:
        f.write(b"\n".join(species_chunks))

#######################################################################

# make pygments.css for docs

import datetime
from pygments.style import Style
from pygments.formatters import HtmlFormatter
from pygments.token import Token


class CustomStyle(Style):

    default_style = ""

    bg = "#f8f8f2"
    fore = "#282a36"
    comment = "#adb6cf"
    error = "#8b080b"

    # color names from https://coolors.co/
    flickr_pink = "#f72585"
    purple = "#7209b7"
    trypan_blue = "#834cff"
    absolute_zero = "#0048d0"

    styles = {
        Token.Text.Whitespace: fore,
        Token.Comment: "italic " + comment,
        Token.Comment.Preproc: "noitalic " + flickr_pink,
        Token.Keyword: flickr_pink,
        Token.Keyword.Pseudo: flickr_pink,
        Token.Keyword.Type: fore,
        Token.Operator: fore,
        Token.Operator.Word: flickr_pink,
        Token.Name.Builtin: absolute_zero,
        Token.Name.Function: trypan_blue,
        Token.Name.Class: absolute_zero,
        Token.Name.Namespace: fore,
        Token.Name.Exception: flickr_pink,
        Token.Name.Variable: "italic " + absolute_zero,
        Token.Name.Constant: flickr_pink,
        Token.Name.Label: purple,
        Token.Name.Entity: fore,
        Token.Name.Attribute: absolute_zero,
        Token.Name.Tag: flickr_pink,
        Token.Name.Decorator: fore,
        Token.Literal.String: purple,
        Token.Literal.String.Doc: "italic " + purple,
        Token.Literal.String.Interpol: "bold " + purple,
        Token.Literal.String.Escape: "bold " + purple,
        Token.Literal.String.Regex: purple,
        Token.Literal.String.Symbol: purple,
        Token.Literal.String.Other: purple,
        Token.Literal.Number: trypan_blue,
        Token.Generic.Heading: fore,
        Token.Generic.Subheading: fore,
        Token.Generic.Deleted: error,
        Token.Generic.Inserted: "bg:#50fa7b",
        Token.Generic.Error: flickr_pink,
        Token.Generic.Emph: "italic",
        Token.Generic.Strong: "bold",
        Token.Generic.Prompt: "bold " + error,
        Token.Generic.Output: fore,
        Token.Generic.Traceback: error,
        Token.Error: "border:" + error,
    }


css = HtmlFormatter(style=CustomStyle).get_style_defs()
with open("docs/source/_static/pygments.css", "w") as f:
    f.write(
        datetime.datetime.now().strftime(
            "/* Created on %b %d %Y at %H:%M:%S by make_pygments.py */"
        )
        + "\n"
        + css
    )


#######################################################################

# package app requirements

if shutil.which("npm"):
    print("npm detected: getting app requirements...")
    os.system("src/thtools/app/build.sh")

#######################################################################

# build package

from setuptools import setup, Extension

from Cython.Distutils.build_ext import new_build_ext
import numpy

print("Building with Cython...")
setup(
    ext_modules=[Extension("*", ["src/thtools/*.pyx"])],
    cmdclass={"build_ext": new_build_ext},
    include_dirs=numpy.get_include(),
)
