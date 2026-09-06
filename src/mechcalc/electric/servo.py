"""伺服电机选型模块

内置简化伺服电机数据库，支持综合选型及惯量比校验。

用法:
    >>> raw = servo_select(load_torque=2.0, max_speed=3000, load_inertia=0.001, accel_time=0.1)
    >>> raw['selected_model']
    'MS200'
"""

import math
from dataclasses import dataclass

from ..core.units import Q_, QuantityLike, set_quantity, to_mag


@dataclass
class ServoMotorSpec:
    """伺服电机规格"""

    model: str
    rated_power: float  # W
    rated_torque: float  # N·m
    rated_speed: float  # rpm
    max_torque: float  # N·m
    rotor_inertia: float  # kg·m²


# 简化的伺服电机数据库
SERVO_DB: list[ServoMotorSpec] = [
    ServoMotorSpec("MS40", 40, 0.127, 3000, 0.382, 0.013e-6),
    ServoMotorSpec("MS60", 60, 0.191, 3000, 0.573, 0.019e-6),
    ServoMotorSpec("MS100", 100, 0.318, 3000, 0.955, 0.031e-6),
    ServoMotorSpec("MS200", 200, 0.637, 3000, 1.91, 0.042e-6),
    ServoMotorSpec("MS400", 400, 1.30, 3000, 4.55, 0.042e-6),
    ServoMotorSpec("MS750", 750, 2.40, 3000, 7.70, 0.146e-6),
    ServoMotorSpec("MS1k", 1000, 3.18, 3000, 9.55, 0.37e-6),
    ServoMotorSpec("MS1.5k", 1500, 4.78, 3000, 14.3, 0.62e-6),
    ServoMotorSpec("MS2k", 2000, 6.37, 3000, 19.1, 0.87e-6),
    ServoMotorSpec("MS3k", 3000, 9.55, 3000, 28.6, 1.6e-6),
    ServoMotorSpec("MS5k", 5000, 15.9, 3000, 47.7, 2.5e-6),
]


def servo_select(
    load_torque: QuantityLike,
    max_speed: QuantityLike,
    load_inertia: QuantityLike = None,
    accel_time: QuantityLike = None,
    safety_factor: float = 1.5,
    reducer_ratio: float = 1.0,
    max_inertia_ratio: float = 20.0,
) -> dict:
    """
    伺服电机综合选型。

    需求扭矩 = 负载扭矩 × 安全系数 / 减速比；
    峰值扭矩 = 需求扭矩 + 加速扭矩(J·ω/t)；
    匹配额定扭矩/峰值扭矩/转速/功率均满足的型号，并做惯量比校验。

    :param load_torque: 负载扭矩(N*m)
    :param max_speed: 最大转速(rpm)
    :param load_inertia: 负载惯量(kg*m**2)，可选
    :param accel_time: 加速时间(s)，可选
    :param safety_factor: 安全系数(None)，默认 1.5
    :param reducer_ratio: 减速比(None)，默认 1.0
    :param max_inertia_ratio: 最大允许惯量比(None)，默认 20.0
    :return: 选型结果 dict
    """
    T_load = set_quantity(load_torque, "N*m")
    n_load = set_quantity(max_speed, "rpm")

    T_req = (T_load * float(safety_factor) / float(reducer_ratio)).to("N*m")
    n_motor = (n_load * float(reducer_ratio)).to("rpm")
    n_motor_rpm = to_mag(n_motor, "rpm")

    omega = Q_(n_motor_rpm * 2 * math.pi / 60, "rad/s")
    P_req = (T_req * omega).to("W")

    T_accel = Q_(0.0, "N*m")
    if load_inertia is not None and accel_time is not None:
        J = set_quantity(load_inertia, "kg*m**2")
        t = set_quantity(accel_time, "s")
        T_accel = (J * omega / t).to("N*m")

    T_peak = (T_req + T_accel).to("N*m")

    T_req_Nm = to_mag(T_req, "N*m")
    T_peak_Nm = to_mag(T_peak, "N*m")
    P_req_W = to_mag(P_req, "W")

    selected = None
    for motor in SERVO_DB:
        if (
            motor.rated_torque >= T_req_Nm
            and motor.max_torque >= T_peak_Nm
            and motor.rated_speed >= n_motor_rpm
            and motor.rated_power >= P_req_W
        ):
            selected = motor
            break

    if selected is None:
        return {
            "error": "数据库中无满足条件的电机，请增大减速比或选用更大电机",
            "required_torque_Nm": round(T_req_Nm, 3),
            "peak_torque_Nm": round(T_peak_Nm, 3),
            "required_speed_rpm": round(n_motor_rpm, 1),
            "required_power_W": round(P_req_W, 1),
        }

    inertia_check = None
    if load_inertia is not None:
        J_load = set_quantity(load_inertia, "kg*m**2")
        J_reflected = selected.rotor_inertia * (float(reducer_ratio) ** 2)
        ratio = to_mag(J_load, "kg*m**2") / J_reflected if J_reflected > 0 else float("inf")
        inertia_check = {
            "load_inertia_kg_m2": round(to_mag(J_load, "kg*m**2"), 6),
            "motor_rotor_inertia_kg_m2": selected.rotor_inertia,
            "inertia_ratio": round(ratio, 2),
            "max_allowed_ratio": float(max_inertia_ratio),
            "passed": ratio <= float(max_inertia_ratio),
        }

    return {
        "selected_model": selected.model,
        "rated_power_W": selected.rated_power,
        "rated_torque_Nm": selected.rated_torque,
        "max_torque_Nm": selected.max_torque,
        "rated_speed_rpm": selected.rated_speed,
        "required_torque_Nm": round(T_req_Nm, 3),
        "peak_torque_Nm": round(T_peak_Nm, 3),
        "required_speed_rpm": round(n_motor_rpm, 1),
        "required_power_W": round(P_req_W, 1),
        "inertia_ratio_check": inertia_check,
        "reducer_ratio": float(reducer_ratio),
    }
