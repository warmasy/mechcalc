"""通用工具

结果封装与调度：Result、to_result、calc_batch。
"""

from .result import Result, calc_batch, to_result

__all__ = [
    'Result', 'calc_batch', 'to_result',
]
