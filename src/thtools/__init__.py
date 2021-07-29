"""
A library for the analysis of toehold switch riboregulators
created by the iGEM team City of London UK 2021.
"""

__version__ = "0.1.0"

import os

HOME = os.path.dirname(os.path.abspath(__file__))
CPU_COUNT = os.cpu_count()

from .core import *
from .crt import *
from .utils import *
from .fasta import *
