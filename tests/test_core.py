"""核心模块测试"""

import pytest
from mechcalc.core.units import (
    kg, mm, m, MPa, N, rpm, kg_m2, Q_,
    to_mag, to_unit, ensure_quantity, ensure_float,
    NESTED_UNITS, FLAT_UNITS,
)
from mechcalc.utils.result import Result, calc_batch, to_result


class TestUnits:
    def test_kg(self):
        q = kg(10)
        assert to_mag(q) == 10.0
        assert to_unit(q) == 'kg'

    def test_mm_to_m(self):
        q = mm(100)
        assert to_mag(q, 'm') == 0.1

    def test_MPa(self):
        q = MPa(0.5)
        assert to_mag(q) == 0.5
        assert to_unit(q) == 'MPa'

    def test_ensure_quantity(self):
        q1 = ensure_quantity(10, 'mm')
        assert to_mag(q1) == 10.0
        q2 = ensure_quantity(Q_(10, 'mm'), 'm')
        assert to_mag(q2) == 0.01

    def test_ensure_float(self):
        assert ensure_float(10) == 10.0
        assert ensure_float(Q_(10, 'mm'), 'm') == 0.01

    def test_nested_units(self):
        assert '质量' in NESTED_UNITS
        assert 'kg' in NESTED_UNITS['质量']

    def test_flat_units(self):
        assert 'kg' in FLAT_UNITS
        assert 'MPa' in FLAT_UNITS


class TestResult:
    def test_dict_access(self):
        r = Result(params={'a': 1}, results={'b': 2})
        assert r['b'] == 2

    def test_attr_access(self):
        r = Result(params={'a': 1}, results={'b': 2})
        assert r.b == 2
        assert r.params == {'a': 1}

    def test_to_api(self):
        r = Result(params={'a': 1}, results={'b': 2})
        d = r.to_api()
        assert d['params'] == {'a': 1}
        assert d['b'] == 2

    def test_repr(self):
        r = Result(params={'a': 1}, results={'b': 2})
        assert 'Result' in repr(r)


class TestToResult:
    def test_params_recorded(self):
        from mechcalc.inertia import solid_cylinder
        r = to_result(solid_cylinder, 10, 100)
        assert r.params['mass'] == {'value': 10.0, 'unit': 'kg'}
        assert r.value['unit'] == 'kg·m²'

    def test_default_param_recorded(self):
        from mechcalc.pneumatic import push_force
        r = to_result(push_force, 0.4, 32)
        assert r.params['efficiency'] == 0.85  # 默认值也被记录

    def test_kwargs(self):
        from mechcalc import motor_calc
        r = to_result(motor_calc, load_torque=5.0, load_speed=1400)
        assert abs(r.required_power['value'] - 879.6459430) < 1e-6

    def test_quantity_param(self):
        from mechcalc.inertia import solid_cylinder
        r = to_result(solid_cylinder, Q_(10, 'kg'), 100)
        assert r.params['mass'] == {'value': 10.0, 'unit': 'kg'}

    def test_json_safe(self):
        import json
        from mechcalc import motor_calc, solid_cylinder_tensor
        json.dumps(to_result(motor_calc, 5.0, 1400).to_api())
        json.dumps(to_result(solid_cylinder_tensor, 10, 100, 200).to_api())


class TestCalcBatch:
    def test_batch_success(self):
        from mechcalc.inertia import solid_cylinder
        cases = [
            {'mass': 10, 'outer_diameter': 100},
            {'mass': 20, 'outer_diameter': 200},
        ]
        results = calc_batch(solid_cylinder, cases)
        assert len(results) == 2
        assert 'value' in results[0]

    def test_batch_error(self):
        from mechcalc.inertia import solid_cylinder
        cases = [
            {'mass': 10, 'outer_diameter': 100},
            {'mass': -10, 'outer_diameter': 100},  # 负数质量
        ]
        results = calc_batch(solid_cylinder, cases)
        assert len(results) == 2
