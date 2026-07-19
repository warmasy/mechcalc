"""单位系统

基于 pint 的单位管理，提供常用单位的快捷创建函数。

使用方式:
  1. 快捷函数: kg(10), mm(100), MPa(0.6)
  2. 直接使用 Q_: Q_(10, 'kg'), Q_(100, 'mm')
  3. 组合单位: kg_m2(0.015), m_s(10)
"""

from typing import Dict, List, Optional, Union, Any
from pint import UnitRegistry

# 全局单位注册表
ureg = UnitRegistry()
Q_ = ureg.Quantity  # type: ignore


# ==================== 分类单位字典 ====================
NESTED_UNITS: Dict[str, Dict[str, str]] = {
    '质量': {'kg': 'kg', 'g': 'g', 'mg': 'mg', 't': 't'},
    '长度': {'mm': 'mm', 'cm': 'cm', 'dm': 'dm', 'm': 'm', 'km': 'km', 'um': 'um', 'nm': 'nm'},
    '力': {'N': 'N', 'kN': 'kN', 'kgf': 'kgf'},
    '压力': {'Pa': 'Pa', 'kPa': 'kPa', 'MPa': 'MPa', 'bar': 'bar', 'psi': 'psi'},
    '能量': {'J': 'J', 'kJ': 'kJ', 'MJ': 'MJ'},
    '功率': {'W': 'W', 'kW': 'kW', 'MW': 'MW'},
    '扭矩': {'Nm': 'N*m', 'Nmm': 'N*mm', 'kgfm': 'kgf*m'},
    '转速': {'rpm': 'rpm', 'Hz': 'Hz'},
    '时间': {'s': 's', 'ms': 'ms', 'min': 'min', 'h': 'h'},
    '角度': {'deg': 'deg', 'rad': 'rad'},
    '体积': {'L': 'L', 'mL': 'mL'},
}

FLAT_UNITS: Dict[str, str] = {}
for category, units in NESTED_UNITS.items():
    FLAT_UNITS.update(units)


# ==================== 动态生成快捷函数 ====================
def __getattr__(name: str) -> Any:
    """动态生成单位快捷函数，如 kg(10) -> Q_(10, 'kg')"""
    unit = FLAT_UNITS.get(name)
    if unit is not None:
        def _unit_func(value):
            return Q_(value, unit)
        _unit_func.__name__ = name
        _unit_func.__doc__ = f"创建 {unit} 单位的 Quantity"
        return _unit_func
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# ==================== 组合单位（手动定义）====================
def kg_m2(value):
    """惯量单位 kg·m²"""
    return Q_(value, 'kg*m**2')


def kg_m3(value):
    """密度单位 kg/m³"""
    return Q_(value, 'kg/m**3')


def m_min(value):
    """速度单位 m/min"""
    return Q_(value, 'm/min')


def m_s(value):
    """速度单位 m/s"""
    return Q_(value, 'm/s')


def m_s2(value):
    """加速度单位 m/s²"""
    return Q_(value, 'm/s**2')


def mm_s(value):
    """速度单位 mm/s"""
    return Q_(value, 'mm/s')


def g_cm3(value):
    """密度单位 g/cm³"""
    return Q_(value, 'g/cm**3')


def Pa_s(value):
    """粘度单位 Pa·s"""
    return Q_(value, 'Pa*s')


def cP(value):
    """粘度单位 cP (centipoise)"""
    return Q_(value, 'cP')


# ==================== 工具函数 ====================

def to_mag(qty, unit=None):
    """
    提取 pint 对象的数值，支持可选的单位转换。

    标量返回 float；数组（向量/矩阵）返回嵌套 list，保证可 JSON 序列化。

    参数:
        qty: pint Quantity 对象或纯数值
        unit: 目标单位字符串（可选）

    返回:
        float 或 list

    示例:
        to_mag(MPa(12))           -> 12.0
        to_mag(MPa(12), 'Pa')     -> 12000000.0
        to_mag(10)                -> 10.0
        to_mag(Q_([1, 2], 'm'))   -> [1.0, 2.0]
    """
    if hasattr(qty, 'magnitude'):
        mag = qty.to(unit).magnitude if unit is not None else qty.magnitude
        tolist = getattr(mag, 'tolist', None)
        return tolist() if tolist is not None else float(mag)
    return float(qty)


def to_unit(qty, unit=None, compact=True):
    """
    提取 pint 对象的单位字符串。

    参数:
        qty: pint Quantity 对象
        unit: 目标单位字符串（可选）
        compact: True 返回简写格式

    返回:
        str: 单位字符串；非 Quantity 返回空字符串
    """
    if not hasattr(qty, 'magnitude') or not hasattr(qty, 'units'):
        return ""

    if unit and hasattr(qty, 'to'):
        qty = qty.to(unit)

    if compact:
        return f"{qty.units:~P}"
    return str(qty.units)


def ensure_quantity(value, unit: Optional[str] = None):
    """
    统一将纯数值或已有 Quantity 转为 pint Quantity。

    示例:
        ensure_quantity(10, 'mm')      -> 10 mm
        ensure_quantity(Q_(10, 'mm'))  -> 10 mm
        ensure_quantity(Q_(10, 'mm'), 'm') -> 0.01 m
    """
    if hasattr(value, 'magnitude'):
        if unit is not None:
            return value.to(unit)
        return value
    if unit is None:
        raise ValueError("unit must be provided when value is not a Quantity")
    return Q_(value, unit)


def ensure_float(value, unit: Optional[str] = None) -> float:
    """
    统一提取数值，无论输入是纯数值还是 Quantity。
    """
    if hasattr(value, 'magnitude'):
        if unit is not None:
            return float(value.to(unit).magnitude)
        return float(value.magnitude)
    return float(value)


