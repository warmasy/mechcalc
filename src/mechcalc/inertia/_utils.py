"""惯量计算内部工具函数"""

import math

import numpy as np

from ..core.units import Q_, QuantityLike, to_mag


def _to_deg(value: QuantityLike) -> float:
    """将角度输入转为度数值。支持裸数值（默认度）或 pint Quantity。"""
    if hasattr(value, "magnitude"):
        return float(value.to("deg").magnitude)
    return float(value)


def _to_rad(value: QuantityLike) -> float:
    """将角度输入转为弧度数值。支持裸数值（默认度）或 pint Quantity。"""
    return math.radians(_to_deg(value))


def _validate_positive(**kwargs: QuantityLike) -> None:
    """验证所有参数为正数。"""
    for name, value in kwargs.items():
        v = float(value) if not hasattr(value, "magnitude") else float(value.magnitude)
        if v <= 0:
            raise ValueError(f"参数 {name} 必须为正数，当前值: {v}")


def _validate_nonnegative(**kwargs: QuantityLike) -> None:
    """验证所有参数非负（允许 0，用于长度可能退化的项）。"""
    for name, value in kwargs.items():
        v = float(value) if not hasattr(value, "magnitude") else float(value.magnitude)
        if v < 0:
            raise ValueError(f"参数 {name} 不能为负，当前值: {v}")


def _sum_inertia(terms: list, unit: str = "kg*m**2"):
    """
    多项惯量求和（通用核心）：J = Σ 系数 × 质量 × 长度²。

    所有规则形状的惯量都能写成若干项「系数 × m × 长度²」之和，
    本函数统一做：参数验证 → 逐项累加 → 单位换算。

    :param terms: [(系数, 质量, 长度), ...]
        系数: 无量纲 float（常数或角度函数，如 0.4 = 2/5、1/12）
        质量: Quantity(kg) 或裸数（必须为正）
        长度: 半径/边长等，Quantity 或裸数（允许 0，表示该项退化）
    :param unit: 结果单位，默认 kg·m²
    :return: Quantity(unit)

    示例:
        _sum_inertia([(0.4, m, R)])                      # 球: 2/5·mR²
        _sum_inertia([(0.25, m, R), (1/12, m, L)])       # 圆柱绕直径: m(3R²+L²)/12
    """
    total = None
    for coef, mass, length in terms:
        # 参数验证集中在通用核心：质量必须为正，长度允许 0（退化项）
        _validate_positive(mass=mass)
        _validate_nonnegative(length=length)
        term = float(coef) * mass * length**2
        total = term if total is None else total + term
    return total.to(unit)


def inertia_result(
    *,
    Jx=None,
    Jy=None,
    Jz=None,
    J_rho_O=None,
    plane: bool = False,
    y_bar=None,
    x_bar=None,
    volume=None,
    area=None,
    tensor=None,
    **extra,
) -> dict:
    """
    惯量计算返回结构构造器：一行组装「轴惯量 + 完整张量 + 几何信息」。

    用法：惯量/几何都在函数体算好，return 只做赋值：

        return inertia_result(Jx=J_x, Jy=J_y, Jz=J_x, y_bar=y_bar, volume=volume)

    :param Jx/Jy/Jz/J_rho_O: 各轴转动惯量（自动生成 J_x/J_y/J_z/J_rho_O 键）
    :param plane: 平面形状用垂直轴定理推导 Jz（用于张量）
    :param y_bar/x_bar/volume/area: 常见几何信息（None 自动省略）
    :param tensor: 显式张量覆盖（当返回键与张量轴不一致时使用，
        如旋转对称壳返回 J_x(直径)/J_y(对称轴)，张量 = diag(Jx, Jx, Jy)）
    :param extra: 其他任意字段原样透传（如 i_x、J_a、J_y_prime、arc_length...）
    :return: dict，含 'tensor'（3×3 完整张量，轴信息不足时为 None）
    """
    result: dict = {}
    for key, val in (("J_x", Jx), ("J_y", Jy), ("J_z", Jz), ("J_rho_O", J_rho_O)):
        if val is not None:
            result[key] = val
    if tensor is None:
        tensor = _make_tensor(Jx=Jx, Jy=Jy, Jz=Jz, J_rho_O=J_rho_O, plane=plane)
    result["tensor"] = tensor
    for key, val in (("y_bar", y_bar), ("x_bar", x_bar), ("volume", volume), ("area", area)):
        if val is not None:
            result[key] = val
    result.update(extra)
    return result


def _make_tensor(
    Jx=None,
    Jy=None,
    Jz=None,
    J_rho_O=None,
    plane: bool = False,
) -> object:
    """
    从标准轴分量构造 3×3 惯性张量（质心系，对称形状非对角 = 0）。

    规则:
        - Jz 缺失时优先用 J_rho_O（绕垂直对称轴的极惯量）
        - 平面形状（plane=True）用垂直轴定理 Jz = Jx + Jy
        - 任一分量缺失且无法推导 -> 返回 None（不构成完整张量）

    :param Jx: 绕 x 轴转动惯量(kg·m²)
    :param Jy: 绕 y 轴转动惯量(kg·m²)
    :param Jz: 绕 z 轴转动惯量(kg·m²)
    :param J_rho_O: 绕垂直对称轴(z)的极惯量(kg·m²)
    :param plane: 质量是否全在 x-y 平面（可用垂直轴定理）
    :return: 3×3 惯性张量(kg·m²)，或 None
    """
    if Jz is None and J_rho_O is not None:
        Jz = J_rho_O
    if Jz is None and plane and Jx is not None and Jy is not None:
        Jz = Jx + Jy
    if Jx is None or Jy is None or Jz is None:
        return None
    mag = np.diag(
        [
            float(to_mag(Jx, "kg*m**2")),
            float(to_mag(Jy, "kg*m**2")),
            float(to_mag(Jz, "kg*m**2")),
        ]
    )
    return Q_(mag, "kg*m**2")


def _disk_slice_Jx(
    mass: float, ybar: float, radii_at_z, z0: float, z1: float, n: int = 2000
) -> float:
    """
    旋转对称体绕直径轴(过质心)惯量的数值积分（圆盘切片法）。

    对绕 z 轴旋转对称的物体，绕任意直径轴(x)的惯量:
        Jx = Σ dm·(r(z)²/4 + (z - ybar)²)
    其中 dm = 质量·dV/V，r(z) 为高度 z 处的切片半径。

    :param mass: 总质量(kg)
    :param ybar: 质心高度(m)
    :param radii_at_z: 函数 r(z) -> 半径(m)
    :param z0, z1: 积分范围(沿对称轴, m)
    :param n: 切片数
    :return: 绕直径轴惯量(kg·m²)
    """
    dz = (z1 - z0) / n
    Jx = 0.0
    for i in range(n):
        z = z0 + (i + 0.5) * dz
        rad = radii_at_z(z)
        dV = math.pi * rad**2 * dz
        dm = mass * dV / _body_volume(radii_at_z, z0, z1)
        Jx += dm * (rad**2 / 4.0 + (z - ybar) ** 2)
    return Jx


def _body_volume(radii_at_z, z0: float, z1: float, n: int = 2000) -> float:
    """旋转对称体体积（圆盘切片求和）"""
    dz = (z1 - z0) / n
    V = 0.0
    for i in range(n):
        z = z0 + (i + 0.5) * dz
        rad = radii_at_z(z)
        V += math.pi * rad**2 * dz
    return V
