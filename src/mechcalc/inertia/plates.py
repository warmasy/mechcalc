"""平面板类惯量计算

基于《机械设计手册》表 1-1-83 平面板部分。
"""

import math

from pint import Quantity

from ..core.units import QuantityLike, set_quantity
from ._utils import _sum_inertia, _to_rad, _validate_positive, inertia_result


def triangular_plate(
    mass: QuantityLike,
    b: QuantityLike,
    h: QuantityLike,
    b1: QuantityLike = None,
    b2: QuantityLike = None,
) -> dict[str, Quantity]:
    """
    三角形平板。
    文档表1-1-83 平面板-三角形。

    :param mass: 质量(kg)
    :param b: 底边总长(mm)
    :param h: 高(mm)
    :param b1: 底边被垂足分成的左段(mm)，默认 b/2
    :param b2: 底边被垂足分成的右段(mm)，默认 b/2
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²), 'y_bar': 质心距底边(mm)}
    """
    m = set_quantity(mass, "kg")
    b_m = set_quantity(b, "mm")
    h_m = set_quantity(h, "mm")
    _validate_positive(mass=m, b=b_m, h=h_m)

    if b1 is None or b2 is None:
        b1_m = b2_m = b_m / 2.0
    else:
        b1_m = set_quantity(b1, "mm")
        b2_m = set_quantity(b2, "mm")

    J_x = _sum_inertia([(1.0 / 18.0, m, h_m)])  # m·h²/18
    J_y = (m * (b1_m**3 + b2_m**3) / (6.0 * b_m)).to("kg*m**2")  # 比值式，保留原公式

    y_bar = (h_m / 3.0).to("m")
    area = (0.5 * b_m * h_m).to("m**2")

    return inertia_result(Jx=J_x, Jy=J_y, plane=True, y_bar=y_bar, area=area)


def rectangular_plate(mass: QuantityLike, a: QuantityLike, b: QuantityLike) -> dict[str, Quantity]:
    """
    矩形板。
    文档表1-1-83 平面板-矩形。

    :param mass: 质量(kg)
    :param a: 板高度(mm，y方向尺寸)
    :param b: 板宽度(mm，x方向尺寸)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²),
              'J_rho_O': 绕ρO轴(kg·m²), 'J_D': 绕对角线轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    a_m = set_quantity(a, "mm")
    b_m = set_quantity(b, "mm")
    _validate_positive(mass=m, a=a_m, b=b_m)

    k12 = 1.0 / 12.0
    J_x = _sum_inertia([(k12, m, a_m)])  # m·a²/12
    J_y = _sum_inertia([(k12, m, b_m)])  # m·b²/12
    J_rho_O = _sum_inertia([(k12, m, a_m), (k12, m, b_m)])  # m(a²+b²)/12

    D2 = a_m**2 + b_m**2  # mm²，保持 Quantity
    sin_phi = (2.0 * a_m * b_m / D2).to("")  # 无量纲
    J_D = (m * D2 * sin_phi**2 / 24.0).to("kg*m**2")
    area = (a_m * b_m).to("m**2")

    return inertia_result(Jx=J_x, Jy=J_y, J_rho_O=J_rho_O, J_D=J_D, area=area)


def semicircular_plate(mass: QuantityLike, radius: QuantityLike) -> dict[str, Quantity]:
    """
    半圆板。
    文档表1-1-83 平面板-半圆板。

    :param mass: 质量(kg)
    :param radius: 半径(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²),
              'J_rho_O': 绕ρO轴(kg·m²), 'J_rho_G': 绕ρG轴(kg·m²),
              'y_bar': 质心距圆心(mm)}
    """
    m = set_quantity(mass, "kg")
    r = set_quantity(radius, "mm")
    _validate_positive(mass=m, radius=r)

    J_xy = _sum_inertia([(0.25, m, r)])  # m·r²/4
    J_rho_O = _sum_inertia([(0.5, m, r)])  # m·r²/2
    J_rho_G = _sum_inertia([(0.5 * (1.0 - 32.0 / (9.0 * math.pi**2)), m, r)])
    y_bar = (4.0 * r / (3.0 * math.pi)).to("m")
    area = (0.5 * math.pi * r**2).to("m**2")

    return inertia_result(
        Jx=J_xy,
        Jy=J_xy,
        J_rho_O=J_rho_O,
        J_rho_G=J_rho_G,
        y_bar=y_bar,
        area=area,
    )


def annular_plate(
    mass: QuantityLike, outer_radius: QuantityLike, inner_radius: QuantityLike
) -> dict[str, Quantity]:
    """
    圆环板（平面板）。
    文档表1-1-83 平面板-圆环。

    :param mass: 质量(kg)
    :param outer_radius: 外半径(mm)
    :param inner_radius: 内半径(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²), 'J_rho_O': 绕ρO轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    R = set_quantity(outer_radius, "mm")
    r = set_quantity(inner_radius, "mm")
    _validate_positive(mass=m, outer_radius=R, inner_radius=r)
    if float(r.magnitude) >= float(R.magnitude):
        raise ValueError("内半径必须小于外半径")

    J_xy = _sum_inertia([(0.25, m, R), (0.25, m, r)])  # m(R²+r²)/4
    J_rho_O = _sum_inertia([(0.5, m, R), (0.5, m, r)])  # m(R²+r²)/2

    area = (math.pi * (R**2 - r**2)).to("m**2")

    return inertia_result(Jx=J_xy, Jy=J_xy, J_rho_O=J_rho_O, area=area)


