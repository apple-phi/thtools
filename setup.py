# python3 setup.py sdist bdist_wheel

from setuptools import find_packages, setup, Extension

import numpy as np


with open("README.md", "r") as f:
    long_description = f.read()
    
meta = {}
with open("thtools/_meta.py") as f:
    exec(f.read(), meta)
    
try:
    from Cython.Build import cythonize, build_ext
    ext_modules=cythonize([
        Extension("*", ["thtools/*.pyx"])
    ])
except ImportError:
    from distutils.command.build_ext import build_ext
    ext_modules=[
        Extension("*", ["thtools/*.c"])
    ]

setup(
    name="thtools",
    version=meta["__version__"],
    author="Lucas Ng",
    author_email="lkn849@gmail.com",
    description="A library for the analysis of toehold switch riboregulators.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
    ],
    # url="",
    packages=find_packages(),
    python_requires=">=3.7",
    ext_modules=ext_modules,
    cmdclass={'build_ext': build_ext},
    include_dirs=np.get_include(),
    install_requires=[
        "eel>=0.14.0",
        "nupack>=4.0.0",
        "pathos>=0.2.8",
        "prettytable>=2.1.0",
        "psutil>=5.8.0",
    ],
    include_package_data=True,
)
