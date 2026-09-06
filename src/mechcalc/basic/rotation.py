"""旋转运动基础计算

角速度、角加速度、切向速度、切向加速度。
"""

import math

from pint import Quantity

from ..core.units import Q_, QuantityLike, set_quantity


def angular_velocity(rpm_speed: QuantityLike) -> Quantity:
    """
    转速转角速度。

    ω = 2π * n / 60

    :param rpm_speed: 转速(rpm)
    :return: 角速度(rad/s)
    """
    n = set_quantity(rpm_speed, "rpm")
    n_val = float(n.magnitude)
    omega = Q_(n_val * 2 * math.pi / 60, "rad/s")
    return omega


def angular_acceleration(omega_change: QuantityLike, time: QuantityLike) -> Quantity:
    """
    角加速度。

    α = Δω / t

    :param omega_change: 角速度变化量(rad/s)
    :param time: 时间(s)
    :return: 角加速度(rad/s²)
    """
    dw = set_quantity(omega_change, "rad/s")
    t = set_quantity(time, "s")

    alpha = (dw / t).to("rad/s**2")
    return alpha


def tangential_velocity(radius: QuantityLike, angular_velocity: QuantityLike) -> Quantity:
    """
    切向线速度。

    v = ω * r

    :param radius: 旋转半径(m)
    :param angular_velocity: 角速度(rad/s)
    :return: 切向速度(m/s)
    """
    r = set_quantity(radius, "m")
    omega = set_quantity(angular_velocity, "rad/s")

    v = (omega * r).to("m/s")
    return v


def tangential_acceleration(
    radius: QuantityLike,
    angular_acceleration: QuantityLike,
) -> Quantity:
    """
    切向加速度。

    a_t = α * r

    :param radius: 旋转半径(m)
    :param angular_acceleration: 角加速度(rad/s²)
    :return: 切向加速度(m/s²)
    """
    r = set_quantity(radius, "m")
    alpha = set_quantity(angular_acceleration, "rad/s**2")

    a_t = (alpha * r).to("m/s**2")
    return a_t
