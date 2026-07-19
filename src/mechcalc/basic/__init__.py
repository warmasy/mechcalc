"""基础力学计算模块

提供机械工程中最常用的基础公式计算，供高级模块复用。

函数默认返回原始 pint Quantity，可直接链式计算；
需要带参数记录的 Result 时，用 to_result 现场包装。

用法:
    # 默认：链式计算
    F = gravity(mass=100)
    a = (F / 50).to('m/s**2')  # 直接参与后续计算

    # 需要 Result（参数记录、JSON 序列化）时：
    result = to_result(gravity, mass=100)
    print(result.value)  # {'value': 980.665, 'unit': 'N'}
"""

from .kinematics import (
    velocity, displacement, acceleration, uniform_motion, uniform_acceleration,
)
from .dynamics import (
    gravity, friction, centrifugal_force, inertia_force,
)
from .rotation import (
    angular_velocity, angular_acceleration, tangential_velocity, tangential_acceleration,
)
from .energy import (
    kinetic_energy, potential_energy, power, torque_power,
)
from .mass_volume import (
    mass_from_density, cylinder_volume, sphere_volume, cuboid_volume,
)
from .motion3d import (
    point_velocity, centripetal_acceleration,
    rotational_kinetic_energy, angular_momentum, gravity_force,
)

__all__ = [
    # 运动学
    'velocity', 'displacement', 'acceleration',
    'uniform_motion', 'uniform_acceleration',
    # 动力学
    'gravity', 'friction', 'centrifugal_force', 'inertia_force',
    # 旋转运动
    'angular_velocity', 'angular_acceleration',
    'tangential_velocity', 'tangential_acceleration',
    # 能量功率
    'kinetic_energy', 'potential_energy', 'power', 'torque_power',
    # 质量体积
    'mass_from_density', 'cylinder_volume', 'sphere_volume', 'cuboid_volume',
    # 三维运动（向量化）
    'point_velocity', 'centripetal_acceleration',
    'rotational_kinetic_energy', 'angular_momentum', 'gravity_force',
]
