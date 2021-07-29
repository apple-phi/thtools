import thtools


def test_hsa_miR_210_3p():
    """
    Test our iGEM team's toehold switch for hsa-miR-210-3p activates correctly.
    """
    fasta = thtools.FParser.fromspecies("Homo sapiens")
    tc = thtools.autoconfig(
        ths="uuagccgcugucacacgcacagggauuuacaaaaagaggagaguaaaaugcugugcgugcaccauaaaacgaacauagac",
        rbs="agaggaga",
        triggers=fasta.seqs[135:145],
        names=fasta.ids[135:145],
    )
    res = tc.run(max_size=3)
    assert res.target_name == fasta[res.target] == "hsa-miR-210-3p"
