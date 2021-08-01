import pytest
import thtools as tt


@pytest.fixture(name="hsa_fasta_slice", scope="module")
def _hsa_fasta_slice():
    return tt.FParser.fromspecies("Homo sapiens")[295:305]


@pytest.fixture(name="hsa_miR_210_3p_thtest", scope="module")
def _hsa_miR_210_3p_thtest(hsa_fasta_slice):
    thtest = tt.autoconfig(
        ths="UUAGCCGCUGUCACACGCACAGGGAUUUACAAAAAGAGGAGAGUAAAAUGCUGUGCGUGCACCAUAAAACGAACAUAGAC",
        rbs="AGAGGAGA",
        triggers=hsa_fasta_slice.seqs,
        names=hsa_fasta_slice.ids,
    )
    return thtest
