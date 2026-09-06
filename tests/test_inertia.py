"""惯量计算模块测试（含手册新增几何体）"""

import math

import pytest

from mechcalc import (
    annular_plate,
    # 细杆
    arc_rod,
    ball_screw,
    circular_plate,
    circular_ring_rod,
    cone,
    cone_lateral_shell,
    cylinder,
    cylinder_lateral_shell,
    cylinder_total_shell,
    cylindrical_rod,
    elliptical_plate,
    elliptical_ring_rod,
    elliptical_torus,
    gear_rack,
    gearbox,
    hemisphere,
    hemisphere_shell,
    hollow_sphere,
    inclined_rod,
    parabolic_plate,
    point_mass,
    rectangular_frame_rod,
    rectangular_plate,
    # 立体形状
    rectangular_prism,
    rectangular_torus,
    regular_polygon_plate,
    right_pyramid,
    sector_plate,
    segment_plate,
    semicircular_plate,
    sphere,
    sphere_shell,
    spherical_cap,
    to_result,
    torus_shell,
    trapezoidal_plate,
    # 平面板
    triangular_plate,
    triangular_prism,
    truncated_cone,
    # 薄壳体
    truncated_cone_shell,
    tube,
    u_rod,
)
from mechcalc.core.units import to_mag

# ==================== 原有测试（保留）====================


class TestPointMass:
    def test_basic(self):
        result = to_result(point_mass, 5, 50)
        expected = 5 * 0.05**2
        assert abs(result.value["value"] - expected) < 1e-6


class TestBallScrew:
    def test_basic(self):
        result = to_result(ball_screw, 5, 10)
        expected = 5 * 0.01**2 / (4 * math.pi**2)
        assert abs(result.value["value"] - expected) < 1e-6


class TestGearRack:
    def test_basic(self):
        result = to_result(gear_rack, 10, 60)
        expected = 10 * (math.pi * 0.03) ** 2
        assert abs(result.value["value"] - expected) < 1e-6


class TestGearbox:
    def test_basic(self):
        result = to_result(gearbox, 0.1, 5)
        expected = 0.1 / 25
        assert abs(result.value["value"] - expected) < 1e-6


class TestInclinedRod:
    def test_alpha_90_matches_rod_formula(self):
        raw = inclined_rod(10, 400, 90)
        J_rod = 10 * 0.4**2 / 12  # m·L²/12（细杆绕中点）
        assert abs(to_mag(raw["J_c"], "kg*m**2") - J_rod) < 1e-12

    def test_alpha_0(self):
        raw = inclined_rod(10, 400, 0, r=100)
        assert abs(to_mag(raw["J_c"], "kg*m**2")) < 1e-15
        assert abs(to_mag(raw["J_b"], "kg*m**2")) < 1e-15
        assert abs(to_mag(raw["J_a"], "kg*m**2") - 10 * 0.1**2) < 1e-12

    def test_end_axis_is_4x_center(self):
        raw = inclined_rod(10, 400, 90)
        J_b = to_mag(raw["J_b"], "kg*m**2")
        J_c = to_mag(raw["J_c"], "kg*m**2")
        assert abs(J_b - 4 * J_c) < 1e-12


# ==================== 新增测试：细杆 ====================


class TestArcRod:
    def test_semicircle(self):
        raw = arc_rod(2, 100, 90)
        assert abs(to_mag(raw["J_rho_O"], "kg*m**2") - 2 * 0.1**2) < 1e-12

    def test_quarter_circle(self):
        raw = arc_rod(1, 200, 45)
        J = to_mag(raw["J_rho_O"], "kg*m**2")
        assert abs(J - 1 * 0.2**2) < 1e-12


class TestURod:
    def test_symmetric(self):
        raw = u_rod(3, 200, 100)
        assert "J_x" in raw
        assert "J_y" in raw
        assert to_mag(raw["J_x"], "kg*m**2") > 0


class TestCylindricalRod:
    def test_basic(self):
        raw = cylindrical_rod(5, 150, 250, 30)
        assert "J_x" in raw
        assert "J_y" in raw
        assert "J_z" in raw


class TestRectangularFrameRod:
    def test_square(self):
        raw = rectangular_frame_rod(4, 200, 200)
        Jx = to_mag(raw["J_x"], "kg*m**2")
        Jy = to_mag(raw["J_y"], "kg*m**2")
        assert abs(Jx - Jy) < 1e-12


