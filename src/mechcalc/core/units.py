"""单位系统

基于 pint 的单位管理，提供 Q_ 创建和单位转换工具。

使用方式:
  Q_(10, 'kg')      -> 10 kg
  Q_(100, 'mm')     -> 100 mm
  Q_(0.6, 'MPa')    -> 0.6 MPa
  Q_(0.015, 'kg*m**2') -> 0.015 kg·m²
"""

from typing import Any, TypeAlias

from pint import Quantity, UnitRegistry

# 全局单位注册表
ureg = UnitRegistry()
Q_ = ureg.Quantity  # type: ignore

# 类型别名：函数入参统一接受"裸数值（按文档默认单位解释）或 pint Quantity"
QuantityLike: TypeAlias = float | int | Quantity


# ==================== 工具函数 ====================


def to_mag(qty: QuantityLike, unit: str | None = None) -> Any:
    """
    提取 pint 对象的数值，支持可选的单位转换。

    标量返回 float；数组（向量/矩阵）返回嵌套 list，保证可 JSON 序列化。

    参数:
        qty: pint Quantity 对象或纯数值
        unit: 目标单位字符串（可选）

    返回:
        float 或 list

    示例:
        to_mag(Q_(12, 'MPa'))           -> 12.0
        to_mag(Q_(12, 'MPa'), 'Pa')     -> 12000000.0
        to_mag(10)                      -> 10.0
        to_mag(Q_([1, 2], 'm'))         -> [1.0, 2.0]
    """
    if hasattr(qty, "magnitude"):
        mag = qty.to(unit).magnitude if unit is not None else qty.magnitude
        tolist = getattr(mag, "tolist", None)
        return tolist() if tolist is not None else float(mag)
    return float(qty)


def to_unit(qty: Any, unit: str | None = None, compact: bool = True) -> str:
    """
    提取 pint 对象的单位字符串。

    参数:
        qty: pint Quantity 对象
        unit: 目标单位字符串（可选）
        compact: True 返回简写格式

    返回:
        str: 单位字符串；非 Quantity 返回空字符串
    """
    if not hasattr(qty, "magnitude") or not hasattr(qty, "units"):
        return ""

    if unit and hasattr(qty, "to"):
        qty = qty.to(unit)

    if compact:
        return f"{qty.units:~P}"
    return str(qty.units)


def set_quantity(value: QuantityLike, unit: str | None = None) -> Quantity:
    """
    统一将纯数值或已有 Quantity 转为 pint Quantity。

    参数:
        value: 纯数值或 pint Quantity
        unit: 目标单位字符串（纯数值时必须提供）

    示例:
        set_quantity(10, 'mm')           -> 10 mm
        set_quantity(Q_(10, 'mm'))       -> 10 mm
        set_quantity(Q_(10, 'mm'), 'm')  -> 0.01 m
    """
    if hasattr(value, "magnitude"):
        if unit is not None:
            return value.to(unit)
        return value
    if unit is None:
        raise ValueError("unit must be provided when value is not a Quantity")
    return Q_(value, unit)
