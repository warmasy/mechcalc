"""立体形状类惯量计算

基于《机械设计手册》表 1-1-83 立体形状部分。
"""

import math

from pint import Quantity

from ..core.units import Q_, QuantityLike, set_quantity
from ._utils import _disk_slice_Jx, _sum_inertia, _validate_positive, inertia_result


def cylinder(
    mass: QuantityLike, diameter: QuantityLike, length: QuantityLike
) -> dict[str, Quantity]:
    """
    圆柱体（长圆柱，立体形状）。

    :param mass: 质量(kg)
    :param diameter: 直径(mm)
    :param length: 长度(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕中心轴(kg·m²), 'J_z': 绕z轴(kg·m²),
              'y_bar': 质心距底面(mm)}
    """
    m = set_quantity(mass, "kg")
    D = set_quantity(diameter, "mm")
    h = set_quantity(length, "mm")
    _validate_positive(mass=m, diameter=D, length=h)

    R = D / 2.0
    J_x = J_z = _sum_inertia([(0.25, m, R), (1.0 / 12.0, m, h)])  # m(3R²+h²)/12
    J_y = _sum_inertia([(0.5, m, R)])  # mR²/2

    y_bar = (h / 2.0).to("m")
    volume = (math.pi * R**2 * h).to("m**3")

    return inertia_result(Jx=J_x, Jy=J_y, Jz=J_z, y_bar=y_bar, volume=volume)


def tube(
    mass: QuantityLike,
    outer_diameter: QuantityLike,
    inner_diameter: QuantityLike,
    length: QuantityLike,
) -> dict[str, Quantity]:
    """
    圆筒体（长圆筒，立体形状）。

    :param mass: 质量(kg)
    :param outer_diameter: 外径(mm)
    :param inner_diameter: 内径(mm)
    :param length: 长度(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕中心轴(kg·m²), 'J_z': 绕z轴(kg·m²),
              'y_bar': 质心距底面(mm)}
    """
    m = set_quantity(mass, "kg")
    D = set_quantity(outer_diameter, "mm")
    d = set_quantity(inner_diameter, "mm")
    h = set_quantity(length, "mm")
    _validate_positive(mass=m, outer_diameter=D, inner_diameter=d, length=h)
    if float(d.magnitude) >= float(D.magnitude):
        raise ValueError("内径必须小于外径")

    R, r = D / 2.0, d / 2.0
    k3_12 = 3.0 / 12.0
    J_x = _sum_inertia([(k3_12, m, R), (k3_12, m, r), (1.0 / 12.0, m, h)])  # m(3(R²+r²)+h²)/12
    J_y = _sum_inertia([(0.5, m, R), (0.5, m, r)])  # m(R²+r²)/2

    y_bar = (h / 2.0).to("m")
    volume = (math.pi * (R**2 - r**2) * h).to("m**3")

    return inertia_result(Jx=J_x, Jy=J_y, Jz=J_x, y_bar=y_bar, volume=volume)


