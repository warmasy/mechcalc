"""惯量计算模块测试"""

import pytest
import math
from mechcalc import (
    solid_cylinder, hollow_cylinder, point_mass,
    straight_rod, conveyor_belt, ball_screw, gear_rack, gearbox,
)
from mechcalc.core.units import to_mag
from mechcalc import to_result


class TestSolidCylinder:
    def test_basic(self):
        result = to_result(solid_cylinder, 10, 100)
        # J = m*D^2/8 = 10*(0.1)^2/8 = 0.0125 kg·m²
        assert abs(result.value['value'] - 0.0125) < 1e-6
        assert result.value['unit'] == 'kg·m²'

    def test_raw(self):
        raw = solid_cylinder(10, 100)
        assert abs(to_mag(raw, 'kg*m**2') - 0.0125) < 1e-6

    def test_params_recorded(self):
        result = to_result(solid_cylinder, 10, 100)
        assert result.params['mass']['value'] == 10.0
        assert result.params['mass']['unit'] == 'kg'
        assert result.params['outer_diameter']['value'] == 100.0
        assert result.params['outer_diameter']['unit'] == 'mm'


class TestHollowCylinder:
    def test_basic(self):
        result = to_result(hollow_cylinder, 10, 100, 50)
        # J = m*(D^2+d^2)/8 = 10*(0.01+0.0025)/8 = 0.015625 kg·m²
        expected = 10 * (0.1**2 + 0.05**2) / 8
        assert abs(result.value['value'] - expected) < 1e-6


class TestPointMass:
    def test_basic(self):
        result = to_result(point_mass, 5, 50)
        # J = m*r^2 = 5*(0.05)^2 = 0.0125 kg·m²
        expected = 5 * 0.05**2
        assert abs(result.value['value'] - expected) < 1e-6


class TestStraightRod:
    def test_basic(self):
        result = to_result(straight_rod, 2, 300)
        # J = m*L^2/12 = 2*(0.3)^2/12 = 0.015 kg·m²
        expected = 2 * 0.3**2 / 12
        assert abs(result.value['value'] - expected) < 1e-6


class TestConveyorBelt:
    def test_basic(self):
        result = to_result(conveyor_belt, 100, 80)
        # J = m*(D/2)^2 = 100*(0.04)^2 = 0.16 kg·m²
        expected = 100 * 0.04**2
        assert abs(result.value['value'] - expected) < 1e-6


class TestBallScrew:
    def test_basic(self):
        result = to_result(ball_screw, 5, 10)
        # J = m*P^2/(4*pi^2) = 5*(0.01)^2/(4*pi^2)
        expected = 5 * 0.01**2 / (4 * math.pi**2)
        assert abs(result.value['value'] - expected) < 1e-6


class TestGearRack:
    def test_basic(self):
        result = to_result(gear_rack, 10, 60)
        # J = m*(pi*D/2)^2 = 10*(pi*0.03)^2
        expected = 10 * (math.pi * 0.03)**2
        assert abs(result.value['value'] - expected) < 1e-6


class TestGearbox:
    def test_basic(self):
        result = to_result(gearbox, 0.1, 5)
        # J_ref = J/i^2 = 0.1/25 = 0.004 kg·m²
        expected = 0.1 / 25
        assert abs(result.value['value'] - expected) < 1e-6
