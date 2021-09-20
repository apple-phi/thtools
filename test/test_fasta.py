import unittest.mock
import urllib.request, urllib.error

import thtools as tt
from thtools.fasta import iGEMError


def test_copy(hsa_fasta_slice):
    assert hsa_fasta_slice.copy() == hsa_fasta_slice


def test_format(hsa_fasta_slice):
    assert tt.FParser(hsa_fasta_slice.format(line_length=1)) == hsa_fasta_slice


def test_index_by_id(hsa_fasta_slice):
    assert (
        hsa_fasta_slice["hsa-miR-210-3p"]
        == hsa_fasta_slice[::-1][
            len(hsa_fasta_slice) - hsa_fasta_slice.index("hsa-miR-210-3p") - 1
        ][1]
        == "CUGUGCGUGUGACAGCGGCUGA"
    )


def test_index_by_seq(hsa_fasta_slice):
    assert hsa_fasta_slice["CUGUGCGUGUGACAGCGGCUGA"] == "hsa-miR-210-3p"


def test_getitem_by_description_or_header(hsa_fasta_slice):
    index_210_3p = hsa_fasta_slice.index("CUGUGCGUGUGACAGCGGCUGA")
    assert (
        hsa_fasta_slice[hsa_fasta_slice.descriptions[index_210_3p]]
        == hsa_fasta_slice[hsa_fasta_slice.headers[index_210_3p]]
        == ("hsa-miR-210-3p", "CUGUGCGUGUGACAGCGGCUGA")
    )


def test_index_by_description_or_header(hsa_fasta_slice):
    assert (
        hsa_fasta_slice[
            hsa_fasta_slice.index(
                ">hsa-miR-210-3p MIMAT0000267 Homo sapiens miR-210-3p"
            )
        ]
        == hsa_fasta_slice[
            hsa_fasta_slice.index("MIMAT0000267 Homo sapiens miR-210-3p")
        ]
        == ("hsa-miR-210-3p", "CUGUGCGUGUGACAGCGGCUGA")
    )


def test_add(hsa_fasta_slice):
    twice = hsa_fasta_slice.copy() + hsa_fasta_slice.copy()
    assert (twice)[: int(len(twice) / 2)] == hsa_fasta_slice


def test_fromregistry():
    assert (
        tt.FParser.fromregistry(part="BBa_K2206001") * 2
        == tt.FParser(
            """
        >BBa_K2206001 Toehold switch for hsa-miR-27b-3p
        gcagaacttagccactgtgaaggatttacaaaaagaggagagtaaaatgttcacagtgaacctggcggcagcgcaaaag
        """
            * 2
        )
        == tt.FParser.fromregistry(part="BBa_K2206001", parts=["BBa_K2206001"])
    )


def test_iGEMError():
    with unittest.mock.patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.URLError(""),
        return_value=None,
    ):
        try:
            tt.FParser.fromregistry("BBa_K2206001", retries=10)
        except iGEMError:
            assert True
