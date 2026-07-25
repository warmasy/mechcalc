"""mechcalc - 机械工程计算库

基于 pint 单位系统的机械工程计算库，提供惯量计算、气缸计算、电机选型等功能。

快速开始:
    >>> import mechcalc as mc
    >>> raw = mc.solid_cylinder(mass=10, outer_diameter=100)
    >>> raw.to('kg*m**2')
    0.0125 kilogram * meter ** 2

    >>> result = mc.to_result(mc.motor_calc, load_torque=5.0, load_speed=1400)
    >>> result.required_power
    {'value': 879.6, 'unit': 'W'}
"""

from ._version import __version__

# 核心（从子目录导入）
from .core import (
    kg, mm, m, s, N, Nm, MPa, rpm, kg_m2, kW, W,
    Q_, ureg, to_mag, to_unit, ensure_quantity, ensure_float,
    as_vec3, as_vecs, skew, unit_vector, rot_x, rot_y, rot_z,
)

# 通用工具
from .utils import Result, calc_batch, to_result

# 基础计算
from .basic import (
    # 运动学
    velocity, displacement, acceleration,
    uniform_motion, uniform_acceleration,
    # 动力学
    gravity, friction, centrifugal_force, inertia_force,
    # 旋转运动
    angular_velocity, angular_acceleration,
    tangential_velocity, tangential_acceleration,
    # 能量功率
    kinetic_energy, potential_energy, power, torque_power,
    # 质量体积
    mass_from_density, cylinder_volume, sphere_volume, cuboid_volume,
    # 三维运动（向量化）
    point_velocity, centripetal_acceleration,
    rotational_kinetic_energy, angular_momentum, gravity_force,
)

# 惯量计算
from .inertia import (
    solid_cylinder,
    hollow_cylinder,
    point_mass,
    straight_rod,
    conveyor_belt,
    ball_screw,
    gear_rack,
    gearbox,
    inclined_rod,
    # 惯量张量（向量化）
    solid_cylinder_tensor,
    hollow_cylinder_tensor,
    parallel_axis_tensor,
    inertia_about_axis,
)

# 气缸计算
from .pneumatic import (
    push_force,
    pull_force,
    air_consumption,
    cylinder_select,
    STD_BORES,
)

# 电机计算
from .electric import motor_calc

__all__ = [
    "__version__",
    # 核心
    "kg", "mm", "m", "s", "N", "Nm", "MPa", "rpm", "kg_m2", "kW", "W",
    "Q_", "ureg", "to_mag", "to_unit", "ensure_quantity", "ensure_float", 
    "Result", "calc_batch", "to_result",
    "as_vec3", "as_vecs", "skew", "unit_vector", "rot_x", "rot_y", "rot_z",
    # 基础计算
    "velocity", "displacement", "acceleration",
    "uniform_motion", "uniform_acceleration",
    "gravity", "friction", "centrifugal_force", "inertia_force",
    "angular_velocity", "angular_acceleration",
    "tangential_velocity", "tangential_acceleration",
    "kinetic_energy", "potential_energy", "power", "torque_power",
    "mass_from_density", "cylinder_volume", "sphere_volume", "cuboid_volume",
    "point_velocity", "centripetal_acceleration",
    "rotational_kinetic_energy", "angular_momentum", "gravity_force",
    # 惯量
    "solid_cylinder", "hollow_cylinder", "point_mass",
    "straight_rod", "conveyor_belt", "ball_screw", "gear_rack", "gearbox",
    "inclined_rod",
    "solid_cylinder_tensor", "hollow_cylinder_tensor",
    "parallel_axis_tensor", "inertia_about_axis",
    # 气缸
    "push_force", "pull_force", "air_consumption", "cylinder_select", "STD_BORES",
    # 电机
    "motor_calc",
]
