import importlib
from setuptools import setup, Extension

from Cython.Distutils.build_ext import new_build_ext
import numpy

importlib.import_module("setup_assets")

print("Building with Cython...")
setup(
    ext_modules=[Extension("*", ["src/thtools/*.pyx"])],
    cmdclass={"build_ext": new_build_ext},
    include_dirs=numpy.get_include(),
)
