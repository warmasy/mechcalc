"""细杆类惯量计算

基于《机械设计手册》表 1-1-83 细杆部分。
"""

import math

from pint import Quantity

from ..core.units import Q_, QuantityLike, set_quantity
from ._utils import _sum_inertia, _to_deg, _to_rad, _validate_positive, inertia_result


def arc_rod(mass: QuantityLike, radius: QuantityLike, alpha: QuantityLike) -> dict[str, Quantity]:
    """
    圆弧杆（细杆弯成圆弧）。
    文档表1-1-83 细杆-圆弧杆。

    :param mass: 质量(kg)
    :param radius: 圆弧半径(mm)
    :param alpha: 半张角(deg)，总张角 = 2α
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²),
              'J_y_prime': 绕y\'轴(kg·m²), 'J_rho_O': 绕ρO\'轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    R = set_quantity(radius, "mm")
    alpha_rad = _to_rad(alpha)
    _validate_positive(mass=m, radius=R, alpha=alpha_rad)
    if alpha_rad <= 0 or alpha_rad > math.pi:
        raise ValueError("alpha 半张角应在 (0°, 180°] 范围内")

    sin_a = math.sin(alpha_rad)
    cos_a = math.cos(alpha_rad)

    J_x = (m * R**2 * (0.5 - sin_a * cos_a / (2.0 * alpha_rad))).to("kg*m**2")
    J_y_prime = (m * R**2 * (0.5 + sin_a * cos_a / (2.0 * alpha_rad))).to("kg*m**2")
    J_y = (m * R**2 * ((0.5 + sin_a * cos_a / (2.0 * alpha_rad)) - (sin_a / alpha_rad) ** 2)).to(
        "kg*m**2"
    )
    J_rho_O = (m * R**2).to("kg*m**2")

    x_bar = (R * sin_a / alpha_rad).to("m")
    arc_length = (2.0 * alpha_rad * R).to("m")

    return inertia_result(
        Jx=J_x,
        Jy=J_y,
        J_rho_O=J_rho_O,
        J_y_prime=J_y_prime,
        x_bar=x_bar,
        arc_length=arc_length,
    )


def u_rod(mass: QuantityLike, l1: QuantityLike, l2: QuantityLike) -> dict[str, Quantity]:
    """
    U 形杆（细杆组成）。
    文档表1-1-83 细杆-U形杆。

    :param mass: 总质量(kg)
    :param l1: 两侧竖直段长度(mm)
    :param l2: 底部水平段长度(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²),
              'i_x': 回转半径(m), 'i_y': 回转半径(m),
              'x_bar': 质心x(m), 'y_bar': 质心y(m)}
    """
    m = set_quantity(mass, "kg")
    l1_m = set_quantity(l1, "mm")
    l2_m = set_quantity(l2, "mm")
    _validate_positive(mass=m, l1=l1_m, l2=l2_m)

    total_len = 2.0 * l1_m + l2_m
    J_x = (m * l2_m**2 * (l1_m + 6.0 * l2_m) / (12.0 * total_len)).to("kg*m**2")
    J_y = (m * l2_m**2 * (2.0 * l1_m + l2_m) / (3.0 * total_len)).to("kg*m**2")

    i_x = (J_x / m) ** 0.5
    i_y = (J_y / m) ** 0.5

    y_bar = (l1_m**2 / total_len).to("m")
    x_bar = (l2_m / 2.0).to("m")
    total_length = total_len.to("m")

    return inertia_result(
        Jx=J_x,
        Jy=J_y,
        plane=True,
        i_x=i_x,
        i_y=i_y,
        x_bar=x_bar,
        y_bar=y_bar,
        total_length=total_length,
    )


def cylindrical_rod(
    mass: QuantityLike, l1: QuantityLike, l2: QuantityLike, alpha: QuantityLike
) -> dict[str, Quantity]:
    """
    圆柱杆（有直径的直杆，倾斜放置）。
    文档表1-1-83 细杆-直杆（有直径）。

    :param mass: 质量(kg)
    :param l1: 转轴 O 到杆下端距离(mm，沿杆)
    :param l2: 转轴 O 到杆上端距离(mm，沿杆)
    :param alpha: 杆与水平方向(x轴)的夹角(deg)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²), 'J_z': 绕z轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    l1_m = set_quantity(l1, "mm")
    l2_m = set_quantity(l2, "mm")
    alpha_rad = _to_rad(alpha)
    _validate_positive(mass=m, l1=l1_m, l2=l2_m)

    L2 = l1_m**2 - l1_m * l2_m + l2_m**2
    sin_a = math.sin(alpha_rad)
    cos_a = math.cos(alpha_rad)

    J_x = ((m / 3.0) * sin_a**2 * L2).to("kg*m**2")
    J_y = ((m / 3.0) * cos_a**2 * L2).to("kg*m**2")
    J_z = ((m * L2) / 3.0).to("kg*m**2")

    total_length = (l1_m + l2_m).to("m")

    return inertia_result(Jx=J_x, Jy=J_y, Jz=J_z, total_length=total_length)


