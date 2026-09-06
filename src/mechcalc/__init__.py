"""mechcalc - 机械工程计算库

基于 pint 单位系统的机械工程计算库，提供惯量计算、气缸计算、电机计算等功能。

快速开始:
    >>> import mechcalc as mc
    >>> raw = mc.solid_cylinder(mass=10, outer_diameter=100)
    >>> raw.to('kg*m**2')
    0.0125 kilogram * meter ** 2

    >>> result = mc.to_result(mc.motor_calc, load_torque=5.0, load_speed=1400)
    >>> result.required_power
    {'value': 879.6, 'unit': 'W'}
"""

# ruff: noqa: I001  # API 组织文件，import 按功能分组而非字母序

from ._version import __version__

# 核心（从子目录导入）
from .core import (
    Q_,
    ureg,
    to_mag,
    to_unit,
    set_quantity,
    as_vec3,
    as_vecs,
    skew,
    unit_vector,
    rot_x,
    rot_y,
    rot_z,
    # 带单位线性代数（补齐 pint 缺失的 linalg）
    inv,
    det,
    eig,
    matrix_power,
    trace,
)

# 通用工具
from .utils import Result, calc_batch, to_result

# 基础计算
from .basic import (
    # 运动学
    velocity,
    displacement,
    acceleration,
    uniform_motion,
    uniform_acceleration,
    # 动力学
    gravity,
    friction,
    centrifugal_force,
    inertia_force,
    # 旋转运动
    angular_velocity,
    angular_acceleration,
    tangential_velocity,
    tangential_acceleration,
    # 能量功率
    kinetic_energy,
    potential_energy,
    power,
    torque_power,
    # 质量体积
    mass_from_density,
    cylinder_volume,
    sphere_volume,
    cuboid_volume,
    # 三维运动（向量化）
    point_velocity,
    centripetal_acceleration,
    rotational_kinetic_energy,
    angular_momentum,
    gravity_force,
)

# 惯量计算
from .inertia import (
    # 工程应用
    ball_screw,
    gear_rack,
    gearbox,
    # 细杆
    point_mass,
    inclined_rod,
    arc_rod,
    u_rod,
    cylindrical_rod,
    rectangular_frame_rod,
    elliptical_ring_rod,
    circular_ring_rod,
    # 平面板
    triangular_plate,
    rectangular_plate,
    semicircular_plate,
    annular_plate,
    sector_plate,
    trapezoidal_plate,
    regular_polygon_plate,
    circular_plate,
    segment_plate,
    elliptical_plate,
    parabolic_plate,
    # 立体形状
    cylinder,
    tube,
    rectangular_prism,
    right_pyramid,
    triangular_prism,
    truncated_cone,
    sphere,
    hollow_sphere,
    cone,
    spherical_cap,
    elliptical_torus,
    rectangular_torus,
    hemisphere,
    # 薄壳体
    truncated_cone_shell,
    cylinder_lateral_shell,
    cylinder_total_shell,
    cone_lateral_shell,
    hemisphere_shell,
    sphere_shell,
    torus_shell,
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
from .electric import (
    motor_calc,
    motor_select,
    MotorSpec,
    MOTOR_DB,
    servo_select,
    ServoMotorSpec,
    SERVO_DB,
)

__all__ = [
    "__version__",
    # 核心
    "Q_",
    "ureg",
    "to_mag",
    "to_unit",
    "set_quantity",
    "Result",
    "calc_batch",
    "to_result",
    "as_vec3",
    "as_vecs",
    "skew",
    "unit_vector",
    "rot_x",
    "rot_y",
    "rot_z",
    # 带单位线性代数
    "inv",
    "det",
    "eig",
    "matrix_power",
    "trace",
    # 基础计算
    "velocity",
    "displacement",
    "acceleration",
    "uniform_motion",
    "uniform_acceleration",
    "gravity",
    "friction",
    "centrifugal_force",
    "inertia_force",
    "angular_velocity",
    "angular_acceleration",
    "tangential_velocity",
    "tangential_acceleration",
    "kinetic_energy",
    "potential_energy",
    "power",
    "torque_power",
    "mass_from_density",
    "cylinder_volume",
    "sphere_volume",
    "cuboid_volume",
    "point_velocity",
    "centripetal_acceleration",
    "rotational_kinetic_energy",
    "angular_momentum",
    "gravity_force",
    # 惯量 - 工程应用
    "ball_screw",
    "gear_rack",
    "gearbox",
    # 惯量 - 细杆
    "point_mass",
    "inclined_rod",
    "arc_rod",
    "u_rod",
    "cylindrical_rod",
    "rectangular_frame_rod",
    "elliptical_ring_rod",
    "circular_ring_rod",
    # 惯量 - 平面板
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
    # 惯量 - 立体形状
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
    # 惯量 - 薄壳体
    "truncated_cone_shell",
    "cylinder_lateral_shell",
    "cylinder_total_shell",
    "cone_lateral_shell",
    "hemisphere_shell",
    "sphere_shell",
    "torus_shell",
    # 惯量张量
    "solid_cylinder_tensor",
    "hollow_cylinder_tensor",
    "parallel_axis_tensor",
    "inertia_about_axis",
    # 气缸
    "push_force",
    "pull_force",
    "air_consumption",
    "cylinder_select",
    "STD_BORES",
    # 电机
    "motor_calc",
    "motor_select",
    "MotorSpec",
    "MOTOR_DB",
    "servo_select",
    "ServoMotorSpec",
    "SERVO_DB",
]
