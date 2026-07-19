"""旋转运动基础计算

角速度、角加速度、切向速度、切向加速度。
"""

import math
from ..core.units import m, mm, rpm, Q_


def angular_velocity(rpm_speed):
    """
    转速转角速度。

    ω = 2π * n / 60

    :param rpm_speed: 转速(rpm)
    :return: 角速度(rad/s)
    """
    n = rpm(rpm_speed) if not hasattr(rpm_speed, 'magnitude') else rpm_speed.to('rpm')
    n_val = float(n.magnitude)
    omega = Q_(n_val * 2 * math.pi / 60, 'rad/s')
    return omega


def angular_acceleration(omega_change, time):
    """
    角加速度。

    α = Δω / t

    :param omega_change: 角速度变化量(rad/s)
    :param time: 时间(s)
    :return: 角加速度(rad/s²)
    """
    dw = Q_(omega_change, 'rad/s') if not hasattr(omega_change, 'magnitude') else omega_change.to('rad/s')
    t = Q_(time, 's') if not hasattr(time, 'magnitude') else time.to('s')

    alpha = (dw / t).to('rad/s**2')
    return alpha


def tangential_velocity(radius, angular_velocity):
    """
    切向线速度。

    v = ω * r

    :param radius: 旋转半径(m)
    :param angular_velocity: 角速度(rad/s)
    :return: 切向速度(m/s)
    """
    r = m(radius) if not hasattr(radius, 'magnitude') else radius.to('m')
    omega = Q_(angular_velocity, 'rad/s') if not hasattr(angular_velocity, 'magnitude') else angular_velocity.to('rad/s')

    v = (omega * r).to('m/s')
    return v


def tangential_acceleration(radius, angular_acceleration):
    """
    切向加速度。

    a_t = α * r

    :param radius: 旋转半径(m)
    :param angular_acceleration: 角加速度(rad/s²)
    :return: 切向加速度(m/s²)
    """
    r = m(radius) if not hasattr(radius, 'magnitude') else radius.to('m')
    alpha = Q_(angular_acceleration, 'rad/s**2') if not hasattr(angular_acceleration, 'magnitude') else angular_acceleration.to('rad/s**2')

    a_t = (alpha * r).to('m/s**2')
    return a_t
