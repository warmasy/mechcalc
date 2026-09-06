# mechcalc 机械工程计算库

基于 [pint](https://pint.readthedocs.io/)（单位系统）+ [numpy](https://numpy.org/)（向量化）的 Python 机械工程计算库。

覆盖：**惯量计算（标量 + 张量）、三维刚体运动、气缸、电机需求参数**，公式基于《机械设计手册》。

## 特性

- **自带单位**：所有计算基于 pint，输入输出带单位，自动换算，杜绝单位错误
- **双模式输入**：裸数值（按文档默认单位，如 mm/MPa/rpm）或 pint Quantity 随意传
- **向量化**：惯量张量、任意轴等效惯量、旋转刚体运动用 numpy 矩阵表达，支持批量轴 `(N, 3)`
- **API 友好**：`to_result()` 一行把任何计算包装成可 JSON 序列化的报告（含参数记录）
- **零依赖魔法**：`to_result` 通过签名内省 + docstring 解析自动提取参数单位，函数无需装饰器

## 安装

```bash
pip install -e .
# 开发/文档依赖（可选）
pip install -e ".[dev]"
pip install -e ".[docs]"
```

要求 Python ≥ 3.11。

## 一分钟上手

```python
import mechcalc as mc

# 标量计算：实心圆柱惯量（D=100mm, m=10kg -> 0.0125 kg·m²）
J = mc.solid_cylinder(mass=10, outer_diameter=100)

# 向量计算：任意方向轴的等效惯量
I = mc.solid_cylinder_tensor(10, 100, 200)
print(mc.inertia_about_axis(I, [0, 0, 1]))

# 需要带参数记录的报告时（可 JSON 序列化）
r = mc.to_result(mc.motor_calc, load_torque=5.0, load_speed=1400)
print(r.required_power)   # {'value': 879.6, 'unit': 'W'}
```

## 模块结构

| 模块 | 内容 |
|------|------|
| `mc.core` | 单位系统（`Q_`/`set_quantity`/`to_mag`）、3D 向量矩阵工具（`as_vec3`/`skew`/`rot_x/y/z`） |
| `mc.basic` | 运动学、动力学、旋转运动、能量功率、质量体积、三维运动（27 个函数） |
| `mc.inertia` | 惯量：4 种工程机构等效 + 9 种细杆 + 11 种平面板 + 16 种立体 + 7 种薄壳 + 4 个张量函数 |
| `mc.pneumatic` | 气缸推力/拉力/耗气量/综合选型（`STD_BORES` 标准缸径表） |
| `mc.electric` | 电机需求参数（扭矩/转速/功率，含安全系数） |
| `mc.utils` | `Result`（dict + 属性双接口）、`to_result`、`calc_batch` 批量计算 |

完整 API 见 [API 参考文档](https://mechcalc.readthedocs.io/)。

## 设计约定

1. **单位只在边界结算，内部全 SI**：`as_vec3`/`as_vecs` 是唯一允许剥单位的入口
2. **角度**：内部一律弧度；输入参数按文档声明（机械图纸场景用 deg，可传 Quantity）
3. **向量**：单个形状 `(3,)`，批量 `(N, 3)`；右手坐标系，z 轴向上
4. **返回模式**：函数默认返回原始 pint Quantity 或 dict（链式计算）；`to_result` 现场包装为 Result

## 测试与代码质量

```bash
# 运行测试
pytest tests -q

# 代码检查与格式化
ruff check src tests
ruff format src tests
```

- 测试策略：标量函数与张量/向量函数**互锁验证**（如张量 Izz 必须等于标量函数），含退化极限、单位扰动、批量轴用例
- 全部公开函数带类型注解（`QuantityLike` = `float | int | Quantity`），含 `py.typed`

## 文档

```bash
pip install -e ".[docs]"
mkdocs serve
```

## License

MIT
