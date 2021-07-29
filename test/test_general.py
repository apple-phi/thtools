import thtools


def test_hsa_miR_210_3p():
    """
    Test our iGEM team's toehold switch for hsa-miR-210-3p activates correctly.
    """
    fasta = thtools.FParser.fromspecies("Homo sapiens")[295:305]
    tc = thtools.autoconfig(
        ths="uuagccgcugucacacgcacagggauuuacaaaaagaggagaguaaaaugcugugcgugcaccauaaaacgaacauagac",
        rbs="agaggaga",
        triggers=fasta.seqs,
        names=fasta.ids,
    )
    res = tc.run(max_size=3)
    assert res.target_name == fasta[res.target] == "hsa-miR-210-3p"
