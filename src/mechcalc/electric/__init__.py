"""电机计算模块

根据负载条件计算选择电机时所需的必要参数（扭矩、转速、功率）。
只算参数，不做型号推荐。
"""

from .motor_calc import motor_calc

__all__ = [
    'motor_calc',
]
