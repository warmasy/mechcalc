"""工程机构等效惯量计算

滚珠丝杠、齿轮齿条、减速机等机构的惯量折算。
这些不是纯粹几何体惯量，而是工程应用中的等效计算。
（传送带等效惯量 = 质点模型 m·r²，用 point_mass 即可）
"""

import math

from pint import Quantity

from ..core.units import QuantityLike, set_quantity
from ._utils import _sum_inertia


def ball_screw(mass: QuantityLike, lead: QuantityLike) -> Quantity:
    """
    滚珠丝杠等效转动惯量。

    :param mass: 质量(kg)
    :param lead: 导程(mm)
    :return: 转动惯量(kg·m²)
    """
    m = set_quantity(mass, "kg")
    P = set_quantity(lead, "mm")
    return _sum_inertia([(1.0 / (4.0 * math.pi**2), m, P)])  # m·P²/(4π²)


def gear_rack(mass: QuantityLike, pitch_diameter: QuantityLike) -> Quantity:
    """
    齿轮齿条等效转动惯量。

    :param mass: 质量(kg)
    :param pitch_diameter: 节圆直径(mm)
    :return: 转动惯量(kg·m²)
    """
    m = set_quantity(mass, "kg")
    D = set_quantity(pitch_diameter, "mm")
    return _sum_inertia([(math.pi**2 / 4.0, m, D)])  # m(πD/2)²


def gearbox(load_inertia: QuantityLike, ratio: QuantityLike) -> Quantity:
    """
    减速机折算到电机侧的惯量。

    :param load_inertia: 负载惯量(kg·m²)
    :param ratio: 减速比(None)
    :return: 折算惯量(kg·m²)
    """
    J = set_quantity(load_inertia, "kg*m**2")
    i = float(ratio)
    return (J / i**2).to("kg * m ** 2")
