import nupack
import numpy as np

import thtools as tt


def test_autoconfig(hsa_miR_210_3p_thtest, hsa_fasta_slice):
    ths = "UUAGCCGCUGUCACACGCACAGGGAUUUACAAAAAGAGGAGAGUAAAAUGCUGUGCGUGCACCAUAAAACGAACAUAGAC"
    ths_conc = tt.ASSUMED_STRAND_CONC
    rbs_slice = tt.find_rbs(ths, "AGAGGAGA")
    trigger_sets = np.array(hsa_fasta_slice.seqs).reshape(hsa_fasta_slice.num, 1)
    conc_sets = np.full((hsa_fasta_slice.num, 1), tt.ASSUMED_STRAND_CONC)
    names = np.array(hsa_fasta_slice.ids).reshape(hsa_fasta_slice.num, 1)
    manual_thtest = tt.ToeholdTest(
        ths, ths_conc, rbs_slice, trigger_sets, conc_sets, names=names
    )
    assert manual_thtest == hsa_miR_210_3p_thtest


def test_autoconfig_with_const_rna(hsa_fasta_slice):
    thtest = tt.autoconfig(
        ths="", rbs="", triggers=hsa_fasta_slice.seqs, const_rna=["A"]
    )
    assert thtest.const_rna == {"A": tt.ASSUMED_STRAND_CONC}


def test_find_rbs():
    assert tt.find_rbs("AAGGUCACC", "GGU", mult_check=True) == slice(2, 5)


def test_ModelNu3():
    assert str(tt.ModelNu3().to_json()) == str(
        nupack.Model(ensemble="some-nupack3", material="rna95-nupack3").to_json()
    )
