"""惯量张量计算

三维转动的惯量表示与变换。

约定（见 core.linalg）：
- 张量表示在质心坐标系中，对称轴为 z 轴
- 与标量模块 inertia.py 的关系：标量函数即张量绕对称轴的分量，
  测试中用互锁测试保证两套结果一致

用法:
    >>> I = solid_cylinder_tensor(10, 100, 200)       # 3×3 张量，kg·m²
    >>> J = inertia_about_axis(I, [0, 0, 1])          # 绕 z 轴 = 标量 solid_cylinder
    >>> Js = inertia_about_axis(I, [[1,0,0],[0,0,1]]) # 批量，(N,3)
"""

import numpy as np

from ..core.units import Q_, kg, mm, to_mag
from ..core.linalg import as_vec3, as_vecs
from .inertia import solid_cylinder, hollow_cylinder


def _as_tensor(inertia_tensor):
    """惯量张量输入规范化 -> (3,3) SI 数值数组。裸数组按 kg·m² 解释。"""
    if hasattr(inertia_tensor, 'magnitude'):
        arr = np.asarray(inertia_tensor.to('kg*m**2').magnitude, dtype=float)
    else:
        arr = np.asarray(inertia_tensor, dtype=float)
    if arr.shape != (3, 3):
        raise ValueError(f"需要 3×3 惯量张量，得到形状 {arr.shape}")
    return arr


def solid_cylinder_tensor(mass, outer_diameter, length):
    """
    实心圆柱惯量张量（质心坐标系，对称轴为 z）。

    Izz = m·R²/2（复用标量 solid_cylinder）
    Ixx = Iyy = m·(3R² + L²)/12

    :param mass: 质量(kg)
    :param outer_diameter: 外径(mm)
    :param length: 长度(mm)
    :return: 3×3 惯量张量(kg·m²)
    """
    m = kg(mass) if not hasattr(mass, 'magnitude') else mass.to('kg')
    D = mm(outer_diameter) if not hasattr(outer_diameter, 'magnitude') else outer_diameter.to('mm')
    L = mm(length) if not hasattr(length, 'magnitude') else length.to('mm')

    # 复用标量函数，保证与 solid_cylinder 一致
    Izz = to_mag(solid_cylinder(to_mag(m, 'kg'), to_mag(D, 'mm')), 'kg*m**2')

    R = to_mag(D, 'm') / 2
    L_m = to_mag(L, 'm')
    m_val = to_mag(m, 'kg')
    Ixx = Iyy = m_val * (3 * R**2 + L_m**2) / 12

    return Q_(np.diag([Ixx, Iyy, Izz]), 'kg*m**2')


def hollow_cylinder_tensor(mass, outer_diameter, inner_diameter, length):
    """
    空心圆柱惯量张量（质心坐标系，对称轴为 z）。

    Izz = m·(R² + r²)/2（复用标量 hollow_cylinder）
    Ixx = Iyy = m·(3(R² + r²) + L²)/12

    :param mass: 质量(kg)
    :param outer_diameter: 外径(mm)
    :param inner_diameter: 内径(mm)
    :param length: 长度(mm)
    :return: 3×3 惯量张量(kg·m²)
    """
    m = kg(mass) if not hasattr(mass, 'magnitude') else mass.to('kg')
    D = mm(outer_diameter) if not hasattr(outer_diameter, 'magnitude') else outer_diameter.to('mm')
    d = mm(inner_diameter) if not hasattr(inner_diameter, 'magnitude') else inner_diameter.to('mm')
    L = mm(length) if not hasattr(length, 'magnitude') else length.to('mm')

    Izz = to_mag(hollow_cylinder(to_mag(m, 'kg'), to_mag(D, 'mm'), to_mag(d, 'mm')), 'kg*m**2')

    R2 = (to_mag(D, 'm') / 2) ** 2
    r2 = (to_mag(d, 'm') / 2) ** 2
    L_m = to_mag(L, 'm')
    m_val = to_mag(m, 'kg')
    Ixx = Iyy = m_val * (3 * (R2 + r2) + L_m**2) / 12

    return Q_(np.diag([Ixx, Iyy, Izz]), 'kg*m**2')


def parallel_axis_tensor(inertia_tensor, mass, offset):
    """
    平行移轴定理（张量形式）。

    I = I_c + m·(r·r·E − r·rᵀ)，r 为质心到新轴的位移向量

    :param inertia_tensor: 质心惯量张量(kg·m²)，裸数组按 kg·m² 解释
    :param mass: 质量(kg)
    :param offset: 质心到新轴的位移向量 [x, y, z](m)
    :return: 3×3 惯量张量(kg·m²)
    """
    I = _as_tensor(inertia_tensor)
    m = kg(mass) if not hasattr(mass, 'magnitude') else mass.to('kg')
    r = as_vec3(offset, 'm')

    I_new = I + to_mag(m, 'kg') * (r @ r * np.eye(3) - np.outer(r, r))
    return Q_(I_new, 'kg*m**2')


def inertia_about_axis(inertia_tensor, axis):
    """
    任意方向轴的等效转动惯量。

    J = nᵀ·I·n（n 自动单位化）
    axis 支持单方向 (3,) 或批量 (N, 3)。

    :param inertia_tensor: 惯量张量(kg·m²)，裸数组按 kg·m² 解释
    :param axis: 轴向向量(None)，无需单位化
    :return: 等效惯量(kg·m²)，批量时返回数组
    """
    I = _as_tensor(inertia_tensor)
    n = as_vecs(axis)

    if n.ndim == 1:
        return Q_(float(n @ I @ n), 'kg*m**2')
    return Q_(np.einsum('ni,ij,nj->n', n, I, n), 'kg*m**2')