def rectangular_frame_rod(
    mass: QuantityLike, l1: QuantityLike, l2: QuantityLike
) -> dict[str, Quantity]:
    """
    矩形杆框（细杆组成的矩形框）。
    文档表1-1-83 细杆-矩形杆。

    :param mass: 总质量(kg)
    :param l1: 竖直边长度(mm)
    :param l2: 水平边长度(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²),
              'i_x': 回转半径(m), 'i_y': 回转半径(m)}
    """
    m = set_quantity(mass, "kg")
    l1_m = set_quantity(l1, "mm")
    l2_m = set_quantity(l2, "mm")
    _validate_positive(mass=m, l1=l1_m, l2=l2_m)

    total_len = 2.0 * (l1_m + l2_m)
    J_x = (m * l1_m**2 * (l1_m + 3.0 * l2_m) / (12.0 * total_len)).to("kg*m**2")
    J_y = (m * l2_m**2 * (3.0 * l1_m + l2_m) / (12.0 * total_len)).to("kg*m**2")

    i_x = (J_x / m) ** 0.5
    i_y = (J_y / m) ** 0.5

    x_bar = (l2_m / 2.0).to("m")
    y_bar = (l1_m / 2.0).to("m")
    total_length = total_len.to("m")

    return inertia_result(
        Jx=J_x,
        Jy=J_y,
        plane=True,
        i_x=i_x,
        i_y=i_y,
        x_bar=x_bar,
        y_bar=y_bar,
        total_length=total_length,
    )


