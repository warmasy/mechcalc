# 快速开始

## 安装

```bash
cd mechcalc
pip install -e .
```

依赖：`pint >= 0.25`、`numpy >= 1.26`。

## 两种返回模式

### 默认：返回原始 pint Quantity（链式计算）

```python
import mechcalc as mc

J = mc.solid_cylinder(10, 100)     # <Quantity(0.0125, 'kg*m**2')>
omega = mc.angular_velocity(1400)  # rpm -> rad/s

# 直接参与后续计算，单位自动推导
T = 0.5 * J * omega ** 2
print(T.to('J'))                   # 134.3 J
```

返回值是"活的" pint 对象：`.magnitude` 取数值、`.units` 取单位、`.to('J')` 换算。

### to_result：包装成带参数记录的报告

```python
r = mc.to_result(mc.push_force, 0.4, 32)

r.F        # {'value': 273.4, 'unit': 'N'}
r.params   # {'P': {'value': 0.4, 'unit': 'MPa'}, ...}
r.to_api() # 可直接 JSON 序列化（FastAPI 友好）
```

**任何计算函数都可以这样包装**，函数本身不需要写任何装饰代码。

## 双模式输入

所有函数同时接受两种参数形式：

```python
mc.gravity(10)                  # 裸数字：按文档默认单位（kg）解释
mc.gravity(mc.Q_(10000, 'g'))   # Quantity：克自动换算成千克
# 结果完全相同：98.0665 N
```

每个参数的默认单位写在函数文档里（如 `:param mass: 质量(kg)`）。

## 批量计算

`calc_batch` 一次算多组工况，出错的那组单独标记不影响整体：

```python
cases = [
    {'P': 0.4, 'D': 32},
    {'P': 0.6, 'D': 50},
]
results = mc.calc_batch(mc.push_force, cases)
```

部分向量化函数还直接支持数组批量：

```python
I = mc.solid_cylinder_tensor(10, 100, 200)
Js = mc.inertia_about_axis(I, [[1, 0, 0], [0, 1, 0], [0, 0, 1]])  # (N,3)
```
