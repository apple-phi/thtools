import pytest

import thtools


def test_api_miR_210():
    """
    Test our iGEM team's toehold switch for hsa-miR-210-3p activates correctly in Acyrthosiphon pisum.

    This species contains an identical miRNA.
    """
    fasta = thtools.FASTA.fromspecies("Acyrthosiphon pisum")
    tc = thtools.autoconfig(
        ths="uuagccgcugucacacgcacagggauuuacaaaaagaggagaguaaaaugcugugcgugcaccauaaaacgaacauagac",
        rbs="agaggaga",
        triggers=fasta.seqs,
    )
    res = tc.run(max_size=3)
    targeted = fasta.IDs[max(range(fasta.num), key=lambda x: res.activations[x])]
    assert targeted == "api-miR-210"
