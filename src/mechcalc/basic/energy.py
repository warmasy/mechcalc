"""能量与功率基础计算

动能、势能、功率、扭矩功率换算。
"""

from ..core.units import kg, m, Nm, W, Q_


def kinetic_energy(mass, velocity):
    """
    平动动能。

    E_k = ½ * m * v²

    :param mass: 质量(kg)
    :param velocity: 速度(m/s)
    :return: 动能(J)
    """
    m = kg(mass)
    v = Q_(velocity, 'm/s') if not hasattr(velocity, 'magnitude') else velocity.to('m/s')

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
    m_q = kg(mass)
    h = m(height) if not hasattr(height, 'magnitude') else height.to('m')
    g_q = Q_(g, 'm/s**2') if not hasattr(g, 'magnitude') else g.to('m/s**2')

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
    F = Q_(force, 'N') if not hasattr(force, 'magnitude') else force.to('N')
    v = Q_(velocity, 'm/s') if not hasattr(velocity, 'magnitude') else velocity.to('m/s')

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
    T = Nm(torque) if not hasattr(torque, 'magnitude') else torque.to('N*m')
    omega = Q_(angular_velocity, 'rad/s') if not hasattr(angular_velocity, 'magnitude') else angular_velocity.to('rad/s')

    P = (T * omega).to('W')
    return P
