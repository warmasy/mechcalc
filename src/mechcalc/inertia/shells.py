"""薄壳体类惯量计算

基于《机械设计手册》表 1-1-83 薄壳体部分。
"""

import math

from pint import Quantity

from ..core.units import QuantityLike, set_quantity
from ._utils import _make_tensor, _sum_inertia, _validate_positive, inertia_result


def truncated_cone_shell(
    mass: QuantityLike, bottom_radius: QuantityLike, top_radius: QuantityLike, height: QuantityLike
) -> dict[str, Quantity]:
    """
    截顶圆锥侧表面（薄壳）。
    文档表1-1-83 薄壳体-截顶圆锥侧表面。

    :param mass: 质量(kg)
    :param bottom_radius: 下底半径(mm)
    :param top_radius: 上底半径(mm)
    :param height: 高(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    R = set_quantity(bottom_radius, "mm")
    r = set_quantity(top_radius, "mm")
    h = set_quantity(height, "mm")
    _validate_positive(mass=m, bottom_radius=R, top_radius=r, height=h)
    if float(r.magnitude) >= float(R.magnitude):
        raise ValueError("上底半径必须小于下底半径")

    l = ((h**2 + (R - r) ** 2) ** 0.5).to("m")
    # 含比值修正项 (1 + 2Rr/(R+r)²)，保留原公式
    J_x = (m * (R**2 + r**2) / 4.0 + m * h**2 / 18.0 * (1.0 + 2.0 * R * r / (R + r) ** 2)).to(
        "kg*m**2"
    )
    J_y = _sum_inertia([(0.5, m, R), (0.5, m, r)])  # m(R²+r²)/2

    y_bar = (h * (R + 2.0 * r) / (3.0 * (R + r))).to("m")
    area = (math.pi * (R + r) * l).to("m**2")

    return inertia_result(
        Jx=J_x,
        Jy=J_y,
        y_bar=y_bar,
        area=area,
        tensor=_make_tensor(Jx=J_x, Jy=J_x, Jz=J_y),  # 旋转对称: 两个直径轴 = J_x
    )


def cylinder_lateral_shell(
    mass: QuantityLike, radius: QuantityLike, height: QuantityLike
) -> dict[str, Quantity]:
    """
    圆柱侧表面（薄壳）。
    文档表1-1-83 薄壳体-圆柱侧表面。

    :param mass: 质量(kg)
    :param radius: 半径(mm)
    :param height: 高(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²), 'J_n': 绕n轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    R = set_quantity(radius, "mm")
    h = set_quantity(height, "mm")
    _validate_positive(mass=m, radius=R, height=h)

    J_x = _sum_inertia([(0.5, m, R), (1.0 / 12.0, m, h)])  # m(R²/2 + h²/12)
    J_y = _sum_inertia([(1.0, m, R)])  # mR²
    J_n = _sum_inertia([(0.5, m, R), (1.0 / 3.0, m, h)])  # m(3R²+2h²)/6

    y_bar = (h / 2.0).to("m")
    area = (2.0 * math.pi * R * h).to("m**2")

    return inertia_result(
        Jx=J_x,
        Jy=J_y,
        J_n=J_n,
        y_bar=y_bar,
        area=area,
        tensor=_make_tensor(Jx=J_x, Jy=J_x, Jz=J_y),
    )


