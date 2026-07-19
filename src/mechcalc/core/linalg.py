"""三维向量与矩阵工具

向量化计算的基础层。全库统一约定：

- 右手坐标系，z 轴向上
- 角度一律弧度（传入 pint Quantity 时自动换算，支持 deg）
- 单个向量形状 (3,)，批量向量形状 (N, 3)
- 内部一律 SI 单位裸数组，pint 只在边界出现

单位结算纪律：
- as_vec3 是唯一有权剥掉单位的入口（显式 .to(unit) 后取 magnitude）
- 禁止在业务代码里直接 np.asarray(Quantity)（会静默丢单位且不换算）

用法:
    >>> from mechcalc.core.linalg import as_vec3, skew, rot_z
    >>> import numpy as np
    >>> as_vec3([100, 200, 0], 'mm')   # 裸数值按 mm 解释
    array([0.1, 0.2, 0. ])
"""

import math
import numpy as np


# ==================== 输入规范化 ====================

def as_vec3(value, unit):
    """
    三维向量输入规范化 -> (3,) SI 数值数组。

    pint Quantity 显式换算到 unit 后剥成裸数组；
    裸数值（list/tuple/ndarray）按 unit 解释。

    :param value: 三维向量 [x, y, z]，或带数组的 Quantity
    :param unit: 目标单位字符串（SI）
    :return: np.ndarray, shape (3,)
    """
    if hasattr(value, 'magnitude'):
        arr = np.asarray(value.to(unit).magnitude, dtype=float)
    else:
        arr = np.asarray(value, dtype=float)
    if arr.shape != (3,):
        raise ValueError(f"需要三维向量，得到形状 {arr.shape}")
    return arr


def as_vecs(value):
    """
    方向向量规范化，支持单方向 (3,) 或批量 (N, 3)，自动单位化。

    方向无量纲：Quantity 输入直接取 magnitude（方向与单位无关）。

    :param value: 方向向量，形状 (3,) 或 (N, 3)
    :return: 单位化后的 np.ndarray，形状同输入
    """
    if hasattr(value, 'magnitude'):
        n = np.asarray(value.magnitude, dtype=float)
    else:
        n = np.asarray(value, dtype=float)
    if n.ndim not in (1, 2) or n.shape[-1] != 3:
        raise ValueError(f"需要形状 (3,) 或 (N, 3)，得到 {n.shape}")
    return n / np.linalg.norm(n, axis=-1, keepdims=True)


# ==================== 向量运算 ====================

def skew(w):
    """
    反对称矩阵（叉乘矩阵）。

    skew(w) @ r == np.cross(w, r)

    :param w: 三维向量(None)
    :return: 3×3 反对称矩阵
    """
    w = np.asarray(w, dtype=float)
    return np.array([[0, -w[2], w[1]],
                     [w[2], 0, -w[0]],
                     [-w[1], w[0], 0]])


def unit_vector(v):
    """
    单位化向量。

    :param v: 向量(None)
    :return: 同方向单位向量
    """
    v = np.asarray(v, dtype=float)
    return v / np.linalg.norm(v)


# ==================== 旋转矩阵 ====================

def _as_rad(angle):
    """角度规范化 -> 弧度浮点数。接受 float(rad) 或 Quantity（自动换算 deg）。"""
    if hasattr(angle, 'magnitude'):
        return float(angle.to('rad').magnitude)
    return float(angle)


def rot_x(angle):
    """
    绕 x 轴旋转矩阵（右手系）。

    :param angle: 旋转角(rad)，Quantity 时支持 deg
    :return: 3×3 旋转矩阵，语义 v_new = R @ v_old
    """
    a = _as_rad(angle)
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0],
                     [0, c, -s],
                     [0, s, c]])


def rot_y(angle):
    """
    绕 y 轴旋转矩阵（右手系）。

    :param angle: 旋转角(rad)，Quantity 时支持 deg
    :return: 3×3 旋转矩阵，语义 v_new = R @ v_old
    """
    a = _as_rad(angle)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s],
                     [0, 1, 0],
                     [-s, 0, c]])


def rot_z(angle):
    """
    绕 z 轴旋转矩阵（右手系）。

    :param angle: 旋转角(rad)，Quantity 时支持 deg
    :return: 3×3 旋转矩阵，语义 v_new = R @ v_old
    """
    a = _as_rad(angle)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0],
                     [s, c, 0],
                     [0, 0, 1]])