class TestEllipticalRingRod:
    def test_degenerate_to_circle(self):
        raw = elliptical_ring_rod(2, 100, 100)
        Jx = to_mag(raw["J_x"], "kg*m**2")
        Jy = to_mag(raw["J_y"], "kg*m**2")
        expected = 2 * 0.1**2 / 2
        assert abs(Jx - expected) < 0.001
        assert abs(Jy - expected) < 0.001
        assert abs(Jx - Jy) < 0.001


class TestCircularRingRod:
    def test_basic(self):
        raw = circular_ring_rod(1, 50)
        Jx = to_mag(raw["J_x"], "kg*m**2")
        expected = 1 * 0.05**2 / 2
        assert abs(Jx - expected) < 1e-12


# ==================== 新增测试：平面板 ====================


class TestTriangularPlate:
    def test_basic(self):
        raw = triangular_plate(2, 300, 200)
        Jx = to_mag(raw["J_x"], "kg*m**2")
        expected = 2 * 0.2**2 / 18
        assert abs(Jx - expected) < 1e-12


class TestRectangularPlate:
    def test_basic(self):
        raw = rectangular_plate(3, 400, 600)
        Jx = to_mag(raw["J_x"], "kg*m**2")
        expected = 3 * 0.4**2 / 12
        assert abs(Jx - expected) < 1e-12

    def test_rho_O(self):
        raw = rectangular_plate(3, 400, 600)
        J_rho = to_mag(raw["J_rho_O"], "kg*m**2")
        expected = 3 * (0.4**2 + 0.6**2) / 12
        assert abs(J_rho - expected) < 1e-12


class TestSemicircularPlate:
    def test_basic(self):
        raw = semicircular_plate(2, 100)
        Jx = to_mag(raw["J_x"], "kg*m**2")
        expected = 2 * 0.1**2 / 4
        assert abs(Jx - expected) < 1e-12


class TestAnnularPlate:
    def test_basic(self):
        raw = annular_plate(2, 100, 50)
        Jx = to_mag(raw["J_x"], "kg*m**2")
        expected = 2 * (0.1**2 + 0.05**2) / 4
        assert abs(Jx - expected) < 1e-12


class TestSectorPlate:
    def test_semicircle(self):
        raw = sector_plate(2, 100, 90)
        Jx = to_mag(raw["J_x"], "kg*m**2")
        expected = 2 * 0.1**2 / 4
        assert abs(Jx - expected) < 1e-12


class TestTrapezoidalPlate:
    def test_basic(self):
        raw = trapezoidal_plate(3, 100, 200, 150)
        assert to_mag(raw["J_a"], "kg*m**2") > 0
        assert to_mag(raw["J_b"], "kg*m**2") > 0


class TestRegularPolygonPlate:
    def test_square(self):
        raw = regular_polygon_plate(4, n=4, side_length=100)
        Jx = to_mag(raw["J_x"], "kg*m**2")
        expected = 4 * 0.1**2 / 12
        assert abs(Jx - expected) < 1e-6


class TestCircularPlate:
    def test_basic(self):
        raw = circular_plate(2, 100)
        Jx = to_mag(raw["J_x"], "kg*m**2")
        expected = 2 * 0.1**2 / 4
        assert abs(Jx - expected) < 1e-12


class TestSegmentPlate:
    def test_basic(self):
        raw = segment_plate(2, 100, 30)
        assert to_mag(raw["J_x"], "kg*m**2") > 0


class TestEllipticalPlate:
    def test_degenerate_to_circle(self):
        raw = elliptical_plate(2, 100, 100)
        Jx = to_mag(raw["J_x"], "kg*m**2")
        expected = 2 * 0.1**2 / 4
        assert abs(Jx - expected) < 1e-12


class TestParabolicPlate:
    def test_basic(self):
        raw = parabolic_plate(2, 100, 50)
        assert to_mag(raw["J_x"], "kg*m**2") > 0


# ==================== 新增测试：立体形状 ====================


class TestRectangularPrism:
    def test_cube(self):
        raw = rectangular_prism(2, 100, 100, 100)
        Jx = to_mag(raw["J_x"], "kg*m**2")
        expected = 2 * (0.1**2 + 0.1**2) / 12
        assert abs(Jx - expected) < 1e-12


