"""电机需求参数计算测试"""

import math
from mechcalc import motor_calc
from mechcalc.core.units import to_mag
from mechcalc import to_result


class TestMotorCalc:
    def test_basic(self):
        raw = motor_calc(5.0, 1400)
        # T_req = 5.0 * 1.2 = 6.0 N·m
        assert abs(to_mag(raw['required_torque'], 'N*m') - 6.0) < 1e-9
        assert abs(to_mag(raw['required_speed'], 'rpm') - 1400.0) < 1e-9
        # P = 6.0 * 2π * 1400 / 60 ≈ 879.6 W
        expected_P = 6.0 * 2 * math.pi * 1400 / 60
        assert abs(to_mag(raw['required_power'], 'W') - expected_P) < 1e-6

    def test_safety_factor(self):
        raw = motor_calc(5.0, 1400, safety_factor=2.0)
        assert abs(to_mag(raw['required_torque'], 'N*m') - 10.0) < 1e-9

    def test_quantity_input(self):
        from mechcalc.core.units import Q_
        raw = motor_calc(Q_(500, 'N*cm'), 1400)  # 500 N·cm = 5 N·m
        assert abs(to_mag(raw['required_torque'], 'N*m') - 6.0) < 1e-9

    def test_to_result(self):
        r = to_result(motor_calc, 5.0, 1400)
        assert r.required_torque['unit'] == 'm·N'   # pint 按字母序格式化
        assert r.required_speed['unit'] == 'rpm'
        assert r.required_power['unit'] == 'W'
        assert r.params['safety_factor'] == 1.2
