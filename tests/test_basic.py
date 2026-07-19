"""基础计算模块测试"""

import pytest
import math
from mechcalc import (
    velocity, displacement, acceleration, uniform_motion, uniform_acceleration,
    gravity, friction, centrifugal_force, inertia_force,
    angular_velocity, angular_acceleration, tangential_velocity, tangential_acceleration,
    kinetic_energy, potential_energy, power, torque_power,
    mass_from_density, cylinder_volume, sphere_volume, cuboid_volume,
)
from mechcalc.core.units import to_mag
from mechcalc import to_result


class TestKinematics:
    def test_velocity(self):
        result = to_result(velocity, 10, 2)
        assert abs(result.value['value'] - 5.0) < 1e-6
        assert result.value['unit'] == 'm/s'

    def test_displacement(self):
        result = to_result(displacement, 5, 3)
        assert abs(result.value['value'] - 15.0) < 1e-6

    def test_acceleration(self):
        result = to_result(acceleration, 10, 2)
        assert abs(result.value['value'] - 5.0) < 1e-6
        assert result.value['unit'] == 'm/s²'

    def test_uniform_motion(self):
        result = to_result(uniform_motion, 5, 4)
        assert abs(result.displacement['value'] - 20.0) < 1e-6
        assert abs(result.velocity['value'] - 5.0) < 1e-6

    def test_uniform_acceleration(self):
        result = to_result(uniform_acceleration, 0, 10, 2)
        assert abs(result.acceleration['value'] - 5.0) < 1e-6
        assert abs(result.displacement['value'] - 10.0) < 1e-6
        assert abs(result.avg_velocity['value'] - 5.0) < 1e-6


class TestDynamics:
    def test_gravity(self):
        result = to_result(gravity, 10)
        assert abs(result.value['value'] - 98.0665) < 1e-3
        assert result.value['unit'] == 'N'

    def test_gravity_raw(self):
        raw = gravity(10)
        assert abs(to_mag(raw, 'N') - 98.0665) < 1e-3

    def test_friction(self):
        result = to_result(friction, 100, 0.3)
        assert abs(result.value['value'] - 30.0) < 1e-6

    def test_friction_static(self):
        result = to_result(friction, 100, 0.5, static=True)
        assert abs(result.value['value'] - 50.0) < 1e-6

    def test_centrifugal_force(self):
        result = to_result(centrifugal_force, 1, 0.1, 10)
        # F = 1 * 10² * 0.1 = 10 N
        assert abs(result.value['value'] - 10.0) < 1e-6

    def test_inertia_force(self):
        result = to_result(inertia_force, 5, 2)
        # F = 5 * 2 = 10 N
        assert abs(result.value['value'] - 10.0) < 1e-6


class TestRotation:
    def test_angular_velocity(self):
        result = to_result(angular_velocity, 60)
        # ω = 2π * 60 / 60 = 2π rad/s
        expected = 2 * math.pi
        assert abs(result.value['value'] - expected) < 1e-6

    def test_angular_acceleration(self):
        result = to_result(angular_acceleration, 10, 2)
        assert abs(result.value['value'] - 5.0) < 1e-6

    def test_tangential_velocity(self):
        result = to_result(tangential_velocity, 0.1, 10)
        # v = 10 * 0.1 = 1 m/s
        assert abs(result.value['value'] - 1.0) < 1e-6

    def test_tangential_acceleration(self):
        result = to_result(tangential_acceleration, 0.1, 5)
        # a = 5 * 0.1 = 0.5 m/s²
        assert abs(result.value['value'] - 0.5) < 1e-6


class TestEnergy:
    def test_kinetic_energy(self):
        result = to_result(kinetic_energy, 2, 3)
        # E = 0.5 * 2 * 3² = 9 J
        assert abs(result.value['value'] - 9.0) < 1e-6

    def test_potential_energy(self):
        result = to_result(potential_energy, 10, 2)
        # E = 10 * 9.80665 * 2 = 196.133 J
        expected = 10 * 9.80665 * 2
        assert abs(result.value['value'] - expected) < 1e-3

    def test_power(self):
        result = to_result(power, 100, 5)
        # P = 100 * 5 = 500 W
        assert abs(result.value['value'] - 500.0) < 1e-6

    def test_torque_power(self):
        result = to_result(torque_power, 10, 5)
        # P = 10 * 5 = 50 W
        assert abs(result.value['value'] - 50.0) < 1e-6


class TestMassVolume:
    def test_mass_from_density(self):
        result = to_result(mass_from_density, 7850, 0.001)
        # m = 7850 * 0.001 = 7.85 kg
        assert abs(result.value['value'] - 7.85) < 1e-6

    def test_cylinder_volume(self):
        result = to_result(cylinder_volume, 0.1, 0.2)
        # V = π * (0.05)² * 0.2 = π * 0.0025 * 0.2
        expected = math.pi * 0.05 ** 2 * 0.2
        assert abs(result.value['value'] - expected) < 1e-9

    def test_sphere_volume(self):
        result = to_result(sphere_volume, 0.1)
        # V = π * 0.1³ / 6
        expected = math.pi * 0.1 ** 3 / 6
        assert abs(result.value['value'] - expected) < 1e-9

    def test_cuboid_volume(self):
        result = to_result(cuboid_volume, 0.1, 0.2, 0.3)
        assert abs(result.value['value'] - 0.006) < 1e-9