class TestRightPyramid:
    def test_basic(self):
        raw = right_pyramid(3, 200, 200, 300)
        assert to_mag(raw["J_x"], "kg*m**2") > 0
        assert to_mag(raw["y_bar"], "m") == 0.3 / 4


class TestTriangularPrism:
    def test_basic(self):
        raw = triangular_prism(2, 100, 200)
        assert to_mag(raw["J_x"], "kg*m**2") > 0


class TestTruncatedCone:
    def test_basic(self):
        raw = truncated_cone(5, 100, 50, 200)
        assert to_mag(raw["J_y"], "kg*m**2") > 0


class TestSphere:
    def test_basic(self):
        raw = sphere(2, 100)
        J = to_mag(raw["J_x"], "kg*m**2")
        expected = 2 * 2 * 0.1**2 / 5
        assert abs(J - expected) < 1e-12


class TestHollowSphere:
    def test_thin_shell_limit(self):
        raw = hollow_sphere(2, 100.1, 100)
        J = to_mag(raw["J_x"], "kg*m**2")
        assert J > 0


class TestCylinder:
    def test_axis_inertia_formula(self):
        """J_y = m·R²/2（绕对称轴），与长度无关"""
        raw = cylinder(10, 100, 10)
        J_y = to_mag(raw["J_y"], "kg*m**2")
        expected = 10 * 0.05**2 / 2
        assert abs(J_y - expected) < 1e-12

    def test_vertical_axis(self):
        """长圆柱垂直轴惯量应大于中心轴"""
        raw = cylinder(10, 100, 500)
        J_x = to_mag(raw["J_x"], "kg*m**2")
        J_y = to_mag(raw["J_y"], "kg*m**2")
        assert J_x > J_y

    def test_symmetry(self):
        raw = cylinder(10, 100, 200)
        assert to_mag(raw["J_x"], "kg*m**2") == to_mag(raw["J_z"], "kg*m**2")


class TestTube:
    def test_axis_inertia_formula(self):
        """J_y = m·(R²+r²)/2（绕对称轴），与长度无关"""
        raw = tube(10, 100, 50, 10)
        J_y = to_mag(raw["J_y"], "kg*m**2")
        expected = 10 * (0.05**2 + 0.025**2) / 2
        assert abs(J_y - expected) < 1e-12

    def test_basic(self):
        raw = tube(5, 200, 100, 300)
        assert to_mag(raw["J_x"], "kg*m**2") > 0
        assert to_mag(raw["J_y"], "kg*m**2") > 0


class TestCone:
    def test_basic(self):
        raw = cone(3, 100, 150)
        assert to_mag(raw["J_y"], "kg*m**2") > 0


class TestSphericalCap:
    def test_basic(self):
        raw = spherical_cap(2, 100, 50)
        assert to_mag(raw["J_y"], "kg*m**2") > 0


class TestEllipticalTorus:
    def test_basic(self):
        raw = elliptical_torus(2, 200, 30, 20)
        assert to_mag(raw["J_x"], "kg*m**2") > 0


class TestRectangularTorus:
    def test_basic(self):
        raw = rectangular_torus(2, 200, 30, 20)
        assert to_mag(raw["J_x"], "kg*m**2") > 0


class TestHemisphere:
    def test_basic(self):
        raw = hemisphere(2, 100)
        assert to_mag(raw["J_y"], "kg*m**2") > 0
        assert abs(to_mag(raw["y_bar"], "m") - 3 * 0.1 / 8) < 1e-12


# ==================== 新增测试：薄壳体 ====================


class TestTruncatedConeShell:
    def test_basic(self):
        raw = truncated_cone_shell(2, 100, 50, 150)
        assert to_mag(raw["J_x"], "kg*m**2") > 0


