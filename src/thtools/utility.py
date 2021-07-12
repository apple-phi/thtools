import os
import itertools
from typing import Collection, Iterable, Optional

import numpy as np
import nupack

from . import HOME, ASC, ToeholdTest


def autoconfig(
    ths: str,
    rbs: str,
    triggers: Collection[str],
    names: Optional[Collection[str]] = None,
    const_rna: Optional[Iterable[str]] = None,
    set_size: int = 1,
    model: nupack.Model = nupack.Model(),
) -> ToeholdTest:
    """
    Quick configuration of ToeholdTests, assuming every RNA has the same concentration.

    Args:
        ths (str): the toehold switch
        rbs (str): the ribosome binding site whose position in the ths will be autodetected
        triggers (list): an array-like of the triggers to test the ths against
        set_size (int, optional): how many triggers to test against the ths at a time. Defaults to 1.
        const_rna (list, optional): a list of any constant RNAs. Defaults to [].
        names (list, optional): the names of each trigger. Defaults to [].
        model (nupack.Model, optional): the physical model to use. Defaults to nupack.Model().

    Returns:
        a fully configured ToeholdTest instance
    """
    rbs_position = find_rbs(ths, rbs)
    trigger_sets = _combs(triggers, set_size)
    conc_sets = np.full(trigger_sets.shape, ASC, dtype=np.float64)
    if const_rna is None:
        const_rna = {}
    else:
        const_rna = {rna: ASC for rna in const_rna}
    t = ToeholdTest(
        ths={ths: ASC},
        rbs_position=rbs_position,
        trigger_sets=trigger_sets,
        conc_sets=conc_sets,
        const_rna=const_rna,
        model=model,
    )
    if names is not None:
        if len(names) > 0:
            assert len(names) == len(
                triggers
            ), "each name must match to a corresponding trigger. Set to [] otherwise."
            names = _combs(names, set_size)
            t.names = names
    return t


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


class FASTA(object):

    """A basic FASTA parser which holds the data in RAM to be easily passed to ToeholdTest instances."""

    specieslist = sorted(
        [
            i
            for i in [f.split(".")[0] for f in os.listdir(f"{HOME}/miRBase/")]
            if len(i) > 0
        ]
    )
    _linelength = 70

    def __init__(self, txt: str):
        """Parse FASTA from text."""
        txt_lines = [line for line in txt.splitlines() if len(line) > 0]
        self.headers = [line for line in txt_lines if ">" in line]
        self.seqs = "".join(
            [line if ">" not in line else "<split>" for line in txt_lines][1:]
        ).split("<split>")

        first_space_indices = [header.index(" ") for header in self.headers]
        self.IDs = [
            self.headers[i][1 : first_space_indices[i]]
            for i in range(len(self.headers))
        ]
        self.descriptions = [
            self.headers[i][first_space_indices[i] + 1 :]
            for i in range(len(self.headers))
        ]

        assert (
            len(self.headers)
            == len(self.seqs)
            == len(self.IDs)
            == len(self.descriptions)
        ), "error in parsing FASTA."

        self.num = len(self.IDs)
        self.txt = txt
        self.source = set()

    def __repr__(self):
        """Edit __repr__ to include # of seqs."""
        return f"<{self.__module__}.{type(self).__qualname__} of {self.num} seqs at {hex(id(self))}>"

    def __str__(self):
        """Access original text."""
        return self.txt

    def __getitem__(self, key: str):
        """Index by ID, header or sequence to obtain sequence (or ID if indexing by sequence)."""
        if key in self.IDs:
            return self.seqs[self.IDs.index(key)]
        elif key in self.seqs:
            return self.IDs[self.seqs.index(key)]
        elif key in self.headers:
            return self.seqs[self.headers.index(key)]
        raise KeyError(f"key '{key}' not found in IDs, headers or sequences")

    def __setitem__(self, key: str, value: str):
        """Index by ID, header or sequence to set sequence (or ID if indexing by sequence)."""
        if key in self.IDs:
            self.seqs[self.IDs.index(key)] = value
        elif key in self.seqs:
            self.IDs[self.seqs.index(key)] = value
        elif key in self.headers:
            self.seqs[self.headers.index(key)] = value
        raise KeyError(f"key '{key}' not found in IDs, headers or sequences")

    def __add__(self, other):
        """FASTA summation."""
        new = self.__new__(type(self))
        new.headers = self.headers + other.headers
        new.seqs = self.seqs + other.seqs
        new.IDs = self.IDs + other.IDs
        new.descriptions = self.descriptions + other.descriptions
        new.num = self.num + other.num

        if self.txt[:-1] != "\n":
            self.txt += "\n"
        new.txt = self.txt + other.txt
        new.source = self.source | other.source
        return new

    def format(self, linelength: int = _linelength) -> str:
        """Format the text of a FASTA to be a certain line length in each sequence."""
        return "".join(
            [
                f">{self.IDs[i]} {self.descriptions[i]}\n{self.seq_format(self.seqs[i], linelength)}\n"
                for i in range(self.num)
            ]
        )

    @classmethod
    def fromfile(cls, filename: str):
        """Parse a FASTA file into a FASTA object."""
        with open(filename, "r") as f:
            new = cls(f.read())
        new.source.add(filename)
        return new

    @classmethod
    def fromspecies(cls, species: str):
        """
        Create a FASTA instance based on the MiRNAs in the database.

        Full species list available via FASTA.specieslist
        """
        return cls.fromfile(f"{HOME}/miRBase/{species}.fa")

    @staticmethod
    def seq_format(seq, seq_width: int = 70) -> str:
        """Internal sequence formatter to a certain length."""
        return "".join(
            [
                seq[i]
                if (i + 1) % seq_width != 0 or i == len(seq) - 1
                else f"{seq[i]}\n"
                for i in range(len(seq))
            ]
        )


def find_rbs(ths: str, rbs: str, mult_check: bool = False) -> slice:
    """Get the slice position of a rbs sequence in a long ths sequence."""
    ths = ths.upper()
    rbs = rbs.upper()
    if mult_check:
        assert ths.count(rbs) <= 1, "multiple RBSs found."
    i = ths.rindex(rbs)
    return slice(i, i + len(rbs))
