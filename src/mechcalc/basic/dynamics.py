"""动力学基础计算

重力、摩擦力、离心力、惯性力等。
"""

from pint import Quantity

from ..core.units import QuantityLike, set_quantity


def gravity(mass: QuantityLike, g: QuantityLike = 9.80665) -> Quantity:
    """
    重力计算。

    F = m * g

    :param mass: 质量(kg)
    :param g: 重力加速度(m/s²)，默认 9.80665
    :return: 重力(N)
    """
    m = set_quantity(mass, "kg")
    g_q = set_quantity(g, "m/s**2")

    F = (m * g_q).to("N")
    return F


def friction(
    normal_force: QuantityLike,
    friction_coefficient: float,
    static: bool = False,
) -> Quantity:
    """
    摩擦力计算。

    F_f = μ * N

    :param normal_force: 正压力(N)
    :param friction_coefficient: 摩擦系数(None)
    :param static: 是否静摩擦(None)，默认 False（动摩擦）
    :return: 摩擦力(N)
    """
    N_q = set_quantity(normal_force, "N")
    mu = float(friction_coefficient)

    F_f = (N_q * mu).to("N")
    return F_f


def centrifugal_force(
    mass: QuantityLike,
    radius: QuantityLike,
    angular_velocity: QuantityLike,
) -> Quantity:
    """
    离心力计算。

    F = m * ω² * r

    :param mass: 质量(kg)
    :param radius: 旋转半径(m)
    :param angular_velocity: 角速度(rad/s)
    :return: 离心力(N)
    """
    m = set_quantity(mass, "kg")
    r = set_quantity(radius, "m")
    omega = set_quantity(angular_velocity, "rad/s")

    F = (m * omega**2 * r).to("N")
    return F


def inertia_force(mass: QuantityLike, acceleration: QuantityLike) -> Quantity:
    """
    惯性力（达朗贝尔原理）。

    F = m * a

    :param mass: 质量(kg)
    :param acceleration: 加速度(m/s²)
    :return: 惯性力(N)
    """
    m = set_quantity(mass, "kg")
    a = set_quantity(acceleration, "m/s**2")

    F = (m * a).to("N")
    return F
