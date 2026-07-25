"""三维刚体运动计算

旋转刚体上点的速度/加速度、转动动能、角动量、重力向量。

约定（见 core.linalg）：右手坐标系，z 轴向上，向量形状 (3,)，内部 SI。

用法:
    >>> v = point_velocity([0, 0, 10], [0.1, 0, 0])   # v = ω×r
    >>> F = gravity_force(10)                          # [0, 0, -98.0665] N
    >>> F_body = gravity_force(10, rotation=rot_x(math.pi / 2))
"""

import numpy as np

from ..core.units import Q_, to_mag, ensure_quantity
from ..core.linalg import as_vec3, skew


def _as_tensor(inertia_tensor):
    """惯量张量输入规范化 -> (3,3) SI 数值数组。裸数组按 kg·m² 解释。"""
    if hasattr(inertia_tensor, 'magnitude'):
        arr = np.asarray(inertia_tensor.to('kg*m**2').magnitude, dtype=float)
    else:
        arr = np.asarray(inertia_tensor, dtype=float)
    if arr.shape != (3, 3):
        raise ValueError(f"需要 3×3 惯量张量，得到形状 {arr.shape}")
    return arr


def point_velocity(angular_velocity, position):
    """
    旋转刚体上一点的线速度。

    v = ω × r

    :param angular_velocity: 角速度向量 [wx, wy, wz](rad/s)
    :param position: 相对转轴的位置向量 [x, y, z](m)
    :return: 线速度向量(m/s)
    """
    w = as_vec3(angular_velocity, 'rad/s')
    r = as_vec3(position, 'm')
    return Q_(skew(w) @ r, 'm/s')


def centripetal_acceleration(angular_velocity, position):
    """
    向心加速度。

    a = ω × (ω × r)

    :param angular_velocity: 角速度向量 [wx, wy, wz](rad/s)
    :param position: 相对转轴的位置向量 [x, y, z](m)
    :return: 向心加速度向量(m/s²)
    """
    w = as_vec3(angular_velocity, 'rad/s')
    r = as_vec3(position, 'm')
    W = skew(w)
    return Q_(W @ W @ r, 'm/s**2')


def rotational_kinetic_energy(inertia_tensor, angular_velocity):
    """
    转动动能。

    T = ½·ωᵀ·I·ω

    :param inertia_tensor: 惯量张量(kg·m²)，裸数组按 kg·m² 解释
    :param angular_velocity: 角速度向量 [wx, wy, wz](rad/s)
    :return: 动能(J)
    """
    I = _as_tensor(inertia_tensor)
    w = as_vec3(angular_velocity, 'rad/s')
    return Q_(0.5 * float(w @ I @ w), 'J')


def angular_momentum(inertia_tensor, angular_velocity):
    """
    角动量。

    L = I·ω

    :param inertia_tensor: 惯量张量(kg·m²)，裸数组按 kg·m² 解释
    :param angular_velocity: 角速度向量 [wx, wy, wz](rad/s)
    :return: 角动量向量(kg·m²/s)
    """
    I = _as_tensor(inertia_tensor)
    w = as_vec3(angular_velocity, 'rad/s')
    return Q_(I @ w, 'kg*m**2/s')


def gravity_force(mass, rotation=None, g=9.80665):
    """
    重力向量。

    默认世界系（z 轴向上）：F = [0, 0, -m·g]
    传入 rotation（3×3 坐标变换矩阵，世界系 -> 本体系）时，
    输出重力在本体系中的分量，如 rotation=rot_x(angle)。

    :param mass: 质量(kg)
    :param rotation: 坐标变换矩阵(None)，可选
    :param g: 重力加速度(m/s²)，默认 9.80665
    :return: 重力向量(N)
    """
    m = ensure_quantity(mass, 'kg')
    g_q = ensure_quantity(g, 'm/s**2')
    F_mag = to_mag((m * g_q).to('N'), 'N')
    vec = np.array([0.0, 0.0, -F_mag])

    if rotation is not None:
        R = np.asarray(rotation, dtype=float)
        if R.shape != (3, 3):
            raise ValueError(f"rotation 需要 3×3 矩阵，得到形状 {R.shape}")
        vec = R @ vec

    return ensure_quantity(vec, 'N')