def rectangular_prism(
    mass: QuantityLike, a: QuantityLike, b: QuantityLike, h: QuantityLike
) -> dict[str, Quantity]:
    """
    矩形棱柱。

    :param mass: 质量(kg)
    :param a: 底面边长(mm)
    :param b: 底面边长(mm)
    :param h: 高度(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²), 'J_z': 绕z轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    a = set_quantity(a, "mm")
    b = set_quantity(b, "mm")
    h = set_quantity(h, "mm")
    _validate_positive(mass=m, a=a, b=b, h=h)

    k12 = 1.0 / 12.0
    J_x = _sum_inertia([(k12, m, b), (k12, m, h)])  # m(b²+h²)/12
    J_y = _sum_inertia([(k12, m, a), (k12, m, b)])  # m(a²+b²)/12
    J_z = _sum_inertia([(k12, m, a), (k12, m, h)])  # m(a²+h²)/12

    volume = (a * b * h).to("m**3")

    return inertia_result(Jx=J_x, Jy=J_y, Jz=J_z, volume=volume)


def right_pyramid(
    mass: QuantityLike, a: QuantityLike, b: QuantityLike, h: QuantityLike
) -> dict[str, Quantity]:
    """
    正直角锥体（底面为矩形的四棱锥）。
    文档表1-1-83 立体形状-正直角锥体。

    :param mass: 质量(kg)
    :param a: 底面矩形边长(mm)
    :param b: 底面矩形边长(mm)
    :param h: 高(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²),
              'J_z': 绕z轴(kg·m²), 'y_bar': 质心距底面(mm)}
    """
    m = set_quantity(mass, "kg")
    a_m = set_quantity(a, "mm")
    b_m = set_quantity(b, "mm")
    h_m = set_quantity(h, "mm")
    _validate_positive(mass=m, a=a_m, b=b_m, h=h_m)

    k20 = 1.0 / 20.0
    k34 = 0.75 / 20.0
    J_x = _sum_inertia([(k20, m, b_m), (k34, m, h_m)])  # m(b²+0.75h²)/20
    J_y = _sum_inertia([(k20, m, a_m), (k34, m, h_m)])  # m(a²+0.75h²)/20
    J_z = _sum_inertia([(k20, m, a_m), (k20, m, b_m)])  # m(a²+b²)/20
    y_bar = (h_m / 4.0).to("m")
    volume = (a_m * b_m * h_m / 3.0).to("m**3")

    return inertia_result(Jx=J_x, Jy=J_y, Jz=J_z, y_bar=y_bar, volume=volume)


def triangular_prism(
    mass: QuantityLike, side_length: QuantityLike, height: QuantityLike
) -> dict[str, Quantity]:
    """
    正三角柱（底面为正三角形）。
    文档表1-1-83 立体形状-正三角柱。

    :param mass: 质量(kg)
    :param side_length: 底面正三角形边长(mm)
    :param height: 柱高(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²), 'J_z': 绕z轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    a_m = set_quantity(side_length, "mm")
    h_m = set_quantity(height, "mm")
    _validate_positive(mass=m, side_length=a_m, height=h_m)

    J_xy = _sum_inertia([(1.0 / 24.0, m, a_m), (1.0 / 12.0, m, h_m)])  # m(a²+2h²)/24
    J_z = _sum_inertia([(1.0 / 12.0, m, a_m)])  # m·a²/12

    y_bar = (h_m / 2.0).to("m")
    volume = (math.sqrt(3.0) * a_m**2 * h_m / 4.0).to("m**3")

    return inertia_result(Jx=J_xy, Jy=J_xy, Jz=J_z, y_bar=y_bar, volume=volume)


def truncated_cone(
    mass: QuantityLike, bottom_radius: QuantityLike, top_radius: QuantityLike, height: QuantityLike
) -> dict[str, Quantity]:
    """
    截顶圆锥体。
    文档表1-1-83 立体形状-截顶圆锥体。

    :param mass: 质量(kg)
    :param bottom_radius: 下底半径(mm)
    :param top_radius: 上底半径(mm)
    :param height: 高(mm)
    :return: {'J_y': 绕中心轴(kg·m²), 'y_bar': 质心距大底面(mm)}
    """
    m = set_quantity(mass, "kg")
    R = set_quantity(bottom_radius, "mm")
    r = set_quantity(top_radius, "mm")
    h_m = set_quantity(height, "mm")
    _validate_positive(mass=m, bottom_radius=R, top_radius=r, height=h_m)
    if float(r.magnitude) >= float(R.magnitude):
        raise ValueError("上底半径必须小于下底半径")

    J_y = ((3.0 * m / 10.0) * (R**5 - r**5) / (R**3 - r**3)).to("kg*m**2")
    y_bar = (h_m * (R**2 + 2.0 * R * r + 3.0 * r**2) / (4.0 * (R**2 + R * r + r**2))).to("m")
    volume = math.pi * h_m * (R**2 + R * r + r**2) / 3.0

    # 旋转对称体: 绕任意直径轴惯量相同。圆盘切片数值积分补全 Jx = Jz
    R_m = R.to("m").magnitude
    r_m = r.to("m").magnitude
    h_v = h_m.to("m").magnitude
    ybar_m = y_bar.to("m").magnitude
    m_kg = m.to("kg").magnitude
    Jx_val = _disk_slice_Jx(
        mass=m_kg,
        ybar=ybar_m,
        radii_at_z=lambda z: R_m - (R_m - r_m) * z / h_v,
        z0=0.0,
        z1=h_v,
    )
    J_x = Q_(Jx_val, "kg*m**2")
    volume_q = volume.to("m**3")

    return inertia_result(Jx=J_x, Jy=J_x, Jz=J_y, y_bar=y_bar, volume=volume_q)


