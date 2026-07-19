"""核心基础设施

单位系统、结果封装、计算装饰器。
"""

from .units import (
    kg, mm, m, s, N, Nm, MPa, rpm, kg_m2, kW, W,
    Q_, ureg, to_mag, to_unit, ensure_quantity, ensure_float,
    NESTED_UNITS, FLAT_UNITS,
)
from .linalg import (
    as_vec3, as_vecs, skew, unit_vector,
    rot_x, rot_y, rot_z,
)

__all__ = [
    'kg', 'mm', 'm', 's', 'N', 'Nm', 'MPa', 'rpm', 'kg_m2', 'kW', 'W',
    'Q_', 'ureg', 'to_mag', 'to_unit', 'ensure_quantity', 'ensure_float', 
    'NESTED_UNITS', 'FLAT_UNITS',
    'as_vec3', 'as_vecs', 'skew', 'unit_vector',
    'rot_x', 'rot_y', 'rot_z',
]
