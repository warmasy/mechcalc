"""核心基础设施

单位系统、三维向量与矩阵工具。
"""

from .linalg import (
    as_vec3,
    as_vecs,
    rot_x,
    rot_y,
    rot_z,
    skew,
    unit_vector,
)
from .units import (
    Q_,
    set_quantity,
    to_mag,
    to_unit,
    ureg,
)
from .units_linalg import det, eig, inv, matrix_power, trace

__all__ = [
    "Q_",
    "ureg",
    "to_mag",
    "to_unit",
    "set_quantity",
    "as_vec3",
    "as_vecs",
    "skew",
    "unit_vector",
    "rot_x",
    "rot_y",
    "rot_z",
    # 带单位线性代数（补齐 pint 缺失的 linalg 函数）
    "inv",
    "det",
    "eig",
    "matrix_power",
    "trace",
]