def sector_plate(
    mass: QuantityLike, radius: QuantityLike, alpha: QuantityLike
) -> dict[str, Quantity]:
    """
    扇形板。
    文档表1-1-83 平面板-扇形。

    :param mass: 质量(kg)
    :param radius: 半径(mm)
    :param alpha: 半张角(deg)，总张角 = 2α
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²),
              'J_rho_O': 绕ρO轴(kg·m²), 'J_rho_G': 绕ρG轴(kg·m²),
              'x_bar': 质心距圆心(mm)}
    """
    m = set_quantity(mass, "kg")
    r = set_quantity(radius, "mm")
    alpha_rad = _to_rad(alpha)
    _validate_positive(mass=m, radius=r)
    if alpha_rad <= 0 or alpha_rad > math.pi:
        raise ValueError("alpha 半张角应在 (0°, 180°] 范围内")

    sin2a = math.sin(2.0 * alpha_rad)
    J_x = (m * r**2 / 4.0 * (1.0 - sin2a / (2.0 * alpha_rad))).to("kg*m**2")
    J_y = (m * r**2 / 4.0 * (1.0 + sin2a / (2.0 * alpha_rad))).to("kg*m**2")
    J_rho_O = (m * r**2 / 2.0).to("kg*m**2")

    x_bar = (2.0 * r * math.sin(alpha_rad) / (3.0 * alpha_rad)).to("m")
    s = 2.0 * r * math.sin(alpha_rad)
    arc_len = 2.0 * alpha_rad * r
    J_rho_G = (m * r**2 / 2.0 * (1.0 - 8.0 * s**2 / (9.0 * arc_len**2))).to("kg*m**2")
    area = (alpha_rad * r**2).to("m**2")

    return inertia_result(
        Jx=J_x,
        Jy=J_y,
        J_rho_O=J_rho_O,
        J_rho_G=J_rho_G,
        x_bar=x_bar,
        area=area,
    )


