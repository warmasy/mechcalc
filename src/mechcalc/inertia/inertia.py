"""惯量计算模块

提供常见几何体的转动惯量计算公式。

用法:
    # 默认：返回原始 pint Quantity（内部链式计算）
    J = solid_cylinder(10, 100)
    print(J.to('kg*m**2'))   # 0.0125 kg·m²

    # 需要 Result（带参数记录和单位）时：
    result = to_result(solid_cylinder, 10, 100)
    print(result.value)      # {'value': 0.0125, 'unit': 'kg·m²'}
"""

import math
from ..core.units import Q_, to_mag, ensure_quantity


def solid_cylinder(mass, outer_diameter):
    """
    实心圆盘/圆柱惯量。

    :param mass: 质量(kg)
    :param outer_diameter: 外径(mm)
    :return: 转动惯量(kg·m²)
    """
    m = ensure_quantity(mass, 'kg')
    D = ensure_quantity(outer_diameter, 'mm')
    J = (m * D ** 2 / 8).to('kg * m ** 2')
    return J


def hollow_cylinder(mass, outer_diameter, inner_diameter):
    """
    空心圆盘/圆柱惯量。

    :param mass: 质量(kg)
    :param outer_diameter: 外径(mm)
    :param inner_diameter: 内径(mm)
    :return: 转动惯量(kg·m²)
    """
    m = ensure_quantity(mass, 'kg')
    D = ensure_quantity(outer_diameter, 'mm')
    d = ensure_quantity(inner_diameter, 'mm')
    J = (m * (D ** 2 + d ** 2) / 8).to('kg * m ** 2')
    return J


def point_mass(mass, radius):
    """
    质点绕轴转动惯量。

    :param mass: 质量(kg)
    :param radius: 半径(mm)
    :return: 转动惯量(kg·m²)
    """
    m = ensure_quantity(mass, 'kg')
    r = ensure_quantity(radius, 'mm')
    J = (m * r ** 2).to('kg * m ** 2')
    return J


def straight_rod(mass, length):
    """
    直杆绕中心轴转动惯量。

    :param mass: 质量(kg)
    :param length: 长度(mm)
    :return: 转动惯量(kg·m²)
    """
    m = ensure_quantity(mass, 'kg')
    L = ensure_quantity(length, 'mm')
    J = (m * L ** 2 / 12).to('kg * m ** 2')
    return J


def conveyor_belt(mass, roller_diameter):
    """
    传送带等效转动惯量。

    :param mass: 质量(kg)
    :param roller_diameter: 滚筒直径(mm)
    :return: 转动惯量(kg·m²)
    """
    m = ensure_quantity(mass, 'kg')
    D = ensure_quantity(roller_diameter, 'mm')
    J = (m * (D / 2) ** 2).to('kg * m ** 2')
    return J


def ball_screw(mass, lead):
    """
    滚珠丝杠等效转动惯量。

    :param mass: 质量(kg)
    :param lead: 导程(mm)
    :return: 转动惯量(kg·m²)
    """
    m = ensure_quantity(mass, 'kg')
    P = ensure_quantity(lead, 'mm')
    J = (m * P ** 2 / (4 * math.pi ** 2)).to('kg * m ** 2')
    return J


def gear_rack(mass, pitch_diameter):
    """
    齿轮齿条等效转动惯量。

    :param mass: 质量(kg)
    :param pitch_diameter: 节圆直径(mm)
    :return: 转动惯量(kg·m²)
    """
    m = ensure_quantity(mass, 'kg')
    D = ensure_quantity(pitch_diameter, 'mm')
    J = (m * (math.pi * D / 2) ** 2).to('kg * m ** 2')
    return J


def gearbox(load_inertia, ratio):
    """
    减速机折算到电机侧的惯量。

    :param load_inertia: 负载惯量(kg·m²)
    :param ratio: 减速比(None)
    :return: 折算惯量(kg·m²)
    """
    J = ensure_quantity(load_inertia, 'kg*m**2')
    i = float(ratio)
    J_ref = (J / i ** 2).to('kg * m ** 2')
    return J_ref


def inclined_rod(mass, length, alpha, r=0):
    """
    倾斜直杆的转动惯量（杆与转轴夹角为 α，质心在 l/2 处）。

    J_a = m·(r² + (l·sinα)²/12)   转轴 a：距质心垂直距离 r 的平行轴
    J_b = m·(l·sinα)²/3           转轴 b：过杆端点
    J_c = m·(l·sinα)²/12          转轴 c：过质心
    J_z = m·l²/12                 z 轴：过质心且垂直于杆

    α=90° 时 J_c 退化为 straight_rod 的结果。

    :param mass: 质量(kg)
    :param length: 杆长(mm)
    :param alpha: 杆与转轴的夹角(deg)，Quantity 时支持 rad
    :param r: 转轴 a 到质心的垂直距离(mm)，默认 0
    :return: {'J_a': 绕轴a惯量(kg·m²), 'J_b': 绕轴b惯量(kg·m²),
              'J_c': 绕轴c惯量(kg·m²), 'J_z': 绕z轴惯量(kg·m²)}
    """
    m_q = ensure_quantity(mass, 'kg')
    l = ensure_quantity(length, 'mm')
    r_q = ensure_quantity(r, 'mm')
    if hasattr(alpha, 'magnitude'):
        alpha = float(alpha.to('deg').magnitude)

    m_val = to_mag(m_q, 'kg')
    l_m = to_mag(l, 'm')
    r_m = to_mag(r_q, 'm')
    ls = l_m * math.sin(math.radians(alpha))

    return {
        'J_a': Q_(m_val * (r_m ** 2 + ls ** 2 / 12), 'kg*m**2'),
        'J_b': Q_(m_val * ls ** 2 / 3, 'kg*m**2'),
        'J_c': Q_(m_val * ls ** 2 / 12, 'kg*m**2'),
        'J_z': Q_(m_val * l_m ** 2 / 12, 'kg*m**2'),
    }
