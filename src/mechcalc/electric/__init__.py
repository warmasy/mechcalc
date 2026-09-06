"""电机计算模块

- motor_calc:    电机需求参数计算（只算参数，不做型号推荐）
- motor_select:  普通电机（三相异步）综合选型（内置简化型号库）
- servo_select:  伺服电机综合选型（含惯量比校验）
"""

from .motor import MOTOR_DB, MotorSpec, motor_select
from .motor_calc import motor_calc
from .servo import SERVO_DB, ServoMotorSpec, servo_select

__all__ = [
    "motor_calc",
    "motor_select",
    "MotorSpec",
    "MOTOR_DB",
    "servo_select",
    "ServoMotorSpec",
    "SERVO_DB",
]
