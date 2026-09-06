"""带单位的 numpy 线性代数工具

pint 原生支持：元素级运算、`@`、np.dot、np.linalg.norm / solve / transpose 等，
但不支持：np.linalg.inv / det / eig / matrix_power、np.trace。

本模块用「剥单位 → 裸算 → 装回」模式补齐这些函数，并正确推导结果单位：

    inv(A)         单位取倒数            (m -> 1/m)
    det(A)  (n×n)  单位是 unit**n        (m -> m²)
    eig(A)         特征值单位 = A 的单位，特征向量无量纲
    matrix_power   单位是 unit**p
    trace          单位 = A 的单位

用法:
    >>> A = Q_(np.array([[2., 0.], [0., 3.]]), 'm')
    >>> inv(A)          # [[0.5, 0], [0, 1/3]]  m^-1
    >>> det(A)          # 6 m²
    >>> w, v = eig(A)   # w 单位 m，v 无量纲
    >>> trace(A)        # 5 m

约定：传入裸数组（无单位）时返回裸 numpy 结果，工具对两种输入通吃。
"""

import numpy as np
from pint import Quantity


def _as_matrix(value: object) -> tuple[np.ndarray, object]:
    """规范化输入 -> (裸数值数组, 单位或 None)。裸数组按原样返回。"""
    if hasattr(value, "magnitude"):
        return np.asarray(value.magnitude, dtype=float), value.units
    return np.asarray(value, dtype=float), None


def _wrap(raw: np.ndarray, units: object) -> object:
    """按输入是否有单位包装结果。"""
    return Quantity(raw, units) if units is not None else raw


def inv(qty):
    """
    矩阵求逆（单位取倒数）。

    A 可逆时：inv(A) = A⁻¹，单位 = unit⁻¹
    """
    mag, u = _as_matrix(qty)
    return _wrap(np.linalg.inv(mag), u**-1 if u is not None else None)


def det(qty):
    """
    行列式（单位 = unit**n，n 为矩阵阶数）。

    物理意义示例：2×2 惯量张量 det 的单位是 kg²·m⁴。
    """
    mag, u = _as_matrix(qty)
    n = mag.shape[0]
    return _wrap(np.linalg.det(mag), u**n if u is not None else None)


def eig(qty):
    """
    特征值分解。

    :return: (特征值, 特征向量)
        - 特征值：单位 = 矩阵单位（如 m）
        - 特征向量：无量纲（按列存放，np.linalg.eig 约定）
    """
    mag, u = _as_matrix(qty)
    w, v = np.linalg.eig(mag)
    return _wrap(w, u), v


def matrix_power(qty, p: int):
    """
    矩阵幂（单位 = unit**p）。

    :param p: 整数次幂（负幂等价于多次求逆）
    """
    mag, u = _as_matrix(qty)
    return _wrap(np.linalg.matrix_power(mag, p), u**p if u is not None else None)


def trace(qty):
    """
    矩阵的迹（单位 = 矩阵单位）。

    物理意义示例：惯量张量的迹 Ixx+Iyy+Izz 单位 kg·m²。
    """
    mag, u = _as_matrix(qty)
    return _wrap(np.trace(mag), u)