def cylinder_total_shell(
    mass: QuantityLike, radius: QuantityLike, height: QuantityLike
) -> dict[str, Quantity]:
    """
    圆柱全表面（薄壳：侧面 + 上下底）。
    文档表1-1-83 薄壳体-圆柱全表面。

    :param mass: 质量(kg)
    :param radius: 半径(mm)
    :param height: 高(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    R = set_quantity(radius, "mm")
    h = set_quantity(height, "mm")
    _validate_positive(mass=m, radius=R, height=h)

    A_lat = 2.0 * math.pi * R * h
    A_base = math.pi * R**2
    A_total = A_lat + 2.0 * A_base

    # J_x = 侧面绕直径轴(过质心) + 两底面绕直径轴(移轴 h/2)
    J_x = (m * (3.0 * R**2 * (R + 2.0 * h) + h**2 * (3.0 * R + h)) / (12.0 * (R + h))).to("kg*m**2")
    J_y = (m * R**2 * (R + 2.0 * h) / (2.0 * (R + h))).to("kg*m**2")

    y_bar = (h / 2.0).to("m")
    area = A_total.to("m**2")

    return inertia_result(
        Jx=J_x,
        Jy=J_y,
        y_bar=y_bar,
        area=area,
        tensor=_make_tensor(Jx=J_x, Jy=J_x, Jz=J_y),
    )


def cone_lateral_shell(
    mass: QuantityLike, bottom_radius: QuantityLike, height: QuantityLike
) -> dict[str, Quantity]:
    """
    圆锥侧表面（薄壳）。
    文档表1-1-83 薄壳体-圆锥侧表面。

    :param mass: 质量(kg)
    :param bottom_radius: 底面半径(mm)
    :param height: 高(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²), 'J_n': 绕n轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    R = set_quantity(bottom_radius, "mm")
    h = set_quantity(height, "mm")
    _validate_positive(mass=m, bottom_radius=R, height=h)

    l = ((R**2 + h**2) ** 0.5).to("m")
    J_x = _sum_inertia([(0.25, m, R), (1.0 / 18.0, m, h)])  # m(R²/4 + h²/18)
    J_y = _sum_inertia([(0.5, m, R)])  # mR²/2
    J_n = _sum_inertia([(0.25, m, R), (1.0 / 6.0, m, h)])  # m(3R²+2h²)/12

    y_bar = (h / 3.0).to("m")
    area = (math.pi * R * l).to("m**2")

    return inertia_result(
        Jx=J_x,
        Jy=J_y,
        J_n=J_n,
        y_bar=y_bar,
        area=area,
        tensor=_make_tensor(Jx=J_x, Jy=J_x, Jz=J_y),
    )


def hemisphere_shell(mass: QuantityLike, radius: QuantityLike) -> dict[str, Quantity]:
    """
    半球面（薄壳）。
    文档表1-1-83 薄壳体-半球面。

    :param mass: 质量(kg)
    :param radius: 半径(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²), 'J_n': 绕n轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    R = set_quantity(radius, "mm")
    _validate_positive(mass=m, radius=R)

    J_x = _sum_inertia([(5.0 / 12.0, m, R)])  # 5mR²/12
    J_y = _sum_inertia([(2.0 / 3.0, m, R)])  # 2mR²/3
    J_n = J_y

    y_bar = (R / 2.0).to("m")
    area = (2.0 * math.pi * R**2).to("m**2")

    return inertia_result(
        Jx=J_x,
        Jy=J_y,
        J_n=J_n,
        y_bar=y_bar,
        area=area,
        tensor=_make_tensor(Jx=J_x, Jy=J_x, Jz=J_y),
    )


def sphere_shell(mass: QuantityLike, radius: QuantityLike) -> dict[str, Quantity]:
    """
    全球面（薄壳）。
    文档表1-1-83 薄壳体-全球面。

    :param mass: 质量(kg)
    :param radius: 半径(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²), 'J_z': 绕z轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    R = set_quantity(radius, "mm")
    _validate_positive(mass=m, radius=R)

    J = _sum_inertia([(2.0 / 3.0, m, R)])  # 2mR²/3

    area = (4.0 * math.pi * R**2).to("m**2")

    return inertia_result(Jx=J, Jy=J, Jz=J, area=area)


def torus_shell(
    mass: QuantityLike, mean_radius: QuantityLike, tube_radius: QuantityLike
) -> dict[str, Quantity]:
    """
    圆环（薄壳）。
    文档表1-1-83 薄壳体-圆环。

    :param mass: 质量(kg)
    :param mean_radius: 圆环中径(mm)
    :param tube_radius: 圆环截面半径(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²), 'J_rho_O': 绕ρO轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    R = set_quantity(mean_radius, "mm")
    r = set_quantity(tube_radius, "mm")
    _validate_positive(mass=m, mean_radius=R, tube_radius=r)

    J_xy = _sum_inertia([(0.5, m, R), (0.375, m, r)])  # m(4R²+3r²)/8
    J_rho_O = _sum_inertia([(1.0, m, R), (0.75, m, r)])  # m(4R²+3r²)/4
    i_rho_O = (0.5 * (4.0 * R**2 + 3.0 * r**2) ** 0.5).to("m")
    area = (4.0 * math.pi**2 * R * r).to("m**2")

    return inertia_result(Jx=J_xy, Jy=J_xy, J_rho_O=J_rho_O, i_rho_O=i_rho_O, area=area)
