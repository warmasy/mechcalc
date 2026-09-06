"""惯量计算模块

常见几何体的转动惯量计算 + 工程机构等效惯量。
所有返回 dict 的函数都含 'tensor' 键（完整 3×3 惯性张量，kg·m²）。
"""

from .applications import (
    ball_screw,
    gear_rack,
    gearbox,
)
from .plates import (
    annular_plate,
    circular_plate,
    elliptical_plate,
    parabolic_plate,
    rectangular_plate,
    regular_polygon_plate,
    sector_plate,
    segment_plate,
    semicircular_plate,
    trapezoidal_plate,
    triangular_plate,
)
from .rods import (
    arc_rod,
    circular_ring_rod,
    cylindrical_rod,
    elliptical_ring_rod,
    inclined_rod,
    point_mass,
    rectangular_frame_rod,
    u_rod,
)
from .shells import (
    cone_lateral_shell,
    cylinder_lateral_shell,
    cylinder_total_shell,
    hemisphere_shell,
    sphere_shell,
    torus_shell,
    truncated_cone_shell,
)
from .solids import (
    cone,
    cylinder,
    elliptical_torus,
    hemisphere,
    hollow_sphere,
    rectangular_prism,
    rectangular_torus,
    right_pyramid,
    sphere,
    spherical_cap,
    triangular_prism,
    truncated_cone,
    tube,
)
from .tensor import (
    hollow_cylinder_tensor,
    inertia_about_axis,
    parallel_axis_tensor,
    solid_cylinder_tensor,
)

__all__ = [
    # 工程应用
    "ball_screw",
    "gear_rack",
    "gearbox",
    # 细杆
    "point_mass",
    "inclined_rod",
    "arc_rod",
    "u_rod",
    "cylindrical_rod",
    "rectangular_frame_rod",
    "elliptical_ring_rod",
    "circular_ring_rod",
    # 平面板
    "triangular_plate",
    "rectangular_plate",
    "semicircular_plate",
    "annular_plate",
    "sector_plate",
    "trapezoidal_plate",
    "regular_polygon_plate",
    "circular_plate",
    "segment_plate",
    "elliptical_plate",
    "parabolic_plate",
    # 立体形状
    "cylinder",
    "tube",
    "rectangular_prism",
    "right_pyramid",
    "triangular_prism",
    "truncated_cone",
    "sphere",
    "hollow_sphere",
    "cone",
    "spherical_cap",
    "elliptical_torus",
    "rectangular_torus",
    "hemisphere",
    # 薄壳体
    "truncated_cone_shell",
    "cylinder_lateral_shell",
    "cylinder_total_shell",
    "cone_lateral_shell",
    "hemisphere_shell",
    "sphere_shell",
    "torus_shell",
    # 张量
    "solid_cylinder_tensor",
    "hollow_cylinder_tensor",
    "parallel_axis_tensor",
    "inertia_about_axis",
]