class TestCylinderLateralShell:
    def test_basic(self):
        raw = cylinder_lateral_shell(2, 100, 200)
        assert to_mag(raw["J_x"], "kg*m**2") > 0

    def test_degenerate_to_circular_ring(self):
        """h→0 退化为细圆环：J_x = m·R²/2"""
        raw = cylinder_lateral_shell(2, 100, 1e-6)
        expected = 2 * 0.1**2 / 2
        assert abs(to_mag(raw["J_x"], "kg*m**2") - expected) < 1e-9

    def test_degenerate_to_rod(self):
        """R→0 退化为细杆：J_x = m·h²/12"""
        raw = cylinder_lateral_shell(2, 1e-6, 300)
        expected = 2 * 0.3**2 / 12
        assert abs(to_mag(raw["J_x"], "kg*m**2") - expected) < 1e-9

    def test_matches_circular_ring_rod(self):
        """互锁：h→0 极限与 circular_ring_rod 一致"""
        raw = cylinder_lateral_shell(2, 100, 1e-6)
        ring = circular_ring_rod(2, 100)
        assert abs(to_mag(raw["J_x"], "kg*m**2") - to_mag(ring["J_x"], "kg*m**2")) < 1e-9


class TestCylinderTotalShell:
    def test_basic(self):
        raw = cylinder_total_shell(2, 100, 200)
        assert to_mag(raw["J_x"], "kg*m**2") > 0

    def test_degenerate_to_disk(self):
        """h→0 退化为圆盘：J_y = m·R²/2, J_x = m·R²/4"""
        raw = cylinder_total_shell(2, 100, 1e-6)
        assert abs(to_mag(raw["J_y"], "kg*m**2") - 2 * 0.1**2 / 2) < 1e-9
        assert abs(to_mag(raw["J_x"], "kg*m**2") - 2 * 0.1**2 / 4) < 1e-9


class TestConeLateralShell:
    def test_basic(self):
        raw = cone_lateral_shell(2, 100, 150)
        assert to_mag(raw["J_x"], "kg*m**2") > 0

    def test_numerical_integration(self):
        """数值积分对照：J_x(过质心直径轴) = m·(R²/4 + h²/18)"""
        import numpy as np

        m, R, h = 2.0, 0.1, 0.15
        N = 400000
        rng = np.random.default_rng(42)
        th = rng.uniform(0, 2 * np.pi, N)
        z = rng.uniform(0, h, N)  # 顶点在原点
        r = R * (1 - z / h)
        w = r  # 壳面质量权重 ∝ 半径
        I_apex = np.average((r * np.sin(th)) ** 2 + z**2, weights=w) * m
        I_c = I_apex - m * (h / 3) ** 2  # 移轴到质心 z̄=h/3
        raw = cone_lateral_shell(m, 100, 150)  # R=100mm, h=150mm 同比例
        assert abs(to_mag(raw["J_x"], "kg*m**2") - I_c) < 1e-4


class TestHemisphereShell:
    def test_basic(self):
        raw = hemisphere_shell(2, 100)
        Jx = to_mag(raw["J_x"], "kg*m**2")
        expected = 5 * 2 * 0.1**2 / 12
        assert abs(Jx - expected) < 1e-12


class TestSphereShell:
    def test_basic(self):
        raw = sphere_shell(2, 100)
        J = to_mag(raw["J_x"], "kg*m**2")
        expected = 2 * 2 * 0.1**2 / 3
        assert abs(J - expected) < 1e-12


class TestTorusShell:
    def test_basic(self):
        raw = torus_shell(2, 200, 30)
        assert to_mag(raw["J_x"], "kg*m**2") > 0


# ==================== 边界与异常测试 ====================


class TestValidation:
    def test_negative_mass(self):
        with pytest.raises(ValueError):
            sphere(-1, 100)

    def test_zero_radius(self):
        with pytest.raises(ValueError):
            sphere(1, 0)

    def test_invalid_angles(self):
        with pytest.raises(ValueError):
            sector_plate(1, 100, 0)
        with pytest.raises(ValueError):
            sector_plate(1, 100, 200)

    def test_inner_ge_outer(self):
        with pytest.raises(ValueError):
            annular_plate(1, 50, 100)
        with pytest.raises(ValueError):
            hollow_sphere(1, 50, 100)
        with pytest.raises(ValueError):
            tube(1, 50, 100, 200)

    def test_polygon_n_too_small(self):
        with pytest.raises(ValueError):
            regular_polygon_plate(1, n=2, side_length=100)

    def test_polygon_no_params(self):
        with pytest.raises(ValueError):
            regular_polygon_plate(1, n=4)
