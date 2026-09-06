"""快速试算脚本（非测试，手工运行示例）

    python examples/quick_try.py
"""

import mechcalc as mc
from mechcalc import to_mag

# 实心圆柱：返回 dict（J_x/J_y/J_z + 完整 3×3 惯性张量）
r = mc.cylinder(10, 500, 100)  # m=10kg, D=500mm, L=100mm
print("J_y (绕对称轴) =", to_mag(r["J_y"], "kg*m**2"), "kg*m^2")
print("完整惯性张量 =")
print(r["tensor"].magnitude)

# Result 模式（带参数记录，可 JSON 序列化）
res = mc.to_result(mc.cylinder, 10, 500, 100)
print("Result mode J_y:", res.J_y["value"], "kg*m^2")
print("params:", res.params)
