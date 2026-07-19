"""inertia.tensor 惯量张量测试

互锁策略：向量/张量结果必须与已有标量函数结果一致。
"""

import json
import numpy as np

from mechcalc import (
    solid_cylinder, hollow_cylinder, point_mass,
    solid_cylinder_tensor, hollow_cylinder_tensor,
    parallel_axis_tensor, inertia_about_axis,
)
from mechcalc.core.units import to_mag, Q_
from mechcalc import to_result


class TestSolidCylinderTensor:
    def test_izz_matches_scalar(self):
        """互锁：张量 Izz == 标量 solid_cylinder"""
        I = np.asarray(solid_cylinder_tensor(10, 100, 200).magnitude)
        J = to_mag(solid_cylinder(10, 100), 'kg*m**2')
        assert abs(I[2, 2] - J) < 1e-12

    def test_ixx_formula(self):
        # m=10, R=0.05, L=0.2 -> Ixx = 10*(3*0.05^2 + 0.2^2)/12
        I = np.asarray(solid_cylinder_tensor(10, 100, 200).magnitude)
        assert abs(I[0, 0] - 10 * (3 * 0.05**2 + 0.2**2) / 12) < 1e-12
        assert I[0, 0] == I[1, 1]
        assert abs(I[0, 1]) < 1e-15  # 非对角元为零

    def test_unit(self):
        T = solid_cylinder_tensor(10, 100, 200)
        assert T.check('[mass] * [length] ** 2')

    def test_to_result_json_safe(self):
        """Result 模式下数组结果为 list，可直接 JSON 序列化"""
        r = to_result(solid_cylinder_tensor, 10, 100, 200)
        assert isinstance(r.value['value'], list)
        assert r.value['unit'] == 'kg·m²'
        json.dumps(r.to_api())


class TestHollowCylinderTensor:
    def test_izz_matches_scalar(self):
        """互锁：张量 Izz == 标量 hollow_cylinder"""
        I = np.asarray(hollow_cylinder_tensor(10, 100, 50, 200).magnitude)
        J = to_mag(hollow_cylinder(10, 100, 50), 'kg*m**2')
        assert abs(I[2, 2] - J) < 1e-12


class TestParallelAxisTensor:
    def test_shift_then_about_z(self):
        """平移 [d,0,0] 后绕 z 轴 = Izz + m·d²"""
        I_c = solid_cylinder_tensor(10, 100, 200)
        I_new = parallel_axis_tensor(I_c, 10, [0.5, 0, 0])
        J = to_mag(inertia_about_axis(I_new, [0, 0, 1]), 'kg*m**2')
        J_c = to_mag(solid_cylinder(10, 100), 'kg*m**2')
        assert abs(J - (J_c + 10 * 0.5**2)) < 1e-12

    def test_degenerates_to_point_mass(self):
        """互锁：零张量平行移轴退化为标量 point_mass"""
        I0 = Q_(np.zeros((3, 3)), 'kg*m**2')
        I_new = parallel_axis_tensor(I0, 5, [0.3, 0, 0])
        J = to_mag(inertia_about_axis(I_new, [0, 0, 1]), 'kg*m**2')
        J_pm = to_mag(point_mass(5, 300), 'kg*m**2')  # radius=300mm
        assert abs(J - J_pm) < 1e-12


class TestInertiaAboutAxis:
    def test_z_axis_matches_scalar(self):
        """互锁：绕 z 轴 == 标量 solid_cylinder"""
        I = solid_cylinder_tensor(10, 100, 200)
        J = inertia_about_axis(I, [0, 0, 1])
        assert abs(to_mag(J, 'kg*m**2') - to_mag(solid_cylinder(10, 100), 'kg*m**2')) < 1e-12

    def test_axis_auto_normalized(self):
        I = solid_cylinder_tensor(10, 100, 200)
        J1 = to_mag(inertia_about_axis(I, [0, 0, 1]), 'kg*m**2')
        J2 = to_mag(inertia_about_axis(I, [0, 0, 5]), 'kg*m**2')
        assert abs(J1 - J2) < 1e-12

    def test_batch(self):
        I = solid_cylinder_tensor(10, 100, 200)
        Js = np.asarray(inertia_about_axis(I, [[1, 0, 0], [0, 1, 0], [0, 0, 1]]).magnitude)
        arr = np.asarray(I.magnitude)
        np.testing.assert_allclose(Js, [arr[0, 0], arr[1, 1], arr[2, 2]])

    def test_unit_perturbation(self):
        """单位扰动：同一物理量换单位输入，结果必须不变"""
        I_a = solid_cylinder_tensor(10, 100, 200)                    # 函数内部生成
        I_b = Q_(np.asarray(I_a.magnitude), 'kg*m**2')               # 显式 Quantity
        I_c = np.asarray(I_a.magnitude)                              # 裸数组（按 kg·m²）
        J1 = to_mag(inertia_about_axis(I_a, [0, 0, 1]), 'kg*m**2')
        J2 = to_mag(inertia_about_axis(I_b, [0, 0, 1]), 'kg*m**2')
        J3 = to_mag(inertia_about_axis(I_c, [0, 0, 1]), 'kg*m**2')
        assert abs(J1 - J2) < 1e-15
        assert abs(J1 - J3) < 1e-15
