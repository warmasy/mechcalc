"""通用惯量计算方案示例（参照用，非测试）

核心思路：J = Σ 系数 × 质量 × 长度²
- _sum_inertia(terms): 通用求和核心，接受多个 (系数, 质量, 长度) 元组
- 每个惯量函数 = 参数验证 + 调用 _sum_inertia 声明配置项
"""

import math

import mechcalc as mc
from mechcalc.core.units import Q_, set_quantity, to_mag
from mechcalc.inertia._utils import _validate_positive


# ==================== 通用核心 ====================

def _sum_inertia(terms, unit="kg*m**2"):
    """
    多项惯量求和：Σ 系数 × 质量 × 长度²。

    :param terms: [(系数, 质量, 长度), ...]
        系数: 无量纲 float（如 0.4 = 2/5、0.25 = 1/4、1/12）
        质量: 质量(kg)，Quantity 或裸数
        长度: 半径/边长等(m)，Quantity 或裸数
    :return: Quantity(kg·m²)

    例:
        _sum_inertia([(0.4, m, R)])                     # 球: 2/5·mR²
        _sum_inertia([(0.25, m, R), (1/12, m, L)])      # 圆柱绕直径: m(3R²+L²)/12
    """
    total = None
    for coef, mass, length in terms:
        # 参数验证集中在通用核心：质量/长度必须为正
        _validate_positive(mass=mass, length=length)
        term = float(coef) * mass * length**2
        total = term if total is None else total + term
    return total.to(unit)


# ==================== 用通用核心重构的惯量函数 ====================

def sphere(mass, radius):
    """圆球：J = (2/5)·m·R²（三个轴一样）"""
    m = set_quantity(mass, "kg")
    R = set_quantity(radius, "mm")
    J = _sum_inertia([(0.4, m, R)])          # 0.4 = 2/5
    return {
        "J_x": J, "J_y": J, "J_z": J,
        "volume": (4.0 * math.pi * R**3 / 3.0).to("m**3"),
    }


def circular_plate(mass, radius):
    """圆板：绕直径 (1/4)·mR²，绕中心轴 (1/2)·mR²"""
    m = set_quantity(mass, "kg")
    R = set_quantity(radius, "mm")
    J_xy = _sum_inertia([(0.25, m, R)])      # 0.25 = 1/4
    J_rho = _sum_inertia([(0.5, m, R)])      # 0.5 = 1/2
    return {
        "J_x": J_xy, "J_y": J_xy,
        "J_rho_O": J_rho,
        "area": (math.pi * R**2).to("m**2"),
    }


def cylinder(mass, diameter, length):
    """圆柱：绕对称轴 (1/2)·mR²；绕直径 m(3R²+L²)/12 = (1/4)mR² + (1/12)mL²"""
    m = set_quantity(mass, "kg")
    D = set_quantity(diameter, "mm")
    L = set_quantity(length, "mm")
    _validate_positive(mass=m, diameter=D, length=L)
    R = D / 2.0
    J_y = _sum_inertia([(0.5, m, R)])                          # 1/2·mR²
    J_x = _sum_inertia([(0.25, m, R), (1.0 / 12.0, m, L)])     # m(3R²+L²)/12
    return {
        "J_x": J_x, "J_y": J_y, "J_z": J_x,
        "volume": (math.pi * R**2 * L).to("m**3"),
    }


def rectangular_prism(mass, a, b, h):
    """长方体：J_x = m(b²+h²)/12 = (1/12)mb² + (1/12)mh²"""
    m = set_quantity(mass, "kg")
    a_q = set_quantity(a, "mm")
    b_q = set_quantity(b, "mm")
    h_q = set_quantity(h, "mm")
    _validate_positive(mass=m, a=a_q, b=b_q, h=h_q)
    k12 = 1.0 / 12.0
    J_x = _sum_inertia([(k12, m, b_q), (k12, m, h_q)])
    J_y = _sum_inertia([(k12, m, a_q), (k12, m, b_q)])
    J_z = _sum_inertia([(k12, m, a_q), (k12, m, h_q)])
    return {"J_x": J_x, "J_y": J_y, "J_z": J_z,
            "volume": (a_q * b_q * h_q).to("m**3")}


def inclined_rod(mass, length, alpha):
    """倾斜杆：J_c = (1/12)·m·(l·sinα)² —— 有效长度 = l·sinα"""
    m = set_quantity(mass, "kg")
    l = set_quantity(length, "mm")
    alpha_rad = math.radians(alpha)
    L_eff = (l * math.sin(alpha_rad)).to("m")
    J_c = _sum_inertia([(1.0 / 12.0, m, L_eff)])
    return {"J_c": J_c}


# ==================== 验证：与现有库函数结果一致 ====================

def verify():
    print("===== 通用方案示例 vs 现有 mechcalc 函数 =====\n")
    checks = [
        ("圆球", sphere(10, 100), mc.sphere(10, 100), "J_x"),
        ("圆板绕直径", circular_plate(10, 100), mc.circular_plate(10, 100), "J_x"),
        ("圆板绕中心", circular_plate(10, 100), mc.circular_plate(10, 100), "J_rho_O"),
        ("圆柱绕对称轴", cylinder(10, 100, 200), mc.cylinder(10, 100, 200), "J_y"),
        ("圆柱绕直径", cylinder(10, 100, 200), mc.cylinder(10, 100, 200), "J_x"),
        ("长方体绕x", rectangular_prism(10, 100, 200, 300), mc.rectangular_prism(10, 100, 200, 300), "J_x"),
        ("倾斜杆J_c", inclined_rod(10, 300, 60), mc.inclined_rod(10, 300, 60), "J_c"),
    ]
    for name, new, old, key in checks:
        v_new = to_mag(new[key], "kg*m**2")
        v_old = to_mag(old[key], "kg*m**2")
        ok = "✓" if abs(v_new - v_old) < 1e-9 else "✗"
        print(f"  {name:<10} 通用={v_new:.6f}  现有={v_old:.6f}  {ok}")

    # 错误验证演示：负质量被拦截
    print("\n===== 参数验证演示 =====")
    try:
        sphere(-10, 100)
        print("  负质量: 未拦截 ✗")
    except ValueError as e:
        print(f"  负质量: 拦截 ✓ ({e})")


if __name__ == "__main__":
    verify()