def trapezoidal_plate(
    mass: QuantityLike, top_width: QuantityLike, bottom_width: QuantityLike, height: QuantityLike
) -> dict[str, Quantity]:
    """
    梯形板。
    文档表1-1-83 平面板-梯形。

    :param mass: 质量(kg)
    :param top_width: 上底长度(mm)
    :param bottom_width: 下底长度(mm)
    :param height: 高(mm)
    :return: {'J_a': 绕下底(kg·m²), 'J_b': 绕上底(kg·m²),
              'J_n': 绕重心平行底边(kg·m²), 'y_bar': 质心距下底(mm)}
    """
    m = set_quantity(mass, "kg")
    a_m = set_quantity(top_width, "mm")
    b_m = set_quantity(bottom_width, "mm")
    h_m = set_quantity(height, "mm")
    _validate_positive(mass=m, top_width=a_m, bottom_width=b_m, height=h_m)

    J_a = (m * h_m**2 * (a_m + 3.0 * b_m) / (6.0 * (a_m + b_m))).to("kg*m**2")
    J_b = (m * h_m**2 * (b_m + 3.0 * a_m) / (6.0 * (a_m + b_m))).to("kg*m**2")
    J_n = (m * h_m**2 * (a_m**2 + 4.0 * a_m * b_m + b_m**2) / (18.0 * (a_m + b_m) ** 2)).to(
        "kg*m**2"
    )
    y_bar = (h_m * (2.0 * a_m + b_m) / (3.0 * (a_m + b_m))).to("m")
    area = (0.5 * (a_m + b_m) * h_m).to("m**2")

    return inertia_result(J_a=J_a, J_b=J_b, J_n=J_n, y_bar=y_bar, area=area)


def regular_polygon_plate(
    mass: QuantityLike,
    n: QuantityLike,
    side_length: QuantityLike = None,
    inradius: QuantityLike = None,
    circumradius: QuantityLike = None,
) -> dict[str, Quantity]:
    """
    正 n 边形板。
    文档表1-1-83 平面板-正n边形。

    :param mass: 质量(kg)
    :param n: 边数(≥3)
    :param side_length: 边长(mm)，至少提供 side_length、inradius、circumradius 之一
    :param inradius: 内切圆半径(mm)
    :param circumradius: 外接圆半径(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²), 'J_rho_O': 绕ρO轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    if n < 3:
        raise ValueError("边数 n 必须 ≥ 3")

    if side_length is not None:
        a = set_quantity(side_length, "mm")
        r = a / (2.0 * math.tan(math.pi / n))
        R = a / (2.0 * math.sin(math.pi / n))
    elif inradius is not None:
        r = set_quantity(inradius, "mm")
        a = 2.0 * r * math.tan(math.pi / n)
        R = r / math.cos(math.pi / n)
    elif circumradius is not None:
        R = set_quantity(circumradius, "mm")
        r = R * math.cos(math.pi / n)
        a = 2.0 * R * math.sin(math.pi / n)
    else:
        raise ValueError("必须提供 side_length、inradius 或 circumradius 中的至少一个")

    _validate_positive(mass=m, side_length=a, inradius=r, circumradius=R)

    J_rho_O = _sum_inertia([(0.5, m, r), (1.0 / 24.0, m, a)])  # m(12r²+a²)/24
    J_xy = _sum_inertia([(0.25, m, r), (1.0 / 48.0, m, a)])  # m(12r²+a²)/48

    area = (0.5 * n * a * r).to("m**2")

    return inertia_result(Jx=J_xy, Jy=J_xy, J_rho_O=J_rho_O, area=area)


def circular_plate(mass: QuantityLike, radius: QuantityLike) -> dict[str, Quantity]:
    """
    圆板。
    文档表1-1-83 平面板-圆板。

    :param mass: 质量(kg)
    :param radius: 半径(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²), 'J_rho_O': 绕ρO轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    r = set_quantity(radius, "mm")
    _validate_positive(mass=m, radius=r)

    J_xy = _sum_inertia([(0.25, m, r)])  # m·r²/4
    J_rho_O = _sum_inertia([(0.5, m, r)])  # m·r²/2

    i_x = (r / 2.0).to("m")
    i_y = i_x
    i_rho_O = (r / math.sqrt(2.0)).to("m")
    area = (math.pi * r**2).to("m**2")

    return inertia_result(
        Jx=J_xy,
        Jy=J_xy,
        J_rho_O=J_rho_O,
        i_x=i_x,
        i_y=i_y,
        i_rho_O=i_rho_O,
        area=area,
    )


