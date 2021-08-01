import pytest

import thtools as tt


@pytest.fixture(name="hsa_miR_210_3p_crt_result", scope="module")
def _hsa_miR_210_3p_crt_result(hsa_miR_210_3p_thtest):
    return tt.CelsiusRangeTest(hsa_miR_210_3p_thtest, (37, 100)).run(max_size=3)


def test_specificity(hsa_miR_210_3p_crt_result):
    result = hsa_miR_210_3p_crt_result
    assert result.specificity[0] > 0.9 and result.specificity[-1] == 0


def test_activation_result(hsa_miR_210_3p_crt_result):
    result = hsa_miR_210_3p_crt_result
    assert result.activation[0] > 0.6 and result.activation[-1] < 0.1
