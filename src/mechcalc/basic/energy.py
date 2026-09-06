"""能量与功率基础计算

动能、势能、功率、扭矩功率换算。
"""

from pint import Quantity

from ..core.units import QuantityLike, set_quantity


def kinetic_energy(mass: QuantityLike, velocity: QuantityLike) -> Quantity:
    """
    平动动能。

    E_k = ½ * m * v²

    :param mass: 质量(kg)
    :param velocity: 速度(m/s)
    :return: 动能(J)
    """
    m = set_quantity(mass, "kg")
    v = set_quantity(velocity, "m/s")

    E = (0.5 * m * v**2).to("J")
    return E


def potential_energy(
    mass: QuantityLike,
    height: QuantityLike,
    g: QuantityLike = 9.80665,
) -> Quantity:
    """
    重力势能。

    E_p = m * g * h

    :param mass: 质量(kg)
    :param height: 高度(m)
    :param g: 重力加速度(m/s²)，默认 9.80665
    :return: 势能(J)
    """
    m_q = set_quantity(mass, "kg")
    h = set_quantity(height, "m")
    g_q = set_quantity(g, "m/s**2")

    E = (m_q * g_q * h).to("J")
    return E


def power(force: QuantityLike, velocity: QuantityLike) -> Quantity:
    """
    功率（力 × 速度）。

    P = F * v

    :param force: 力(N)
    :param velocity: 速度(m/s)
    :return: 功率(W)
    """
    F = set_quantity(force, "N")
    v = set_quantity(velocity, "m/s")

    P = (F * v).to("W")
    return P


def torque_power(torque: QuantityLike, angular_velocity: QuantityLike) -> Quantity:
    """
    旋转功率（扭矩 × 角速度）。

    P = T * ω

    :param torque: 扭矩(N*m)
    :param angular_velocity: 角速度(rad/s)
    :return: 功率(W)
    """
    T = set_quantity(torque, "N*m")
    omega = set_quantity(angular_velocity, "rad/s")

    P = (T * omega).to("W")
    return P
