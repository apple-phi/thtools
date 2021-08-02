import pytest

import thtools as tt


@pytest.fixture(name="hsa_miR_210_3p_crt_result", scope="module")
def _hsa_miR_210_3p_crt_result(hsa_miR_210_3p_thtest):
    return tt.CelsiusRangeTest(hsa_miR_210_3p_thtest, range(10, 100, 10)).run(
        max_size=3, n_samples=100
    )


def test_crt_specificity(hsa_miR_210_3p_crt_result):
    result = hsa_miR_210_3p_crt_result
    assert result.specificity[3] > 0.9 and result.specificity[-1] == 0


def test_crt_activation(hsa_miR_210_3p_crt_result):
    result = hsa_miR_210_3p_crt_result
    assert result.activation[3] > 0.6 and result.activation[-1] < 0.1


def test_crt_target(hsa_miR_210_3p_crt_result):
    result = hsa_miR_210_3p_crt_result
    assert result.inferred_target_name == "hsa-miR-210-3p"
