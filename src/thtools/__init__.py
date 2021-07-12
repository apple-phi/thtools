"""A library for the analysis of toehold switch riboregulators."""

__version__ = "0.0.2"

import os

HOME = os.path.dirname(os.path.abspath(__file__))
ASC = 1e-7  # Assumed Strand Concentration = 100nM, following the example of A. Green [doi: 10.1016/j.cell.2014.10.002]

from .analysis import ToeholdTest  # not confidence_interval
from .utility import autoconfig, FASTA, find_rbs  # not _combs
from . import demos
