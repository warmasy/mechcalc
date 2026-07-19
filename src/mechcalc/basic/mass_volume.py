"""质量与体积基础计算

由密度和几何尺寸计算质量，常用几何体体积。
"""

import math
from ..core.units import kg, m, mm, Q_


def mass_from_density(density, volume):
    """
    由密度和体积计算质量。

    m = ρ * V

    :param density: 密度(kg/m³)
    :param volume: 体积(m³)
    :return: 质量(kg)
    """
    rho = Q_(density, 'kg/m**3') if not hasattr(density, 'magnitude') else density.to('kg/m**3')
    V = Q_(volume, 'm**3') if not hasattr(volume, 'magnitude') else volume.to('m**3')

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
    D = m(diameter) if not hasattr(diameter, 'magnitude') else diameter.to('m')
    L = m(length) if not hasattr(length, 'magnitude') else length.to('m')

    V = (math.pi * (D / 2) ** 2 * L).to('m**3')
    return V


def sphere_volume(diameter):
    """
    球体体积。

    V = π * D³ / 6

    :param diameter: 直径(m)
    :return: 体积(m³)
    """
    D = m(diameter) if not hasattr(diameter, 'magnitude') else diameter.to('m')

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
    L = m(length) if not hasattr(length, 'magnitude') else length.to('m')
    W = m(width) if not hasattr(width, 'magnitude') else width.to('m')
    H = m(height) if not hasattr(height, 'magnitude') else height.to('m')

    V = (L * W * H).to('m**3')
    return V
