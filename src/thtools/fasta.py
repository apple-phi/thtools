"""A sub-module to parse FASTA files, which comes with the mature section of miRBase included."""

import os
from typing import List, Union

from . import HOME


class FParser:
    """
    A basic FASTA parser with `miRBase <https://www.mirbase.org>`_ built in.

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
        [
            i
            for i in [
                f.split(".")[0] for f in os.listdir(os.path.join(HOME, "miRBase"))
            ]
            if len(i) > 0
        ]
    )
    line_length = 70

    def __init__(self, text: str):
        text_lines = [
            line.replace(";", ">") for line in text.splitlines() if len(line) > 0
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

    def __repr__(self):
        return f"<{self.__module__}.{type(self).__qualname__} of {self.num} seqs at {hex(id(self))}>"

    def __str__(self):
        return self.text

    def __getitem__(self, key: Union[int, str, slice]):
        if isinstance(key, slice):
            new = self.copy()
            new.ids = self.ids[key]
            new.seqs = self.seqs[key]
            new.descriptions = self.descriptions[key]
            new.num = len(new.ids)
            new.text = new.format()
            return new

        if isinstance(key, int):
            return (self.ids[key], (self.seqs[key]))

        if isinstance(key, str):

            if key in self.ids:
                return self.seqs[self.ids.index(key)]
            if key in self.seqs:
                return self.ids[self.seqs.index(key)]

            if key in self.descriptions:
                index = self.descriptions.index(key)
                return (self.ids[index], (self.seqs[index]))
            if key in self.headers:
                index = self.headers.index(key)
                return (self.ids[index], (self.seqs[index]))

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

    def format(self, linelength: int = line_length) -> str:
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
            [
                f">{self.ids[i]} {self.descriptions[i]}\n{self._seq_format(self.seqs[i], linelength)}\n"
                for i in range(self.num)
            ]
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

    @staticmethod
    def _seq_format(seq, seq_width: int) -> str:
        """Internal sequence formatter to set sequences to a certain length."""
        return "".join(
            [
                seq[i]
                if (i + 1) % seq_width != 0 or i == len(seq) - 1
                else f"{seq[i]}\n"
                for i in range(len(seq))
            ]
        )
