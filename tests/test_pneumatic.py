"""气动计算模块测试"""

import pytest
import math
from mechcalc import (
    push_force, pull_force, air_consumption, cylinder_select, STD_BORES,
)
from mechcalc.core.units import to_mag
from mechcalc import to_result


class TestPushForce:
    def test_basic(self):
        result = to_result(push_force, 0.4, 32)
        # A = pi*(16)^2 = 804.25 mm²
        # F = 0.4 MPa * 804.25 mm² * 0.85 = 0.4 N/mm² * 804.25 mm² * 0.85
        # F = 0.4e6 Pa * 804.25e-6 m² * 0.85 = 273.445 N
        assert 'F' in result
        assert 'A' in result
        assert result.F['unit'] == 'N'
        assert result.A['unit'] == 'mm²'

    def test_raw(self):
        raw = push_force(0.4, 32)
        assert 'F' in raw
        assert 'A' in raw


class TestPullForce:
    def test_basic(self):
        result = to_result(pull_force, 0.4, 32)
        assert 'F' in result
        assert 'A' in result

    def test_with_rod(self):
        result = to_result(pull_force, 0.4, 32, d=12)
        assert 'F' in result

    def test_auto_rod(self):
        result = to_result(pull_force, 0.4, 32)
        # 自动估算杆径: max(round(32*0.35), 2) = max(11, 2) = 11
        assert 'F' in result


class TestAirConsumption:
    def test_basic(self):
        result = to_result(air_consumption, 32, 100, 2, 0.4)
        assert 'air_consumption' in result
        assert 'volume_per_stroke' in result


class TestCylinderSelect:
    def test_select_success(self):
        result = to_result(cylinder_select, 200, 0.4, 100)
        assert 'selected_bore' in result
        assert 'theoretical_bore' in result
        assert 'push_force' in result
        assert 'pull_force' in result
        assert result.selected_bore['unit'] == 'mm'
        assert result.selected_bore['value'] in STD_BORES

    def test_select_params(self):
        result = to_result(cylinder_select, 200, 0.4, 100, eta=0.9, S=1.5)
        assert result.params['eta'] == 0.9
        assert result.params['S'] == 1.5

    def test_select_raw(self):
        raw = cylinder_select(200, 0.4, 100)
        assert 'selected_bore' in raw
        assert 'theoretical_bore' in raw
