"""能量与功率基础计算

动能、势能、功率、扭矩功率换算。
"""

from ..core.units import ensure_quantity


def kinetic_energy(mass, velocity):
    """
    平动动能。

    E_k = ½ * m * v²

    :param mass: 质量(kg)
    :param velocity: 速度(m/s)
    :return: 动能(J)
    """
    m = ensure_quantity(mass, 'kg')
    v = ensure_quantity(velocity, 'm/s')

    E = (0.5 * m * v ** 2).to('J')
    return E


def potential_energy(mass, height, g=9.80665):
    """
    重力势能。

    E_p = m * g * h

    :param mass: 质量(kg)
    :param height: 高度(m)
    :param g: 重力加速度(m/s²)，默认 9.80665
    :return: 势能(J)
    """
    m_q = ensure_quantity(mass, 'kg')
    h = ensure_quantity(height, 'm')
    g_q = ensure_quantity(g, 'm/s**2')

    E = (m_q * g_q * h).to('J')
    return E


def power(force, velocity):
    """
    功率（力 × 速度）。

    P = F * v

    :param force: 力(N)
    :param velocity: 速度(m/s)
    :return: 功率(W)
    """
    F = ensure_quantity(force, 'N')
    v = ensure_quantity(velocity, 'm/s')

    P = (F * v).to('W')
    return P


def torque_power(torque, angular_velocity):
    """
    旋转功率（扭矩 × 角速度）。

    P = T * ω

    :param torque: 扭矩(N*m)
    :param angular_velocity: 角速度(rad/s)
    :return: 功率(W)
    """
    T = ensure_quantity(torque, 'N*m')
    omega = ensure_quantity(angular_velocity, 'rad/s')

    P = (T * omega).to('W')
    return P
