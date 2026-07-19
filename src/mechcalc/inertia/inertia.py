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
from ..core.units import kg, mm, kg_m2, Q_


def solid_cylinder(mass, outer_diameter):
    """
    实心圆盘/圆柱惯量。

    :param mass: 质量(kg)
    :param outer_diameter: 外径(mm)
    :return: 转动惯量(kg·m²)
    """
    m = kg(mass)
    D = mm(outer_diameter)
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
    m = kg(mass)
    D = mm(outer_diameter)
    d = mm(inner_diameter)
    J = (m * (D ** 2 + d ** 2) / 8).to('kg * m ** 2')
    return J


def point_mass(mass, radius):
    """
    质点绕轴转动惯量。

    :param mass: 质量(kg)
    :param radius: 半径(mm)
    :return: 转动惯量(kg·m²)
    """
    m = kg(mass)
    r = mm(radius)
    J = (m * r ** 2).to('kg * m ** 2')
    return J


def straight_rod(mass, length):
    """
    直杆绕中心轴转动惯量。

    :param mass: 质量(kg)
    :param length: 长度(mm)
    :return: 转动惯量(kg·m²)
    """
    m = kg(mass)
    L = mm(length)
    J = (m * L ** 2 / 12).to('kg * m ** 2')
    return J


def conveyor_belt(mass, roller_diameter):
    """
    传送带等效转动惯量。

    :param mass: 质量(kg)
    :param roller_diameter: 滚筒直径(mm)
    :return: 转动惯量(kg·m²)
    """
    m = kg(mass)
    D = mm(roller_diameter)
    J = (m * (D / 2) ** 2).to('kg * m ** 2')
    return J


def ball_screw(mass, lead):
    """
    滚珠丝杠等效转动惯量。

    :param mass: 质量(kg)
    :param lead: 导程(mm)
    :return: 转动惯量(kg·m²)
    """
    m = kg(mass)
    P = mm(lead)
    J = (m * P ** 2 / (4 * math.pi ** 2)).to('kg * m ** 2')
    return J


def gear_rack(mass, pitch_diameter):
    """
    齿轮齿条等效转动惯量。

    :param mass: 质量(kg)
    :param pitch_diameter: 节圆直径(mm)
    :return: 转动惯量(kg·m²)
    """
    m = kg(mass)
    D = mm(pitch_diameter)
    J = (m * (math.pi * D / 2) ** 2).to('kg * m ** 2')
    return J


def gearbox(load_inertia, ratio):
    """
    减速机折算到电机侧的惯量。

    :param load_inertia: 负载惯量(kg·m²)
    :param ratio: 减速比(None)
    :return: 折算惯量(kg·m²)
    """
    J = kg_m2(load_inertia)
    i = float(ratio)
    J_ref = (J / i ** 2).to('kg * m ** 2')
    return J_ref
