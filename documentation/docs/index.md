---
title: mechcalc 机械工程计算库
hide:
  - toc
  - navigation
  - feedback
---

<div class="stat-grid">
  <div class="stat-card">
    <span class="stat-value">100+</span>
    <span class="stat-label">计算函数</span>
  </div>
  <div class="stat-card">
    <span class="stat-value">56</span>
    <span class="stat-label">惯量形状</span>
  </div>
  <div class="stat-card">
    <span class="stat-value">163</span>
    <span class="stat-label">单元测试</span>
  </div>
  <div class="stat-card">
    <span class="stat-value">4</span>
    <span class="stat-label">计算模块</span>
  </div>
</div>

## 特性

<div class="grid cards" markdown>

-   :material-weight-kilogram:{ .lg .middle } **自带单位，杜绝错误**

    ---

    所有计算基于 pint，输入输出带单位、自动换算。
    裸数值（按文档默认单位）或 Quantity 随意传。

-   :material-matrix:{ .lg .middle } **惯量张量，一行拿到**

    ---

    每个惯量函数返回完整 3×3 惯性张量，
    配合 `inertia_about_axis` 处理任意姿态。

-   :material-function-variant:{ .lg .middle } **通用计算核心**

    ---

    `_sum_inertia` 用「系数 × m × 长度²」统一表达公式，
    `inertia_result` 一行组装返回结构，代码精简清晰。

-   :material-engine-outline:{ .lg .middle } **选型闭环**

    ---

    气缸综合选型（标准缸径表）、电机/伺服选型（内置型号库 + 惯量比校验）。

-   :material-api:{ .lg .middle } **API 友好**

    ---

    `to_result()` 一行把任何计算包装成可 JSON 序列化的报告，
    `calc_batch()` 批量计算多组工况。

-   :material-database-sync:{ .lg .middle } **FastAPI 就绪**

    ---

    与 FastAPI 服务（mechcalc-api）深度集成，路由自动生成，
    计算历史自动入库。

</div>

## 一分钟上手

```python
import mechcalc as mc

# 惯量：返回各轴惯量 + 完整 3×3 惯性张量
r = mc.cylinder(mass=10, diameter=100, length=200)
print(r['J_y'])        # 0.0125 kg·m²（绕对称轴）
print(r['tensor'])     # 完整 3×3 惯性张量

# 任意姿态、任意轴的惯量
I = mc.solid_cylinder_tensor(10, 100, 200)
print(mc.inertia_about_axis(I, [1, 1, 1]))   # 绕空间对角线

# 电机选型（内置型号库）
print(mc.motor_select(load_torque=5.0, load_speed=1400)['selected_model'])
```

## 安装

```bash
pip install -e .
# 文档构建依赖（可选）
pip install -e ".[docs]"
```

要求 Python ≥ 3.11。

## 文档导航

- **[快速开始](guide/quickstart.md)**：安装、调用模式、批量计算
- **[单位系统](guide/units.md)**：双模式输入、`to_result` 包装规则
- **[计算原理](theory/inertia.md)**：公式推导、配图讲解
- **[惯性张量入门教程](theory/inertia_tensor_guide.md)**：从零理解惯量张量与姿态变换
- **[API 参考](api/inertia.md)**：全部函数的参数与返回值
