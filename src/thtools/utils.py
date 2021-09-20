"""
Definitions of ToeholdTools utility functions and objects.
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

import itertools
from typing import Collection, Optional

import numpy as np
import nupack

from .core import ToeholdTest


__all__ = ["ASSUMED_STRAND_CONC", "autoconfig", "find_rbs", "ModelNu3"]

ASSUMED_STRAND_CONC: float = 1e-7
"""
A molarity of 100nM.

This concentration is used for all strands in the :func:`autoconfig` function.
This follows the example of Alex Green :cite:p:`green_toehold_2014`.
"""


################################################################################


def autoconfig(
    ths: str,
    rbs: str,
    triggers: Collection[str],
    set_size: int = 1,
    model: nupack.Model = nupack.Model(),
    names: Optional[Collection[str]] = None,
    const_rna: Optional[str] = None,
) -> ToeholdTest:
    """
    Quick configuration of ToeholdTests,
    assuming every RNA has the concentration of
    :attr:`thtools.utils.ASSUMED_STRAND_CONC`.

    Parameters
    ----------
    ths : str
        The toehold switch
    rbs : str
        The ribosome binding site whose slice of the toehold switch will be autodetected
    triggers : Collection[str]
        An array-like of the triggers to test the toehold switch against
    set_size : int, default=1
        How many triggers to test combinatorically against the toehold switch at a time.
    model : nupack.Model, default=nupack.Model()
        The thermodynamic model to use.
    names : Collection[str], optional
        The names of each trigger.
    const_rna : Iterable, optional
        A list of any constant RNAs.

    Returns
    -------
    A fully configured :class:`~thtools.core.ToeholdTest` instance.

    Examples
    --------
    >>> import thtools as tt
    >>> ths = "UUAGCCGCUGUCACACGCACAGGGAUUUACAAAAAGAGGAGAGUAAAAUGCUGUGCGUGCACCAUAAAACGAACAUAGAC"
    >>> rbs = "AGAGGAGA"
    >>> triggers = ["CUGUGCGUGUGACAGCGGCUGA", "CUAUACAAUCUACUGUCUUUCC", "UGUACAGCCUCCUAGCUUUCC"]
    >>> my_test = tt.autoconfig(ths, rbs, triggers)
    >>> my_result = my_test.run(max_size=3, n_samples=100)
    >>> my_result.specificity # gives as decimal, not percentage
    0.9999999587733204
    """
    rbs_slice = find_rbs(ths, rbs)
    trigger_sets = _combs(triggers, set_size)
    conc_sets = np.full(trigger_sets.shape, ASSUMED_STRAND_CONC, dtype=np.float64)
    if not const_rna:
        const_rna = {}
    else:
        const_rna = {rna: ASSUMED_STRAND_CONC for rna in const_rna}
    t = ToeholdTest(
        ths=ths,
        ths_conc=ASSUMED_STRAND_CONC,
        rbs_slice=rbs_slice,
        trigger_sets=trigger_sets,
        conc_sets=conc_sets,
        const_rna=const_rna,
        model=model,
    )
    if names is not None and len(names) > 0:
        assert len(names) == len(
            triggers
        ), "each name must match to a corresponding trigger. Set to [] otherwise."
        names = _combs(names, set_size)
        t.names = names
    return t


################################################################################


def _combs(a: Collection, r: int) -> np.ndarray:
    """
    Return successive r-length combinations of elements in the array a.

    Should produce the same output as array(list(combinations(a, r))), but
    faster.
    ^ from https://stackoverflow.com/questions/16003217/n-d-version-of-itertools-combinations-in-numpy
    """
    a = np.array(a)
    dt = np.dtype([("", a.dtype)] * r)
    b = np.fromiter(itertools.combinations(a, r), dt)
    return b.view(a.dtype).reshape(-1, r)


################################################################################


def find_rbs(ths: str, rbs: str, mult_check: bool = False) -> slice:
    """
    Get the slice the RBS occupies in a toehold switch sequence.

    Parameters
    ----------
    ths : str
        The toehold switch sequence.
    rbs : str
        The ribosome binding site sequence.
    mult_check : bool, default = False
        Whether to raise an error if multiple RBS sequences are found.

    Examples
    --------
    >>> import thtools as tt
    >>> ths = "UUAGCCGCUGUCACACGCACAGGGAUUUACAAAAAGAGGAGAGUAAAAUGCUGUGCGUGCACCAUAAAACGAACAUAGAC"
    >>> rbs = "AGAGGAGA"
    >>> tt.find_rbs(ths, rbs)
    slice(34, 42, None)
    """
    ths = ths.upper()
    rbs = rbs.upper()
    if mult_check:
        assert ths.count(rbs) <= 1, "multiple RBSs found."
    i = ths.rindex(rbs)
    return slice(i, i + len(rbs))


################################################################################


@nupack.rebind.forward  # make the class available to the nupack C++ API
class ModelNu3(nupack.Model):
    """
    Class to emulate the behaviour of NUPACK v3.

    A thermodynamic model subclassing :class:`nupack.Model`
    which mimics the `NUPACK website <https://nupack.org>`_ .

    Parameters
    ----------
    wobble : bool, optional
    kelvin : float, optional
    celsius : float, optional, default = 37
    sodium : float, default = 1.0
    magnesium : float, default = 0.0

    Examples
    --------
    >>> import thtools as tt
    >>> ths = "UUAGCCGCUGUCACACGCACAGGGAUUUACAAAAAGAGGAGAGUAAAAUGCUGUGCGUGCACCAUAAAACGAACAUAGAC"
    >>> rbs = "AGAGGAGA"
    >>> triggers = ["CUGUGCGUGUGACAGCGGCUGA", "CUAUACAAUCUACUGUCUUUCC", "UGUACAGCCUCCUAGCUUUCC"]
    >>> model = tt.ModelNu3(celsius=21.0)
    >>> my_test = tt.autoconfig(ths, rbs, triggers, model=model)
    >>> my_result = my_test.run(max_size=3, n_samples=100)
    >>> my_result.specificity # gives as decimal, not percentage
    1.0
    """

    def __new__(cls, wobble=None, kelvin=None, celsius=37, sodium=1.0, magnesium=0.0):
        return nupack.Model.__new__(
            cls,
            ensemble="some-nupack3",
            material="rna95-nupack3",
            wobble=wobble,
            kelvin=kelvin,
            celsius=celsius,
            sodium=sodium,
            magnesium=magnesium,
        )

    def __init__(self, wobble=None, kelvin=None, celsius=37, sodium=1.0, magnesium=0.0):
        super().__init__(
            ensemble="some-nupack3",
            material="rna95-nupack3",
            wobble=wobble,
            kelvin=kelvin,
            celsius=celsius,
            sodium=sodium,
            magnesium=magnesium,
        )


################################################################################
