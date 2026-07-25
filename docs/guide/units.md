# 单位系统

单位处理是 mechcalc 的核心设计：**单位只在边界结算，内部永远 SI**。

## 三种角色

| 场景 | 工具 | 例子 |
|------|------|------|
| 收参（函数入口，两种输入通吃） | `ensure_quantity(v, unit)` | `ensure_quantity(mass, 'kg')` |
| 造量（构造返回值/中间量） | `Q_(值, '单位')` 或快捷函数 | `Q_(J, 'kg*m**2')`、`mc.kg(10)` |
| 去向量化（剥成 SI 数组） | `as_vec3` / `as_vecs` | `as_vec3(pos, 'm')` |

## 单位快捷函数

常用单位有快捷构造器（就是 `Q_(v, '单位')` 的缩写）：

```python
mc.kg(10)      # ≡ mc.Q_(10, 'kg')
mc.mm(100)     # ≡ mc.Q_(100, 'mm')
mc.MPa(0.4)    # ≡ mc.Q_(0.4, 'MPa')
```

完整列表：`kg, mm, m, s, N, Nm, MPa, rpm, kg_m2, kW, W`。

## 单位提取

```python
from mechcalc import to_mag, to_unit

to_mag(mc.Q_(100, 'mm'), 'm')   # 0.1（先换算再取数值）
to_unit(mc.Q_(100, 'mm'))       # 'mm'
```

## 设计约定（扩展开发必读）

1. **内部 SI**：函数内部只用 kg/m/s/rad，换算系数全部集中在入口/出口
2. **角度**：内部一律弧度；输入参数按文档声明（机械图纸场景用 deg）
3. **向量**：单个向量形状 `(3,)`，批量 `(N, 3)`；右手坐标系，z 轴向上
4. **禁止**：内部代码直接 `np.asarray(Quantity)`（会静默丢单位且不换算），一律走 `as_vec3` / `as_vecs`

## 常见坑

!!! warning "pint 的常量陷阱"
    `ureg.g` 是**克**、`ureg.h` 是**小时**、`ureg.G` 是**高斯**——pint 把它们解析成单位而不是物理常数。物理常数要用全名 `ureg.standard_gravity` 等。完整常量数值见项目根目录《物理常量参考.md》。