def sphere(mass: QuantityLike, radius: QuantityLike) -> dict[str, Quantity]:
    """
    圆球。
    文档表1-1-83 立体形状-圆球。

    :param mass: 质量(kg)
    :param radius: 半径(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²), 'J_z': 绕z轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    R = set_quantity(radius, "mm")
    _validate_positive(mass=m, radius=R)

    J = _sum_inertia([(0.4, m, R)])  # 2/5·mR²

    volume = (4.0 * math.pi * R**3 / 3.0).to("m**3")

    return inertia_result(Jx=J, Jy=J, Jz=J, volume=volume)


def hollow_sphere(
    mass: QuantityLike, outer_radius: QuantityLike, inner_radius: QuantityLike
) -> dict[str, Quantity]:
    """
    空心圆球。
    文档表1-1-83 立体形状-空心圆球。

    :param mass: 质量(kg)
    :param outer_radius: 外半径(mm)
    :param inner_radius: 内半径(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²), 'J_z': 绕z轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    R = set_quantity(outer_radius, "mm")
    r = set_quantity(inner_radius, "mm")
    _validate_positive(mass=m, outer_radius=R, inner_radius=r)
    if float(r.magnitude) >= float(R.magnitude):
        raise ValueError("内半径必须小于外半径")

    J = ((2.0 * m / 5.0) * (R**5 - r**5) / (R**3 - r**3)).to("kg*m**2")

    volume = (4.0 * math.pi * (R**3 - r**3) / 3.0).to("m**3")

    return inertia_result(Jx=J, Jy=J, Jz=J, volume=volume)


def cone(
    mass: QuantityLike, bottom_diameter: QuantityLike, height: QuantityLike
) -> dict[str, Quantity]:
    """
    直圆锥体。
    文档表1-1-83 立体形状-直圆锥体。

    :param mass: 质量(kg)
    :param bottom_diameter: 底面直径(mm)
    :param height: 高(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕中心轴(kg·m²), 'J_z': 绕z轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    D = set_quantity(bottom_diameter, "mm")
    h_m = set_quantity(height, "mm")
    _validate_positive(mass=m, bottom_diameter=D, height=h_m)

    R = D / 2.0
    J_x = _sum_inertia([(0.15, m, R), (0.15 / 4.0, m, h_m)])  # 3m(R²+h²/4)/20
    J_y = _sum_inertia([(0.3, m, R)])  # 3mR²/10
    y_bar = (h_m / 4.0).to("m")
    volume = (math.pi * R**2 * h_m / 3.0).to("m**3")

    return inertia_result(Jx=J_x, Jy=J_y, Jz=J_x, y_bar=y_bar, volume=volume)


def spherical_cap(
    mass: QuantityLike, sphere_radius: QuantityLike, cap_height: QuantityLike
) -> dict[str, Quantity]:
    """
    球冠（立体）。
    文档表1-1-83 立体形状-球冠。

    :param mass: 质量(kg)
    :param sphere_radius: 球半径(mm)
    :param cap_height: 冠高(mm)
    :return: {'J_y': 绕对称轴(kg·m²), 'y_bar': 质心距球冠底面(mm)}
    """
    m = set_quantity(mass, "kg")
    R = set_quantity(sphere_radius, "mm")
    h = set_quantity(cap_height, "mm")
    _validate_positive(mass=m, sphere_radius=R, cap_height=h)
    if float(h.magnitude) > 2.0 * float(R.magnitude):
        raise ValueError("冠高不能大于球直径")

    R_m = R.to("m")
    h_m = h.to("m")
    J_y = ((2.0 * m * h_m / (3.0 * R_m - h_m)) * (R_m**2 - 0.75 * R_m * h_m + 0.15 * h_m**2)).to(
        "kg*m**2"
    )
    # 手册原式 y_bar = h(2R-h)²/(4(3R-h)) 量纲为 L²，修正为标准公式 y_bar = 3(2R-h)²/(4(3R-h))
    y_bar = (3.0 * (2.0 * R_m - h_m) ** 2 / (4.0 * (3.0 * R_m - h_m))).to("m")
    volume = math.pi * h_m**2 * (3.0 * R_m - h_m) / 3.0

    # 旋转对称体: 绕任意直径轴惯量相同。圆盘切片数值积分补全 Jx = Jz
    Rv = R_m.magnitude
    hv = h_m.magnitude
    ybar_m = y_bar.to("m").magnitude
    m_kg = m.to("kg").magnitude
    # 球冠底面在 z=0，球心在 z = R-h，切片半径 r(z) = sqrt(R² - (z - (R-h))²)
    zc = Rv - hv
    Jx_val = _disk_slice_Jx(
        mass=m_kg,
        ybar=ybar_m,
        radii_at_z=lambda z: math.sqrt(max(Rv**2 - (z - zc) ** 2, 0.0)),
        z0=0.0,
        z1=hv,
    )
    J_x = Q_(Jx_val, "kg*m**2")
    volume_q = volume.to("m**3")

    return inertia_result(Jx=J_x, Jy=J_x, Jz=J_y, y_bar=y_bar, volume=volume_q)


def elliptical_torus(
    mass: QuantityLike,
    mean_radius: QuantityLike,
    semi_major: QuantityLike,
    semi_minor: QuantityLike,
) -> dict[str, Quantity]:
    """
    椭圆截面圆环（立体）。
    文档表1-1-83 立体形状-椭圆截面圆环。

    :param mass: 质量(kg)
    :param mean_radius: 圆环中径(mm，中心到截面中心的距离)
    :param semi_major: 截面椭圆半轴(mm，径向)
    :param semi_minor: 截面椭圆半轴(mm，轴向)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    R = set_quantity(mean_radius, "mm")
    a = set_quantity(semi_major, "mm")
    b = set_quantity(semi_minor, "mm")
    _validate_positive(mass=m, mean_radius=R, semi_major=a, semi_minor=b)

    J_x = _sum_inertia([(0.5, m, R), (0.375, m, a), (0.25, m, b)])  # m(4R²+3a²+2b²)/8
    J_y = _sum_inertia([(0.5, m, R), (0.375, m, a), (0.375, m, b)])  # m(4R²+3a²+3b²)/8

    volume = (2.0 * math.pi**2 * R * a * b).to("m**3")

    return inertia_result(Jx=J_x, Jy=J_y, volume=volume)


