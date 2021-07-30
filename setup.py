"""setup.py"""

#######################################################################

import os
import shutil


def mkdir(path):
    """Force the clearing and creation of a directory."""
    try:
        os.mkdir(path)
    except FileExistsError:
        shutil.rmtree(path, ignore_errors=True)
        os.mkdir(path)


#######################################################################

# download fonts

import urllib.request
import io
import zipfile


def mkfont(font, path):
    """Download font from https://google-webfonts-helper.herokuapp.com/"""
    font_dir = "src/thtools/app/web/assets/fonts/" + font
    mkdir(font_dir)
    with urllib.request.urlopen(path) as font_url:
        with zipfile.ZipFile(io.BytesIO(font_url.read())) as zipped_f:
            zipped_f.extractall(font_dir)


print("Downloading fonts...")
mkdir("src/thtools/app/web/assets")
mkdir("src/thtools/app/web/assets/fonts")

mkfont(
    "Montserrat",
    "https://google-webfonts-helper.herokuapp.com/api/fonts/montserrat?download=zip&subsets=latin&variants=100,200,300,500,600,700,800,900,100italic,200italic,300italic,regular,italic,500italic,600italic,700italic,800italic,900italic&formats=woff,woff2",
)

#######################################################################

# save miRBase
import gzip
import re


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

# make package if not importing

import sys

print("Building with Cython...")
if len(sys.argv) > 1:

    from setuptools import setup, Extension
    from Cython.Distutils.build_ext import new_build_ext
    import numpy

    setup(
        ext_modules=[Extension("*", ["src/thtools/*.pyx"])],
        cmdclass={"build_ext": new_build_ext},
        include_dirs=numpy.get_include(),
    )

#######################################################################
