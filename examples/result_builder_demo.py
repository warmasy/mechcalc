"""惯量返回构造器方案 v2（参照用，非测试）

改进点：
- 惯量、体积、y_bar 等全部在函数体里算好
- return 只做赋值（inertia_result 一行，无计算表达式）
"""

import math

import mechcalc as mc
from mechcalc.core.units import set_quantity, to_mag
from mechcalc.inertia._utils import _make_tensor, _sum_inertia, _validate_positive


# ==================== 返回结构构造器 ====================

def inertia_result(
    *,
    Jx=None, Jy=None, Jz=None, J_rho_O=None, plane=False,
    y_bar=None, x_bar=None, volume=None, area=None,
    **extra,
):
    """一行构造惯量返回：轴惯量 + 自动完整张量 + 几何信息 + 额外字段（None 自动过滤）。"""
    result = {}
    for key, val in (("J_x", Jx), ("J_y", Jy), ("J_z", Jz), ("J_rho_O", J_rho_O)):
        if val is not None:
            result[key] = val
    result["tensor"] = _make_tensor(Jx=Jx, Jy=Jy, Jz=Jz, J_rho_O=J_rho_O, plane=plane)
    for key, val in (("y_bar", y_bar), ("x_bar", x_bar), ("volume", volume), ("area", area)):
        if val is not None:
            result[key] = val
    result.update(extra)
    return result


# ==================== 函数体先算 + return 纯赋值 ====================

def cylinder(mass, diameter, length):
    """实心圆柱惯量。"""
    m = set_quantity(mass, "kg")
    D = set_quantity(diameter, "mm")
    h = set_quantity(length, "mm")
    _validate_positive(mass=m, diameter=D, length=h)
    R = D / 2.0

    # 惯量
    J_y = _sum_inertia([(0.5, m, R)])                      # 绕对称轴
    J_x = _sum_inertia([(0.25, m, R), (1.0 / 12.0, m, h)])  # 绕直径

    # 几何
    y_bar = (h / 2.0).to("m")
    volume = (math.pi * R**2 * h).to("m**3")

    return inertia_result(Jx=J_x, Jy=J_y, Jz=J_x, y_bar=y_bar, volume=volume)


def sphere(mass, radius):
    """圆球惯量。"""
    m = set_quantity(mass, "kg")
    R = set_quantity(radius, "mm")
    _validate_positive(mass=m, radius=R)

    # 惯量
    J = _sum_inertia([(0.4, m, R)])

    # 几何
    volume = (4.0 * math.pi * R**3 / 3.0).to("m**3")

    return inertia_result(Jx=J, Jy=J, Jz=J, volume=volume)


def circular_plate(mass, radius):
    """圆板惯量。"""
    m = set_quantity(mass, "kg")
    r = set_quantity(radius, "mm")
    _validate_positive(mass=m, radius=r)

    # 惯量
    J_xy = _sum_inertia([(0.25, m, r)])   # 绕直径
    J_rho = _sum_inertia([(0.5, m, r)])   # 绕中心轴

    # 几何
    area = (math.pi * r**2).to("m**2")
    i_x = (r / 2.0).to("m")
    i_rho_O = (r / math.sqrt(2.0)).to("m")

    return inertia_result(
        Jx=J_xy, Jy=J_xy, J_rho_O=J_rho,
        area=area, i_x=i_x, i_y=i_x, i_rho_O=i_rho_O,
    )


def arc_rod(mass, radius, alpha):
    """圆弧杆惯量（特殊轴函数示例）。"""
    m = set_quantity(mass, "kg")
    R = set_quantity(radius, "mm")
    _validate_positive(mass=m, radius=R)
    a = math.radians(alpha)
    if a <= 0 or a > math.pi:
        raise ValueError("alpha 半张角应在 (0°, 180°] 范围内")
    sin_a, cos_a = math.sin(a), math.cos(a)

    # 惯量（系数含角度）
    J_x = _sum_inertia([(0.5 - sin_a * cos_a / (2.0 * a), m, R)])
    J_y_prime = _sum_inertia([(0.5 + sin_a * cos_a / (2.0 * a), m, R)])
    J_y = _sum_inertia([(0.5 + sin_a * cos_a / (2.0 * a) - (sin_a / a) ** 2, m, R)])
    J_rho = _sum_inertia([(1.0, m, R)])

    # 几何
    x_bar = (R * sin_a / a).to("m")
    arc_length = (2.0 * a * R).to("m")

    return inertia_result(
        Jx=J_x, Jy=J_y, J_rho_O=J_rho,
        J_y_prime=J_y_prime,
        x_bar=x_bar, arc_length=arc_length,
    )


# ==================== 验证：与现有函数完全一致 ====================

def verify():
    print("===== 函数体先算 + return 纯赋值 vs 现有函数 =====\n")
    checks = [
        ("cylinder", cylinder(10, 100, 200), mc.cylinder(10, 100, 200)),
        ("sphere", sphere(10, 100), mc.sphere(10, 100)),
        ("circular_plate", circular_plate(10, 100), mc.circular_plate(10, 100)),
        ("arc_rod", arc_rod(10, 100, 90), mc.arc_rod(10, 100, 90)),
    ]
    all_ok = True
    for name, new, old in checks:
        keys_ok = set(new.keys()) == set(old.keys())
        val_ok = True
        for k in (set(new.keys()) & set(old.keys())) - {"tensor"}:
            vn, vo = new[k], old[k]
            if hasattr(vn, "magnitude") and hasattr(vo, "magnitude"):
                try:
                    diff = abs(to_mag(vn, "kg*m**2") - to_mag(vo, "kg*m**2"))
                except Exception:
                    diff = abs(float(vn.magnitude) - float(vo.magnitude))
                if diff > 1e-9:
                    val_ok = False
                    break
        ok = "✓" if (keys_ok and val_ok) else "✗"
        all_ok = all_ok and ok == "✓"
        print(f"  {name:<15} {ok}  键一致: {keys_ok}  值一致: {val_ok}")
    print(f"\n结果: {'全部一致，可放心落地' if all_ok else '有差异，需检查'}")

    print("\n===== cylinder 函数完整代码（函数体先算，return 纯赋值）=====")
    print("def cylinder(mass, diameter, length):")
    print("    ... 参数准备 ...")
    print("    # 惯量")
    print("    J_y = _sum_inertia([(0.5, m, R)])")
    print("    J_x = _sum_inertia([(0.25, m, R), (1.0/12.0, m, h)])")
    print("    # 几何")
    print("    y_bar = (h/2.0).to('m')")
    print("    volume = (math.pi*R**2*h).to('m**3')")
    print("    return inertia_result(Jx=J_x, Jy=J_y, Jz=J_x, y_bar=y_bar, volume=volume)")


if __name__ == "__main__":
    verify()
