# mechcalc 机械工程计算库

基于 pint 的机械工程计算库，覆盖**惯量计算、三维运动、气动、电机需求计算**。

## 特性

- **自带单位**：所有计算基于 pint，输入输出带单位，自动换算，杜绝单位错误
- **双模式输入**：裸数值（按文档默认单位）或 pint Quantity 随意传
- **向量化**：三维问题（惯量张量、任意轴等效惯量、旋转刚体运动）用 numpy 矩阵表达
- **API 友好**：`to_result()` 一行把任何计算包装成可 JSON 序列化的报告

## 安装

```bash
pip install -e .
# 文档构建依赖（可选）
pip install -e ".[docs]"
```

## 一分钟上手

```python
import mechcalc as mc

# 标量计算：实心圆柱惯量
J = mc.solid_cylinder(mass=10, outer_diameter=100)
print(J.to('kg*m**2'))          # 0.0125 kg·m²

# 向量计算：任意方向轴的等效惯量
I = mc.solid_cylinder_tensor(10, 100, 200)
print(mc.inertia_about_axis(I, [0, 0, 1]))

# 需要带参数记录的报告时
r = mc.to_result(mc.motor_calc, load_torque=5.0, load_speed=1400)
print(r.required_power)         # {'value': 879.6, 'unit': 'W'}
```

## 文档导航

- **[快速开始](guide/quickstart.md)**：安装、调用模式、批量计算
- **[单位系统](guide/units.md)**：双模式输入、`to_result` 包装规则
- **[计算原理](theory/inertia.md)**：公式推导、配图讲解
- **[API 参考](api/inertia.md)**：全部函数的参数与返回值
