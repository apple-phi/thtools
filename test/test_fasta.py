import thtools as tt


def test_copy(hsa_fasta_slice):
    assert hsa_fasta_slice.copy() == hsa_fasta_slice


def test_format(hsa_fasta_slice):
    assert tt.FParser(hsa_fasta_slice.format(line_length=1)) == hsa_fasta_slice


def test_index(hsa_fasta_slice):
    assert (
        hsa_fasta_slice["hsa-miR-210-3p"]
        == hsa_fasta_slice[::-1][
            len(hsa_fasta_slice) - hsa_fasta_slice.index("hsa-miR-210-3p") - 1
        ][1]
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
