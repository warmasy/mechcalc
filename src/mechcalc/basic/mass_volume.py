"""质量与体积基础计算

由密度和几何尺寸计算质量，常用几何体体积。
"""

import math
from ..core.units import ensure_quantity


def mass_from_density(density, volume):
    """
    由密度和体积计算质量。

    m = ρ * V

    :param density: 密度(kg/m³)
    :param volume: 体积(m³)
    :return: 质量(kg)
    """
    rho = ensure_quantity(density, 'kg/m**3')
    V = ensure_quantity(volume, 'm**3')

    m = (rho * V).to('kg')
    return m


def cylinder_volume(diameter, length):
    """
    圆柱体体积。

    V = π * (D/2)² * L

    :param diameter: 直径(m)
    :param length: 长度(m)
    :return: 体积(m³)
    """
    D = ensure_quantity(diameter, 'm')
    L = ensure_quantity(length, 'm')

    V = (math.pi * (D / 2) ** 2 * L).to('m**3')
    return V


def sphere_volume(diameter):
    """
    球体体积。

    V = π * D³ / 6

    :param diameter: 直径(m)
    :return: 体积(m³)
    """
    D = ensure_quantity(diameter, 'm')

    V = (math.pi * D ** 3 / 6).to('m**3')
    return V


def cuboid_volume(length, width, height):
    """
    长方体体积。

    V = L * W * H

    :param length: 长度(m)
    :param width: 宽度(m)
    :param height: 高度(m)
    :return: 体积(m³)
    """
    L = ensure_quantity(length, 'm')
    W = ensure_quantity(width, 'm')
    H = ensure_quantity(height, 'm')

    V = (L * W * H).to('m**3')
    return V
