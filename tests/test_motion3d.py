"""basic.motion3d 三维运动测试

互锁策略：向量结果的模长/分量必须与已有标量函数一致。
"""

import math
import numpy as np

from mechcalc import (
    point_velocity, centripetal_acceleration,
    rotational_kinetic_energy, angular_momentum, gravity_force,
    tangential_velocity, gravity, solid_cylinder, solid_cylinder_tensor,
    rot_x,
)
from mechcalc.core.units import to_mag, Q_


class TestPointVelocity:
    def test_basic(self):
        # ω=(0,0,10), r=(0.1,0,0) -> v=(0,1,0)
        v = point_velocity([0, 0, 10], [0.1, 0, 0])
        np.testing.assert_allclose(np.asarray(v.magnitude), [0, 1, 0], atol=1e-12)
        assert v.check('[length] / [time]')

    def test_magnitude_matches_scalar(self):
        """互锁：|v| == 标量 tangential_velocity"""
        v = point_velocity([0, 0, 10], [0.1, 0, 0])
        speed = float(np.linalg.norm(np.asarray(v.magnitude)))
        v_scalar = to_mag(tangential_velocity(0.1, 10), 'm/s')
        assert abs(speed - v_scalar) < 1e-12

    def test_mixed_unit_input(self):
        # 位置传 mm 的 Quantity，结果不变
        v = point_velocity(Q_([0, 0, 10], 'rad/s'), Q_([100, 0, 0], 'mm'))
        np.testing.assert_allclose(np.asarray(v.magnitude), [0, 1, 0], atol=1e-12)


class TestCentripetalAcceleration:
    def test_points_to_center(self):
        # a = ω×(ω×r)，ω=(0,0,10), r=(0.1,0,0) -> a=(-10,0,0)，指向轴心
        a = centripetal_acceleration([0, 0, 10], [0.1, 0, 0])
        np.testing.assert_allclose(np.asarray(a.magnitude), [-10, 0, 0], atol=1e-12)
        assert a.check('[length] / [time] ** 2')


class TestRotationalKineticEnergy:
    def test_basic(self):
        # diag(1,2,3), ω=(0,0,10) -> T = 0.5*3*100 = 150 J
        I = Q_(np.diag([1.0, 2.0, 3.0]), 'kg*m**2')
        T = rotational_kinetic_energy(I, [0, 0, 10])
        assert abs(to_mag(T, 'J') - 150.0) < 1e-12

    def test_matches_scalar_formula(self):
        """互锁：张量 + 绕 z 轴 == ½·J_标量·ω²"""
        I = solid_cylinder_tensor(10, 100, 200)
        T = to_mag(rotational_kinetic_energy(I, [0, 0, 10]), 'J')
        J = to_mag(solid_cylinder(10, 100), 'kg*m**2')
        assert abs(T - 0.5 * J * 100) < 1e-12


class TestAngularMomentum:
    def test_basic(self):
        # diag(1,2,3), ω=(0,0,10) -> L = (0,0,30)
        I = Q_(np.diag([1.0, 2.0, 3.0]), 'kg*m**2')
        L = angular_momentum(I, [0, 0, 10])
        np.testing.assert_allclose(np.asarray(L.magnitude), [0, 0, 30])


class TestGravityForce:
    def test_world_frame(self):
        F = gravity_force(10)
        np.testing.assert_allclose(
            np.asarray(F.magnitude), [0, 0, -98.0665], atol=1e-9)

    def test_magnitude_matches_scalar(self):
        """互锁：|F| == 标量 gravity"""
        F = gravity_force(10)
        mag = float(np.linalg.norm(np.asarray(F.magnitude)))
        assert abs(mag - to_mag(gravity(10), 'N')) < 1e-9

    def test_rotated_frame(self):
        # 本体系绕 x 轴转 90°，重力在本体系中的分量随之旋转
        R = rot_x(math.pi / 2)
        F = gravity_force(10, rotation=R)
        expected = R @ np.array([0, 0, -98.0665])
        np.testing.assert_allclose(np.asarray(F.magnitude), expected, atol=1e-9)

    def test_rotation_shape_check(self):
        import pytest
        with pytest.raises(ValueError):
            gravity_force(10, rotation=[1, 2, 3])