def segment_plate(
    mass: QuantityLike, radius: QuantityLike, alpha: QuantityLike
) -> dict[str, Quantity]:
    """
    弓形板。
    文档表1-1-83 平面板-弓形。

    :param mass: 质量(kg)
    :param radius: 半径(mm)
    :param alpha: 半张角(deg)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²),
              'J_rho_O': 绕ρO轴(kg·m²), 'x_bar': 质心距圆心(mm)}
    """
    m = set_quantity(mass, "kg")
    r = set_quantity(radius, "mm")
    alpha_rad = _to_rad(alpha)
    _validate_positive(mass=m, radius=r)
    if alpha_rad <= 0 or alpha_rad > math.pi:
        raise ValueError("alpha 半张角应在 (0°, 180°] 范围内")

    sin2a = math.sin(2.0 * alpha_rad)
    sin4a = math.sin(4.0 * alpha_rad)

    J_x = (m * r**2 / 4.0 * (1.0 - (2.0 * sin2a - sin4a) / (12.0 * alpha_rad))).to("kg*m**2")
    J_y = (m * r**2 / 4.0 * (1.0 + (2.0 * sin2a + sin4a) / (12.0 * alpha_rad))).to("kg*m**2")
    J_rho_O = (m * r**2 / 2.0 * (1.0 + (2.0 * sin2a - sin4a) / (12.0 * alpha_rad))).to("kg*m**2")

    x_bar = (
        4.0 * r * math.sin(alpha_rad) ** 3 / (3.0 * (2.0 * alpha_rad - math.sin(2.0 * alpha_rad)))
    ).to("m")
    area = (r**2 * (alpha_rad - math.sin(alpha_rad) * math.cos(alpha_rad))).to("m**2")

    return inertia_result(Jx=J_x, Jy=J_y, J_rho_O=J_rho_O, x_bar=x_bar, area=area)


def elliptical_plate(
    mass: QuantityLike, semi_major: QuantityLike, semi_minor: QuantityLike
) -> dict[str, Quantity]:
    """
    椭圆板。
    文档表1-1-83 平面板-椭圆形。

    :param mass: 质量(kg)
    :param semi_major: 半长轴(mm，x方向)
    :param semi_minor: 半短轴(mm，y方向)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²), 'J_rho_O': 绕ρO轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    a = set_quantity(semi_major, "mm")
    b = set_quantity(semi_minor, "mm")
    _validate_positive(mass=m, semi_major=a, semi_minor=b)

    J_x = _sum_inertia([(0.25, m, b)])  # m·b²/4
    J_y = _sum_inertia([(0.25, m, a)])  # m·a²/4
    J_rho_O = _sum_inertia([(0.25, m, a), (0.25, m, b)])  # m(a²+b²)/4

    area = (math.pi * a * b).to("m**2")

    return inertia_result(Jx=J_x, Jy=J_y, J_rho_O=J_rho_O, area=area)


def parabolic_plate(mass: QuantityLike, a: QuantityLike, b: QuantityLike) -> dict[str, Quantity]:
    """
    抛物线形板。
    文档表1-1-83 平面板-抛物线形。

    :param mass: 质量(kg)
    :param a: 抛物线特征宽度参数(mm)
    :param b: 抛物线特征高度参数(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²), 'J_rho_O': 绕ρO轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    a_m = set_quantity(a, "mm")
    b_m = set_quantity(b, "mm")
    _validate_positive(mass=m, a=a_m, b=b_m)

    J_x = _sum_inertia([(0.2, m, b_m)])  # m·b²/5
    J_y = _sum_inertia([(8.0 / 35.0, m, a_m)])  # 8m·a²/35
    J_rho_O = _sum_inertia([(1.0 / 7.0, m, a_m), (2.0 / 21.0, m, b_m)])  # m(3a²+2b²)/21

    y_bar = (2.0 * b_m / 5.0).to("m")
    area = (4.0 * a_m * b_m / 3.0).to("m**2")

    return inertia_result(Jx=J_x, Jy=J_y, J_rho_O=J_rho_O, y_bar=y_bar, area=area)
