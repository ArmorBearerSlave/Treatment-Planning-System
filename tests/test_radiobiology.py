import math

import numpy as np

from importlib.util import module_from_spec, spec_from_file_location


MODULE_PATH = "app/cornerstone-tps/dosepred-service/radiobiology.py"
SPEC = spec_from_file_location("radiobiology", MODULE_PATH)
radiobiology = module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(radiobiology)



def test_lq_survival_matches_definition():
    expected = math.exp(-(0.2 * 2.0 + 0.03 * 2.0**2))
    actual = radiobiology.lq_survival(np.array([2.0]), 0.2, 0.03)[0]
    assert math.isclose(actual, expected)



def test_cumulative_survival_applies_fraction_count():
    single = radiobiology.lq_survival(np.array([2.0]), 0.2, 0.03)[0]
    cumulative = radiobiology.cumulative_survival(np.array([2.0]), 0.2, 0.03, 5)[0]
    assert math.isclose(cumulative, single**5)



def test_poisson_tcp_uses_expected_surviving_clonogens():
    assert math.isclose(radiobiology.poisson_tcp(0.1, 10.0), math.exp(-1.0))



def test_eud_and_lkb_ntcp():
    dose = np.array([10.0, 20.0, 30.0, 40.0])
    mask = np.array([True, True, False, False])
    assert math.isclose(radiobiology.equivalent_uniform_dose(dose, mask, 1.0), 15.0)
    assert math.isclose(radiobiology.lkb_ntcp(50.0, 50.0, 0.2, 1.0), 0.5)



def test_rbe_scales_biologic_dose():
    physical = radiobiology.lq_survival(np.array([2.0]), 0.2, 0.03, rbe=1.0)[0]
    rbe_scaled = radiobiology.lq_survival(np.array([2.0]), 0.2, 0.03, rbe=1.1)[0]
    assert rbe_scaled < physical
