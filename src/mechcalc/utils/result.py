"""计算结果封装与 Result 调度

Result 同时支持 dict 接口和属性访问。

计算函数默认返回原始 pint Quantity（内部链式计算）；
需要带参数记录的 Result 时，用 to_result 现场包装，函数本身无需任何装饰：

    >>> from mechcalc import to_result, push_force
    >>> r = to_result(push_force, 0.4, 32)
    >>> r.F
    {'value': 273.4, 'unit': 'N'}
    >>> r.params
    {'P': {'value': 0.4, 'unit': 'MPa'}, 'D': {'value': 32.0, 'unit': 'mm'}, ...}
"""

import functools
import inspect
import re
from typing import Dict, List, Any, Optional

from ..core.units import Q_, to_mag, to_unit


class Result(dict):
    """
    计算结果封装 - 同时支持 dict 接口和属性访问

    继承 dict，所以可以直接:
        - result['F']           # 取某个结果（像 dict）
        - result.F              # 属性方式
        - for k, v in result.items()  # 遍历
        - dict(result)          # 转为纯 dict

    属性:
        params: dict - 输入参数
    """

    _RESERVED_KEYS = {'params'}

    def __init__(self, params: Dict[str, Any], results: Dict[str, Any]):
        conflicts = set(results.keys()) & self._RESERVED_KEYS
        if conflicts:
            raise ValueError(
                f"Result keys {conflicts} conflict with reserved attributes "
                f"{self._RESERVED_KEYS}. Please rename these result keys."
            )
        super().__init__(results)
        self.params = params

    def __getattr__(self, key: str) -> Any:
        if key in ('__dict__', '__class__', '__slots__'):
            raise AttributeError(key)
        if key in self:
            return self[key]
        try:
            return self.__dict__[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __setattr__(self, key: str, value: Any) -> None:
        if key in self._RESERVED_KEYS:
            self.__dict__[key] = value
        else:
            self[key] = value

    def __repr__(self) -> str:
        return f"Result({dict(self)})"

    def __str__(self) -> str:
        lines = ["Params:"]
        for k, v in self.params.items():
            lines.append(f"  {k} = {v}")
        lines.append("Results:")
        for k, v in self.items():
            lines.append(f"  {k} = {v}")
        return "\n".join(lines)

    def to_api(self) -> Dict[str, Any]:
        """转换为 API/JSON 可用的完整字典结构"""
        return {
            'params': self.params,
            **dict(self),
        }


# ==================== Result 调度 ====================

def _parse_param_units_from_docstring(docstring: Optional[str]) -> Dict[str, str]:
    """
    从 Sphinx 风格 docstring 的 :param 行中提取参数单位。

    匹配规则:
        :param name: 描述文字(单位)
        括号内为空、None、- 等视为无单位。

    示例:
        :param P: 工作压力(MPa)        → {'P': 'MPa'}
        :param D: 气缸缸径(mm)         → {'D': 'mm'}
        :param efficiency: 效率(None)    → {'efficiency': ''}
    """
    units: Dict[str, str] = {}
    if not docstring:
        return units

    for line in docstring.split('\n'):
        line = line.strip()
        if not line.startswith(':param'):
            continue

        m = re.match(r':param\s+(\w+)', line)
        if not m:
            continue
        name = m.group(1)

        paren = re.search(r'\(([^)]*)\)', line)
        if paren:
            unit = paren.group(1).strip()
            if unit and unit.lower() not in ('none', '-', 'null', 'na', 'n/a'):
                units[name] = unit
            else:
                units[name] = ''
        else:
            units[name] = ''

    return units


@functools.lru_cache(maxsize=None)
def _param_units_of(func) -> Dict[str, str]:
    """缓存每个函数的 docstring 参数单位解析结果"""
    return _parse_param_units_from_docstring(func.__doc__)


def to_result(func, *args, **kwargs) -> Result:
    """
    调用计算函数并返回 Result（带参数记录和单位）。

    函数无需装饰，现场完成：签名内省记录参数、
    docstring 解析默认单位、结果格式化。

    参数:
        func: 计算函数（如 push_force）
        *args, **kwargs: 原样传给 func

    返回:
        Result

    示例:
        to_result(push_force, 0.4, 32)
        to_result(motor_calc, load_torque=5.0, load_speed=1400)
    """
    param_units = _param_units_of(func)

    bound = inspect.signature(func).bind(*args, **kwargs)
    bound.apply_defaults()

    params: Dict[str, Any] = {}
    for name, val in bound.arguments.items():
        if val is None:
            params[name] = None
        elif hasattr(val, "magnitude"):
            params[name] = {"value": to_mag(val), "unit": to_unit(val)}
        else:
            unit = param_units.get(name, "")
            if isinstance(unit, str) and unit:
                qty = Q_(val, unit)
                params[name] = {"value": to_mag(qty), "unit": to_unit(qty)}
            else:
                params[name] = val

    raw = func(*args, **kwargs)
    return Result(params=params, results=_format_results(raw))


def _format_results(raw: Any) -> Dict[str, Any]:
    """将原始计算结果格式化为 Result.results 的标准结构"""
    if raw is None:
        return {}

    if hasattr(raw, "magnitude"):
        return {"value": {"value": to_mag(raw), "unit": to_unit(raw)}}

    if isinstance(raw, dict):
        results: Dict[str, Any] = {}
        for k, v in raw.items():
            if hasattr(v, "magnitude"):
                results[k] = {"value": to_mag(v), "unit": to_unit(v)}
            elif isinstance(v, dict):
                results[k] = v
            else:
                results[k] = v
        return results

    if isinstance(raw, (tuple, list)):
        results = {}
        for i, val in enumerate(raw):
            k = f"value_{i}"
            if hasattr(val, "magnitude"):
                results[k] = {"value": to_mag(val), "unit": to_unit(val)}
            else:
                results[k] = val
        return results

    return {"result": raw}


# ==================== 批量计算工具 ====================

def calc_batch(func, cases: List[Dict[str, Any]]) -> List[Result]:
    """
    批量计算工具。

    参数:
        func: 计算函数（如 push_force）
        cases: 参数列表，每个元素是一个 dict

    返回:
        List[Result]

    示例:
        cases = [
            {'P': 0.4, 'D': 32},
            {'P': 0.6, 'D': 50},
        ]
        results = calc_batch(push_force, cases)
    """
    results = []
    for case in cases:
        try:
            results.append(to_result(func, **case))
        except Exception as e:
            results.append(
                Result(
                    params=case,
                    results={'error': str(e)},
                )
            )
    return results