def rectangular_torus(
    mass: QuantityLike,
    mean_radius: QuantityLike,
    radial_thickness: QuantityLike,
    axial_width: QuantityLike,
) -> dict[str, Quantity]:
    """
    矩形截面圆环（立体）。
    文档表1-1-83 立体形状-矩形截面圆环。

    :param mass: 质量(kg)
    :param mean_radius: 圆环中径(mm)
    :param radial_thickness: 截面径向厚度(mm)
    :param axial_width: 截面轴向宽度(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²)}
    """
    m = set_quantity(mass, "kg")
    R = set_quantity(mean_radius, "mm")
    a = set_quantity(radial_thickness, "mm")
    b = set_quantity(axial_width, "mm")
    _validate_positive(mass=m, mean_radius=R, radial_thickness=a, axial_width=b)

    J_x = _sum_inertia([(0.5, m, R), (1.0 / 12.0, m, a)])  # m(6R²+a²)/12
    J_y = _sum_inertia([(0.5, m, R), (1.0 / 12.0, m, a), (1.0 / 12.0, m, b)])  # m(6R²+a²+b²)/12

    volume = (2.0 * math.pi * R * a * b).to("m**3")

    return inertia_result(Jx=J_x, Jy=J_y, volume=volume)


def hemisphere(mass: QuantityLike, radius: QuantityLike) -> dict[str, Quantity]:
    """
    半球（立体）。
    文档表1-1-83 立体形状-半球。

    :param mass: 质量(kg)
    :param radius: 半径(mm)
    :return: {'J_x': 绕x轴(kg·m²), 'J_y': 绕y轴(kg·m²), 'J_z': 绕z轴(kg·m²),
              'y_bar': 质心距球心(mm)}
    """
    m = set_quantity(mass, "kg")
    R = set_quantity(radius, "mm")
    _validate_positive(mass=m, radius=R)

    J_xz = _sum_inertia([(83.0 / 320.0, m, R)])  # 83/320·mR²
    J_y = _sum_inertia([(0.4, m, R)])  # 2/5·mR²
    y_bar = (3.0 * R / 8.0).to("m")
    volume = (2.0 * math.pi * R**3 / 3.0).to("m**3")

    return inertia_result(Jx=J_xz, Jy=J_y, Jz=J_xz, y_bar=y_bar, volume=volume)
