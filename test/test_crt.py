import tempfile

import pytest
import scipy.optimize
import numpy as np
from PIL import Image, ImageChops

import thtools as tt


@pytest.fixture(name="hsa_miR_210_3p_crt_result", scope="module")
def _hsa_miR_210_3p_crt_result(hsa_miR_210_3p_thtest):
    return tt.CelsiusRangeTest(hsa_miR_210_3p_thtest, range(10, 100, 10)).run(
        max_size=3, n_samples=100
    )


def test_specificity(hsa_miR_210_3p_crt_result):
    result = hsa_miR_210_3p_crt_result
    assert result.specificity[3] > 0.9 and result.specificity[-1] == 0


def test_activation(hsa_miR_210_3p_crt_result):
    result = hsa_miR_210_3p_crt_result
    assert result.activation[3] > 0.5 and result.activation[-1] < 0.1


def test_target(hsa_miR_210_3p_crt_result):
    result = hsa_miR_210_3p_crt_result
    assert result.inferred_target_name == "hsa-miR-210-3p"


def test_inferred_target_name_setter(hsa_miR_210_3p_crt_result):
    new = hsa_miR_210_3p_crt_result.copy()
    new.inferred_target_name = hsa_miR_210_3p_crt_result.inferred_target_name
    assert new == hsa_miR_210_3p_crt_result


def test_lobf(hsa_miR_210_3p_crt_result):
    """
    Model 10-80°C as a cubic function and compare to LOBF.

    Since the LOBF B-spline is order 3, this should be almost exactly identical.
    """
    plt = hsa_miR_210_3p_crt_result[1:8].plot()
    x_vals, y_spline = plt.gca().lines[-1].get_xydata().T

    def cubic(x, a, b, c, d):
        return a * x ** 3 + b * x ** 2 + c * x + d

    (a, b, c, d), pcov = scipy.optimize.curve_fit(cubic, x_vals, y_spline)
    y_quad = cubic(x_vals, a, b, c, d)

    assert np.allclose(y_spline, y_quad, atol=5)


def test_plot_swap(hsa_miR_210_3p_crt_result):
    plt = hsa_miR_210_3p_crt_result.plot(swap=True)
    x, y = plt.gca().lines[0].get_xydata().T
    assert (
        np.greater_equal(100, y[:7]).all()
        and np.greater_equal(y[:7], 90).all()
        and np.equal(y[8:], 0).all()
    )


def test_getitem(hsa_miR_210_3p_crt_result):
    assert hsa_miR_210_3p_crt_result[0] == hsa_miR_210_3p_crt_result.results[0]


def test_savefig(hsa_miR_210_3p_crt_result):
    # https://stackoverflow.com/questions/35176639/compare-images-python-pil
    tmp1 = tempfile.TemporaryFile(suffix=".png")
    hsa_miR_210_3p_crt_result.savefig(tmp1, dpi=1200)
    tmp2 = tempfile.TemporaryFile(suffix=".png")
    hsa_miR_210_3p_crt_result.plot().savefig(tmp2, dpi=1200)
    with Image.open(tmp1) as im1, Image.open(tmp2) as im2:
        assert not ImageChops.difference(im1, im2).getbbox()
