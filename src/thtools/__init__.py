"""
A library for the analysis of toehold switch riboregulators
created by the iGEM team City of London UK 2021.
"""

# This file is part of ToeholdTools (a library for the analysis of
# toehold switch riboregulators created by the iGEM team City of
# London UK 2021).
# Copyright (c) 2021 Lucas Ng

# ToeholdTools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# ToeholdTools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with ToeholdTools.  If not, see <https://www.gnu.org/licenses/>.

__version__ = "0.3.0"

import os
import nupack

HOME = os.path.dirname(os.path.abspath(__file__))
CPU_COUNT = os.cpu_count()

nupack.config.cache = 0.01  # 10MB
nupack.config.parallelism = True

from .core import *
from .crt import *
from .utils import *
from .fasta import *