def elliptical_ring_rod(
    mass: QuantityLike, a: QuantityLike, b: QuantityLike
) -> dict[str, Quantity]:
    """
    椭圆杆（细杆弯成椭圆环）。
    文档表1-1-83 细杆-椭圆杆。

    :param mass: 质量(kg)
    :param a: 椭圆半长轴(mm，x方向)
    :param b: 椭圆半短轴(mm，y方向)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²), 'J_rho_O': 绕ρO轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    a_m = set_quantity(a, "mm")
    b_m = set_quantity(b, "mm")
    _validate_positive(mass=m, a=a_m, b=b_m)

    a2 = a_m**2
    a4 = a_m**4
    b2 = b_m**2
    b4 = b_m**4

    denom = 2.0 * (45.0 * a4 + 22.0 * a2 * b2 - 3.0 * b4)
    if abs(float(denom.magnitude)) < 1e-15:
        raise ValueError("椭圆参数导致分母为零，请检查 a、b 值")

    J_x = (m * b2 * (55.0 * a4 + 10.0 * a2 * b2 - 3.0 * b4) / denom).to("kg*m**2")
    J_y = (m * a2 * (35.0 * a4 + 34.0 * a2 * b2 - 5.0 * b4) / denom).to("kg*m**2")
    J_rho_O = (m * (a2 + b2) / 2.0).to("kg*m**2")

    x_bar = Q_(0.0, "m")
    y_bar = Q_(0.0, "m")

    return inertia_result(Jx=J_x, Jy=J_y, J_rho_O=J_rho_O, x_bar=x_bar, y_bar=y_bar)


def circular_ring_rod(mass: QuantityLike, radius: QuantityLike) -> dict[str, Quantity]:
    """
    圆环杆（细杆弯成圆环）。
    文档表1-1-83 细杆-圆环杆。

    :param mass: 质量(kg)
    :param radius: 圆环半径(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²), 'J_rho_O': 绕ρO轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    R = set_quantity(radius, "mm")
    _validate_positive(mass=m, radius=R)

    J_xy = _sum_inertia([(0.5, m, R)])  # 1/2·mR²（绕直径）
    J_rho_O = _sum_inertia([(1.0, m, R)])  # mR²（绕中心轴）

    i_x = (J_xy / m) ** 0.5
    i_y = i_x
    i_rho_O = (J_rho_O / m) ** 0.5
    arc_length = (2.0 * math.pi * R).to("m")

    return inertia_result(
        Jx=J_xy,
        Jy=J_xy,
        J_rho_O=J_rho_O,
        i_x=i_x,
        i_y=i_y,
        i_rho_O=i_rho_O,
        arc_length=arc_length,
    )


def point_mass(mass: QuantityLike, radius: QuantityLike) -> Quantity:
    """
    质点绕轴转动惯量。

    :param mass: 质量(kg)
    :param radius: 半径(mm)
    :return: 转动惯量(kg·m²)
    """
    m = set_quantity(mass, "kg")
    r = set_quantity(radius, "mm")
    return _sum_inertia([(1.0, m, r)])  # m·r²


def inclined_rod(
    mass: QuantityLike, length: QuantityLike, alpha: QuantityLike, r: QuantityLike = 0
) -> dict[str, Quantity]:
    """
    倾斜直杆的转动惯量（杆与转轴夹角为 α，质心在 l/2 处）。

    J_a = m·(r² + (l·sinα)²/12)   转轴 a：距质心垂直距离 r 的平行轴
    J_b = m·(l·sinα)²/3           转轴 b：过杆端点
    J_c = m·(l·sinα)²/12          转轴 c：过质心
    J_z = m·l²/12                 z 轴：过质心且垂直于杆

    α=90° 时 J_c 退化为细杆绕中点（mL²/12）的结果。

    :param mass: 质量(kg)
    :param length: 杆长(mm)
    :param alpha: 杆与转轴的夹角(deg)，Quantity 时支持 rad
    :param r: 转轴 a 到质心的垂直距离(mm)，默认 0
    :return: {'J_a': 绕轴a惯量(kg·m²), 'J_b': 绕轴b惯量(kg·m²),
              'J_c': 绕轴c惯量(kg·m²), 'J_z': 绕z轴惯量(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    l = set_quantity(length, "mm")
    r_q = set_quantity(r, "mm")
    alpha_deg = _to_deg(alpha)

    ls = (l * math.sin(math.radians(alpha_deg))).to("m")  # 有效长度 = l·sinα

    J_z = _sum_inertia([(1.0 / 12.0, m, l)])  # mL²/12
    J_c = _sum_inertia([(1.0 / 12.0, m, ls)])  # m(l·sinα)²/12
    J_b = _sum_inertia([(1.0 / 3.0, m, ls)])  # m(l·sinα)²/3
    J_a = _sum_inertia([(1.0, m, r_q), (1.0 / 12.0, m, ls)])  # m·r² + m(l·sinα)²/12

    return inertia_result(
        Jx=Q_(0.0, "kg*m**2"),
        Jy=J_z,
        Jz=J_z,  # 杆沿 x 放置的质心系张量
        J_a=J_a,
        J_b=J_b,
        J_c=J_c,
    )
