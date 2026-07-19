"""电机需求参数计算

根据负载条件计算选择电机时所需的必要参数：
所需扭矩、所需转速、所需功率。

只算参数，不做型号推荐。

用法:
    >>> result = motor_calc(load_torque=5.0, load_speed=1400)
    >>> result['required_torque']   # 所需扭矩（含安全系数）
    <Quantity(6.0, 'newton * meter')>
    >>> result['required_power']    # 所需功率
    <Quantity(879.6..., 'watt')>

    # Result 模式（带参数记录，可 JSON 序列化）
    >>> from mechcalc import to_result
    >>> r = to_result(motor_calc, 5.0, 1400)
    >>> r.required_power
    {'value': 879.6..., 'unit': 'W'}
"""

from ..core.units import Nm, rpm
from ..basic.rotation import angular_velocity
from ..basic.energy import torque_power


def motor_calc(load_torque, load_speed, safety_factor=1.2):
    """
    电机需求参数计算。

    所需扭矩 = 负载扭矩 × 安全系数
    所需功率 = 所需扭矩 × 角速度

    :param load_torque: 负载扭矩(N*m)
    :param load_speed: 负载转速(rpm)
    :param safety_factor: 安全系数(None)，默认 1.2
    :return: {'required_torque': 所需扭矩(N·m),
              'required_speed': 所需转速(rpm),
              'required_power': 所需功率(W)}
    """
    T = Nm(load_torque) if not hasattr(load_torque, 'magnitude') else load_torque.to('N*m')
    n = rpm(load_speed) if not hasattr(load_speed, 'magnitude') else load_speed.to('rpm')

    T_req = (T * float(safety_factor)).to('N*m')

    # 复用 basic 模块：rpm -> rad/s，扭矩×角速度 -> 功率
    omega = angular_velocity(n)
    P_req = torque_power(T_req, omega)

    return {
        'required_torque': T_req,
        'required_speed': n,
        'required_power': P_req,
    }
