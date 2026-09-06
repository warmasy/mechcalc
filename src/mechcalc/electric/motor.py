"""普通电机（三相异步电机）选型模块

内置简化电机数据库，支持按负载扭矩和转速选型。

用法:
    >>> raw = motor_select(load_torque=5.0, load_speed=1400)
    >>> raw['selected_model']
    'YS90L4'

    # Result 模式（带参数记录，可 JSON 序列化）
    >>> r = to_result(motor_select, 5.0, 1400)
    >>> r.selected_model
    'YS90L4'
"""

import math
from dataclasses import dataclass

from ..core.units import QuantityLike, set_quantity, to_mag


@dataclass
class MotorSpec:
    """三相异步电机规格（4极）"""

    model: str
    power: float  # W
    speed: float  # rpm
    torque: float  # N·m


# 简化电机数据库
MOTOR_DB: list[MotorSpec] = [
    MotorSpec("YS5624", 90, 1400, 0.61),
    MotorSpec("YS6324", 120, 1400, 0.82),
    MotorSpec("YS7124", 180, 1400, 1.23),
    MotorSpec("YS8024", 370, 1400, 2.52),
    MotorSpec("YS90S4", 550, 1400, 3.75),
    MotorSpec("YS90L4", 750, 1400, 5.11),
    MotorSpec("YS100L1", 1100, 1430, 7.34),
    MotorSpec("YS100L2", 1500, 1430, 10.0),
    MotorSpec("YS112M", 2200, 1440, 14.6),
    MotorSpec("YS132S", 3000, 1440, 19.9),
    MotorSpec("YS132M", 4000, 1440, 26.5),
    MotorSpec("YS160M", 5500, 1460, 36.0),
    MotorSpec("YS160L", 7500, 1460, 49.0),
]


def motor_select(
    load_torque: QuantityLike,
    load_speed: QuantityLike,
    safety_factor: float = 1.2,
) -> dict:
    """
    普通电机综合选型。

    需求扭矩 = 负载扭矩 × 安全系数；
    需求功率 = 需求扭矩 × 角速度；
    从内置数据库匹配扭矩/转速/功率均满足的最小型号。

    :param load_torque: 负载扭矩(N*m)
    :param load_speed: 负载转速(rpm)
    :param safety_factor: 安全系数(None)，默认 1.2
    :return: 选型结果 dict
    """
    T_load = set_quantity(load_torque, "N*m")
    n_load = set_quantity(load_speed, "rpm")

    T_req = (T_load * float(safety_factor)).to("N*m")
    n_rpm = to_mag(n_load, "rpm")
    T_req_Nm = to_mag(T_req, "N*m")

    P_req_W = T_req_Nm * 2 * math.pi * n_rpm / 60

    selected = None
    for motor in MOTOR_DB:
        if motor.torque >= T_req_Nm and motor.speed >= n_rpm and motor.power >= P_req_W:
            selected = motor
            break

    if selected is None:
        return {
            "error": "数据库中无满足条件的电机",
            "required_torque_Nm": round(T_req_Nm, 3),
            "required_speed_rpm": round(n_rpm, 1),
            "required_power_W": round(P_req_W, 1),
        }

    return {
        "selected_model": selected.model,
        "rated_power_W": selected.power,
        "rated_speed_rpm": selected.speed,
        "rated_torque_Nm": selected.torque,
        "required_torque_Nm": round(T_req_Nm, 3),
        "required_speed_rpm": round(n_rpm, 1),
        "required_power_W": round(P_req_W, 1),
        "torque_margin": round(selected.torque / T_req_Nm, 2) if T_req_Nm > 0 else None,
        "speed_margin": round(selected.speed / n_rpm, 2) if n_rpm > 0 else None,
    }
