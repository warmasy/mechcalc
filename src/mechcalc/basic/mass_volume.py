"""质量与体积基础计算

由密度和几何尺寸计算质量，常用几何体体积。
"""

import math

from pint import Quantity

from ..core.units import QuantityLike, set_quantity


def mass_from_density(density: QuantityLike, volume: QuantityLike) -> Quantity:
    """
    由密度和体积计算质量。

    m = ρ * V

    :param density: 密度(kg/m³)
    :param volume: 体积(m³)
    :return: 质量(kg)
    """
    rho = set_quantity(density, "kg/m**3")
    V = set_quantity(volume, "m**3")

    m = (rho * V).to("kg")
    return m


def cylinder_volume(diameter: QuantityLike, length: QuantityLike) -> Quantity:
    """
    圆柱体体积。

    V = π * (D/2)² * L

    :param diameter: 直径(m)
    :param length: 长度(m)
    :return: 体积(m³)
    """
    D = set_quantity(diameter, "m")
    L = set_quantity(length, "m")

    V = (math.pi * (D / 2) ** 2 * L).to("m**3")
    return V


def sphere_volume(diameter: QuantityLike) -> Quantity:
    """
    球体体积。

    V = π * D³ / 6

    :param diameter: 直径(m)
    :return: 体积(m³)
    """
    D = set_quantity(diameter, "m")

    V = (math.pi * D**3 / 6).to("m**3")
    return V


def cuboid_volume(
    length: QuantityLike,
    width: QuantityLike,
    height: QuantityLike,
) -> Quantity:
    """
    长方体体积。

    V = L * W * H

    :param length: 长度(m)
    :param width: 宽度(m)
    :param height: 高度(m)
    :return: 体积(m³)
    """
    L = set_quantity(length, "m")
    W = set_quantity(width, "m")
    H = set_quantity(height, "m")

    V = (L * W * H).to("m**3")
    return V
