import thtools as tt


def test_FParser_methods(hsa_fasta_slice):
    """Run a series of random operations and check that it stays true to the original FASTA."""
    new_fasta = tt.FParser(hsa_fasta_slice.format(line_length=1)).copy()[::-1]
    new_fasta += new_fasta
    assert (
        new_fasta["hsa-miR-210-3p"]
        == hsa_fasta_slice.seqs[::-1][new_fasta.index("hsa-miR-210-3p")]
    )
