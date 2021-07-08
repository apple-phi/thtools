"""Initialize pkg."""

import os
HOME = os.path.dirname(os.path.abspath(__file__))

from .analysis import ToeholdTest # not confidence_interval
from .utility import autoconfig, FASTA, find_rbs # not combs
from . import demos, _meta
