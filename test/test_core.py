def test_run_generate(hsa_miR_210_3p_thtest, hsa_fasta_slice):
    """
    Test that ToeholdTools detects the target for one of
    our iGEM team's toehold switches (hsa-miR-210-3p)
    via both the run and generate methods.
    """
    thtest1 = hsa_miR_210_3p_thtest.copy()
    thtest2 = thtest1.copy()
    res1 = thtest1.run(max_size=3)
    for _ in thtest2.generate(max_size=3):
        pass
    res2 = thtest2.result
    assert (
        res1.target_name
        == res2.target_name
        == hsa_fasta_slice[res1.target]
        == hsa_fasta_slice[res2.target]
        == "hsa-miR-210-3p"
    )


def test_run(hsa_miR_210_3p_thtest):
    """
    Test that both the run method and the
    result attribute return the same thing.
    """
    thtest = hsa_miR_210_3p_thtest.copy()
    assert thtest.run(max_size=3) == thtest.result


def test_aug(hsa_miR_210_3p_thtest):
    """Test that the AUG is detected to be in the correct place."""
    thtest = hsa_miR_210_3p_thtest.copy()

    # arbitrary values needed for _setup
    thtest.max_size = 100
    thtest.n_samples = 100
    thtest.n_nodes = 100
    thtest.n_chunks = 100
    thtest._setup()

    # this is safe since the switch only has one AUG trigram
    assert thtest.aug_position == thtest.ths.index("AUG")
