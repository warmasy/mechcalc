"""惯量计算模块测试"""

import pytest
import math
from mechcalc import (
    solid_cylinder, hollow_cylinder, point_mass,
    straight_rod, conveyor_belt, ball_screw, gear_rack, gearbox,
    inclined_rod,
)
from mechcalc.core.units import to_mag, Q_
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


class TestInclinedRod:
    def test_alpha_90_matches_straight_rod(self):
        """α=90° 时 J_c 退化为 straight_rod（互锁）"""
        raw = inclined_rod(10, 400, 90)
        J_rod = to_mag(straight_rod(10, 400), 'kg*m**2')
        assert abs(to_mag(raw['J_c'], 'kg*m**2') - J_rod) < 1e-12

    def test_alpha_0(self):
        """α=0（杆与转轴平行）：J_c=J_b=0，J_a=m·r²"""
        raw = inclined_rod(10, 400, 0, r=100)
        assert abs(to_mag(raw['J_c'], 'kg*m**2')) < 1e-15
        assert abs(to_mag(raw['J_b'], 'kg*m**2')) < 1e-15
        assert abs(to_mag(raw['J_a'], 'kg*m**2') - 10 * 0.1**2) < 1e-12

    def test_end_axis_is_4x_center(self):
        """α=90° 时 J_b = m·l²/3 = 4·J_c"""
        raw = inclined_rod(10, 400, 90)
        Jb = to_mag(raw['J_b'], 'kg*m**2')
        Jc = to_mag(raw['J_c'], 'kg*m**2')
        assert abs(Jb - 4 * Jc) < 1e-12

    def test_parallel_axis_theorem(self):
        """J_a − J_c = m·r²（平行移轴定理）"""
        raw = inclined_rod(10, 400, 60, r=200)
        Ja = to_mag(raw['J_a'], 'kg*m**2')
        Jc = to_mag(raw['J_c'], 'kg*m**2')
        assert abs((Ja - Jc) - 10 * 0.2**2) < 1e-12

    def test_jz_independent_of_alpha(self):
        """J_z = m·l²/12，与 α 无关"""
        for a in (0, 30, 60, 90):
            raw = inclined_rod(10, 400, a)
            assert abs(to_mag(raw['J_z'], 'kg*m**2') - 10 * 0.4**2 / 12) < 1e-12

    def test_rad_quantity_input(self):
        """alpha 传 rad 的 Quantity"""
        raw = inclined_rod(10, 400, Q_(math.pi / 2, 'rad'))
        J_rod = to_mag(straight_rod(10, 400), 'kg*m**2')
        assert abs(to_mag(raw['J_c'], 'kg*m**2') - J_rod) < 1e-12

    def test_to_result(self):
        r = to_result(inclined_rod, 10, 400, 60, 100)
        assert r.J_c['unit'] == 'kg·m²'
        assert r.params['alpha']['unit'] == 'deg'
        assert r.params['r']['unit'] == 'mm'
