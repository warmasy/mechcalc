"""core.linalg 向量工具测试"""

import math
import numpy as np
import pytest
from pint import DimensionalityError

from mechcalc.core.linalg import (
    as_vec3, as_vecs, skew, unit_vector, rot_x, rot_y, rot_z,
)
from mechcalc.core.units import Q_


class TestAsVec3:
    def test_raw_list(self):
        np.testing.assert_allclose(as_vec3([1, 2, 3], 'm'), [1, 2, 3])

    def test_quantity_converted(self):
        # mm 自动换算成 m
        np.testing.assert_allclose(
            as_vec3(Q_([100, 200, 0], 'mm'), 'm'), [0.1, 0.2, 0.0])

    def test_wrong_shape(self):
        with pytest.raises(ValueError):
            as_vec3([1, 2], 'm')

    def test_wrong_dimension(self):
        # 量纲错误在入口被拦截
        with pytest.raises(DimensionalityError):
            as_vec3(Q_([1, 2, 3], 's'), 'm')


class TestAsVecs:
    def test_normalized(self):
        n = as_vecs([0, 0, 5])
        np.testing.assert_allclose(n, [0, 0, 1])

    def test_batch(self):
        ns = as_vecs([[3, 0, 0], [0, 0, 5]])
        assert ns.shape == (2, 3)
        np.testing.assert_allclose(np.linalg.norm(ns, axis=1), [1, 1])

    def test_wrong_shape(self):
        with pytest.raises(ValueError):
            as_vecs([1, 2])


class TestSkew:
    def test_equals_cross(self):
        w = np.array([1.0, 2.0, 3.0])
        r = np.array([0.5, -1.0, 2.0])
        np.testing.assert_allclose(skew(w) @ r, np.cross(w, r))

    def test_antisymmetric(self):
        S = skew([1.0, 2.0, 3.0])
        np.testing.assert_allclose(S + S.T, np.zeros((3, 3)))


class TestUnitVector:
    def test_norm_one(self):
        assert abs(np.linalg.norm(unit_vector([3, 4, 0])) - 1.0) < 1e-12


class TestRotation:
    def test_rot_z_quarter(self):
        R = rot_z(math.pi / 2)
        np.testing.assert_allclose(R @ np.array([1.0, 0, 0]), [0, 1, 0], atol=1e-12)

    def test_rot_x_quarter(self):
        R = rot_x(math.pi / 2)
        np.testing.assert_allclose(R @ np.array([0, 1.0, 0]), [0, 0, 1], atol=1e-12)

    def test_rot_y_quarter(self):
        R = rot_y(math.pi / 2)
        np.testing.assert_allclose(R @ np.array([1.0, 0, 0]), [0, 0, -1], atol=1e-12)

    def test_accepts_deg_quantity(self):
        R = rot_z(Q_(90, 'deg'))
        np.testing.assert_allclose(R @ np.array([1.0, 0, 0]), [0, 1, 0], atol=1e-12)

    def test_orthogonal_and_proper(self):
        # 旋转矩阵：正交且行列式为 1
        for R in (rot_x(0.3), rot_y(0.5), rot_z(0.7)):
            np.testing.assert_allclose(R @ R.T, np.eye(3), atol=1e-12)
            assert abs(np.linalg.det(R) - 1.0) < 1e-12
