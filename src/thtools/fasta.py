"""
Parse FASTA files, with built-in access to the mature section of `miRBase <miRBase_>`__.
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

import os
from typing import List, Union, Collection, Optional
import xml.etree.ElementTree as ElementTree
import urllib.request, urllib.error
import logging

from . import HOME

__all__ = ["FParser"]


class iGEMError(Exception):
    """For when something in the iGEM API fails."""


class FParser:
    """
    A basic FASTA parser with `miRBase <https://miRBase.org>`__ built in.

    Extracts main FASTA sub-components. Supports slice syntax and summation.

    Parameters
    ----------
    text : str
        The FASTA text to parse.

    Attributes
    ----------
    ids : List[str]
    seqs : List[str]
    headers : List[str]
    descriptions : List[str]
    num : int
    text : str
    source : set, defaults to set()
    line_length : int, defaults to 70

    Notes
    -----
    Upon instantiation, the :attr:`text` attribute is formatted
    using the :meth:`format` method.

    Examples
    --------
    >>> import thtools as tt
    >>> ths = "UUAGCCGCUGUCACACGCACAGGGAUUUACAAAAAGAGGAGAGUAAAAUGCUGUGCGUGCACCAUAAAACGAACAUAGAC"
    >>> rbs = "AGAGGAGA"
    >>> fasta = tt.FParser.fromspecies("Homo sapiens")[295:305] # slice a small chunk of the database
    >>> triggers = fasta.seqs
    >>> trigger_names = fasta.ids
    >>> my_test = tt.autoconfig(ths, rbs, triggers, names=trigger_names)
    >>> my_result = my_test.run(max_size=3, n_samples=100)
    >>> my_result.specificity
    0.9999981076197236
    """

    ids: List[str]
    seqs: List[str]
    headers: List[str]
    descriptions: List[str]
    num: int
    text: str
    source = set()

    specieslist = sorted(
        i
        for i in [f.split(".")[0] for f in os.listdir(os.path.join(HOME, "miRBase"))]
        if len(i) > 0
    )
    line_length = 70

    def __init__(self, text: str):
        if not text:
            self.num = 0
            return
        text_lines = [
            line.replace(";", ">").strip()
            for line in text.splitlines()
            if len(line) > 0
        ]
        self.headers = [line for line in text_lines if ">" in line]
        self.seqs = "".join(
            [line if ">" not in line else "<split>" for line in text_lines][1:]
        ).split("<split>")
        first_space_indices = [header.index(" ") for header in self.headers]
        self.ids = [
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
            == len(self.ids)
            == len(self.descriptions)
        ), "error in parsing FASTA file."
        self.num = len(self.ids)
        self.text = self.format()

    def __len__(self):
        return self.num

    def __mul__(self, other):
        if isinstance(other, int):
            new = self.copy()
            for _ in range(other - 1):
                new += self
            return new
        else:
            raise NotImplementedError("only scalar multiplication is supported.")

    __rmul__ = __mul__

    def __repr__(self):
        return f"<{self.__module__}.{type(self).__qualname__} of {self.num} {'seqs' if self.num != 1 else 'seq'} at {hex(id(self))}>"

    def __str__(self):
        return self.text

    def __eq__(self, other):
        return (
            self.ids == other.ids
            and self.seqs == other.seqs
            and self.descriptions == other.descriptions
        )

    def __add__(self, other):
        new = self.__new__(type(self))
        new.ids = self.ids + other.ids
        new.seqs = self.seqs + other.seqs
        new.headers = self.headers + other.headers
        new.descriptions = self.descriptions + other.descriptions
        new.num = self.num + other.num
        if self.text[:-1] != "\n":
            self.text += "\n"
        new.text = self.text + other.text
        new.source = self.source | other.source
        return new

    def __getitem__(self, key: Union[int, str, slice]):
        if isinstance(key, slice):
            return self._get_by_slice(key)
        if isinstance(key, int):
            return self._get_by_index(key)
        if isinstance(key, str):
            if key in self.ids:
                return self._get_by_id(key)
            if key in self.seqs:
                return self._get_by_seq(key)
            if key in self.descriptions:
                return self._get_by_desc(key)
            if key in self.headers:
                return self._get_by_header(key)
            raise KeyError(
                f"key '{key}' not found in IDs, sequences, descriptions or headers."
            )

    def _get_by_slice(self, key: slice):
        new = self.copy()
        new.ids = self.ids[key]
        new.seqs = self.seqs[key]
        new.descriptions = self.descriptions[key]
        new.headers = self.headers[key]
        new.num = len(new.ids)
        new.text = new.format()
        return new

    def _get_by_index(self, key: int):
        return (self.ids[key], (self.seqs[key]))

    def _get_by_id(self, key: str):
        return self.seqs[self.ids.index(key)]

    def _get_by_seq(self, key: str):
        return self.ids[self.seqs.index(key)]

    def _get_by_desc(self, key: str):
        index = self.descriptions.index(key)
        return (self.ids[index], (self.seqs[index]))

    def _get_by_header(self, key: str):
        index = self.headers.index(key)
        return (self.ids[index], (self.seqs[index]))

    def index(self, key):
        """Get the index of a key in IDs, sequences, descriptions or headers."""
        if key in self.ids:
            return self.ids.index(key)
        if key in self.seqs:
            return self.seqs.index(key)
        if key in self.descriptions:
            return self.descriptions.index(key)
        if key in self.headers:
            return self.headers.index(key)
        raise KeyError(
            f"key '{key}' not found in IDs, sequences, descriptions or headers."
        )

    # def __setitem__(self, key: str, value: str):
    #     """Set sequence by indexing into any attribute."""
    #     if key in self.ids:
    #         self.seqs[self.ids.index(key)] = value
    #     elif key in self.seqs:
    #         self.ids[self.seqs.index(key)] = value
    #     elif key in self.headers:
    #         self.seqs[self.headers.index(key)] = value
    #     elif key in self.descriptions:
    #         self.seqs[self.descriptions.index(key)] = value
    #     raise KeyError(f"key '{key}' not found in ids, headers or sequences")

    def format(self, line_length: int = line_length) -> str:
        """
        Format the text of a FASTA to be a certain line length in each sequence.

        Parameters
        ----------
        linelength : int, default=FParser.line_length
            The max length of each sequence line.

        Returns
        -------
        str
            The formatted text of the FParser object.
        """
        return "".join(
            f">{self.ids[i]} {self.descriptions[i]}\n{_seq_format(self.seqs[i], line_length)}\n"
            for i in range(self.num)
        ).strip()

    def copy(self):
        """
        Implement copy protocol.

        Returns
        -------
        FParser
            A copy of `self`.
        """
        new = FParser(self.text)
        new.ids = self.ids
        new.seqs = self.seqs
        new.headers = self.headers
        new.descriptions = self.descriptions
        new.num = self.num
        new.source = self.source
        new.line_length = self.line_length
        return new

    @classmethod
    def fromfile(cls, path: str, *args, **kwargs):
        """
        Open a FASTA file and parse it into a :class:`FParser` object.

        Parameters
        ----------
        path : str
            The path to the FASTA file.
        *args
            Any extra arguments to pass to :func:`open`.
        **kwargs
            Any extra keyword arguments to pass to :func:`open`.

        Returns
        -------
        FParser
        """
        with open(path, "r", *args, **kwargs) as f:
            new = cls(f.read())
        new.source.add(path)
        return new

    @classmethod
    def fromspecies(cls, species: str):
        """
        Create a :class:`FParser` instance based on the miRNAs in miRBase.

        Full species list available via :attr:`FParser.specieslist`.

        Parameters
        ----------
        species : str

        Returns
        -------
        FParser
        """
        return cls.fromfile(os.path.join(HOME, "miRBase", f"{species}.fa"))

    @classmethod
    def fromregistry(
        cls,
        part: Optional[str] = None,
        parts: Optional[Collection[str]] = None,
        retries: int = 0,
    ):
        """
        Create a :class:`FParser` instance from a part or list of parts
        in the `Registry of Standard Biological Parts <http://parts.igem.org/Main_Page>`_.

        Parameters
        ----------
        part : str, optional
        parts : Collection[str], optional
        retries : int, default=0

        Returns
        -------
        FParser | list[FParser]

        Raises
        ------
        ValueError
            If neither `part` nor `parts` is supplied.
        """
        if parts:
            if part:
                parts.append(part)
                logging.info("both `part` and `parts` supplied to `fromregsitry`.")
        elif part:
            parts = [part]
        else:
            raise ValueError(
                "at least one of the arguments `part` or `parts` must be passed."
            )
        url = "https://parts.igem.org/cgi/xml/part.cgi?part=" + ".".join(parts)
        try:
            return cls._fromigemxml(parts, urllib.request.urlopen(url).read().decode())
        except urllib.error.URLError as e:
            if retries > 0:
                logging.warning(
                    "Connection to %s timed out. Retrying %s more times.",
                    url,
                    retries,
                )
                return cls.fromregistry(parts=parts, retries=retries - 1)
            raise iGEMError(f"connection to {url} timed out. No more retries.") from e

    @classmethod
    def _fromigemxml(cls, parts, xml_text: str):
        """Parse the return value from the iGEM API."""
        assert "error" not in xml_text.lower()
        root = ElementTree.fromstring(xml_text)
        new = cls("")
        new.ids = parts
        new.descriptions = [tag.text for tag in root.findall(".//part_short_desc")]
        new.seqs = [tag.text for tag in root.findall(".//seq_data")]
        new.num = len(parts)
        return cls(new.format())


def _seq_format(seq, seq_width: int) -> str:
    """Internal sequence formatter to set sequences to a certain length."""
    return "".join(
        seq[i] if (i + 1) % seq_width != 0 or i == len(seq) - 1 else f"{seq[i]}\n"
        for i in range(len(seq))
    )
