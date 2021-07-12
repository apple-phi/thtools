# save miRBase
import urllib.request
import gzip
import os
import shutil

print("Saving miRBase...")
try:
    os.mkdir("src/thtools/miRBase/")
except FileExistsError:
    shutil.rmtree("src/thtools/miRBase/", ignore_errors=True)
    os.mkdir("src/thtools/miRBase/")
with urllib.request.urlopen(
    "ftp://mirbase.org/pub/mirbase/CURRENT/mature.fa.gz"
) as gzipped_f:
    with gzip.GzipFile(fileobj=gzipped_f) as f:
        txt = f.read().decode()
lines = txt.splitlines()
chunks = ["\n".join(lines[n : n + 2]) for n in range(0, len(lines), 2)]
miRNA_by_species = {}
for chunk in chunks:
    species = " ".join(chunk.split()[2:4])
    if species in miRNA_by_species:
        miRNA_by_species[species].append(chunk)
    else:
        miRNA_by_species[species] = [chunk]
for species, species_chunks in miRNA_by_species.items():
    with open("src/thtools/miRBase/" + species + ".fa", "w") as f:
        txt = "\n".join(species_chunks)
        f.write(txt)

#######################################################################

# make package
from setuptools import setup, Extension
from Cython.Distutils.build_ext import new_build_ext
import numpy

setup(
    ext_modules=[Extension("*", ["src/thtools/*.pyx"])],
    cmdclass={"build_ext": new_build_ext},
    include_dirs=numpy.get_include(),
)
