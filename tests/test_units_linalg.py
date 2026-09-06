"""带单位线性代数工具测试

验证「剥单位-裸算-装回」封装的结果数值与单位推导是否正确。
"""

import numpy as np
import pytest

from mechcalc.core import Q_, det, eig, inv, matrix_power, trace


class TestInv:
    def test_numeric(self):
        A = Q_(np.array([[2.0, 0.0], [0.0, 4.0]]), "m")
        r = inv(A)
        np.testing.assert_allclose(r.magnitude, [[0.5, 0], [0, 0.25]])
        assert str(r.units) == "1 / meter"

    def test_unit_reciprocal(self):
        A = Q_(np.array([[1.0, 2.0], [3.0, 4.0]]), "kg*m**2")
        r = inv(A)
        assert r.check("1 / [mass] / [length] ** 2")

    def test_raw_array_passthrough(self):
        r = inv(np.array([[1.0, 0.0], [0.0, 1.0]]))
        assert isinstance(r, np.ndarray)


class TestDet:
    def test_unit_power(self):
        A = Q_(np.array([[2.0, 0.0], [0.0, 3.0]]), "m")
        r = det(A)
        assert abs(r.magnitude - 6.0) < 1e-12
        assert str(r.units) == "meter ** 2"

    def test_3x3(self):
        A = Q_(np.eye(3) * 2.0, "kg")
        r = det(A)
        assert abs(r.magnitude - 8.0) < 1e-12
        assert str(r.units) == "kilogram ** 3"


class TestEig:
    def test_eigenvalue_units(self):
        A = Q_(np.array([[2.0, 0.0], [0.0, 3.0]]), "m")
        w, v = eig(A)
        np.testing.assert_allclose(np.sort(w.magnitude), [2.0, 3.0])
        assert str(w.units) == "meter"

    def test_eigenvector_dimensionless(self):
        A = Q_(np.array([[2.0, 0.0], [0.0, 3.0]]), "m")
        w, v = eig(A)
        assert not hasattr(v, "units")


class TestMatrixPower:
    def test_positive_power(self):
        A = Q_(np.array([[2.0, 0.0], [0.0, 3.0]]), "m")
        r = matrix_power(A, 3)
        np.testing.assert_allclose(r.magnitude, [[8.0, 0], [0, 27.0]])
        assert str(r.units) == "meter ** 3"

    def test_negative_power(self):
        A = Q_(np.array([[2.0, 0.0], [0.0, 4.0]]), "m")
        r = matrix_power(A, -1)
        np.testing.assert_allclose(r.magnitude, [[0.5, 0], [0, 0.25]])
        assert str(r.units) == "1 / meter"


class TestTrace:
    def test_unit_preserved(self):
        A = Q_(np.array([[1.0, 2.0], [3.0, 4.0]]), "kg*m**2")
        r = trace(A)
        assert abs(r.magnitude - 5.0) < 1e-12
        assert r.check("[mass] * [length] ** 2")

    def test_raw_array(self):
        r = trace(np.eye(3))
        assert r == 3.0


class TestInteropWithScalar:
    def test_inertia_tensor_trace(self):
        """物理场景：惯量张量的迹 = Ixx+Iyy+Izz"""
        from mechcalc import solid_cylinder_tensor

        I = solid_cylinder_tensor(10, 100, 200)
        tr = trace(I)
        expected = I.magnitude[0, 0] + I.magnitude[1, 1] + I.magnitude[2, 2]
        assert abs(tr.magnitude - expected) < 1e-12

    def test_det_zero_raises(self):
        A = Q_(np.zeros((2, 2)), "m")
        with pytest.raises(np.linalg.LinAlgError):
            inv(A)
