# 高级惯量 API 设计（待评审）

> 状态：**设计稿，未实现**。评审通过后再落地到 `mechcalc/inertia/tensor.py`。
> 目标：把"惯量张量 × numpy 矩阵运算"的三个高频高级运算封装成正式 API。

## 背景

现有 API 已提供惯量张量基础积木：

- `solid_cylinder_tensor` / `hollow_cylinder_tensor` → 3×3 惯量张量（质心系）
- `parallel_axis_tensor` → 平行移轴（张量形式）
- `inertia_about_axis` → 任意轴等效惯量（支持批量 (N,3)）
- `eig` / `trace` / `det`（`core.units_linalg`）→ 张量分解工具

但以下三个高频场景目前要"手工用 numpy 拼"，应封装为正式函数：

1. **张量旋转**：物体姿态变了，惯量张量如何变换（`I′ = R·I·Rᵀ`）
2. **主惯量分解**：哪根轴转动最省力、主轴方向（`eig`）
3. **组合体惯量**：转盘 + 偏心工件等多部件合成（平行移轴 + 矩阵相加）

---

## API 1：`rotate_tensor` — 惯量张量的坐标变换

### 签名

```python
def rotate_tensor(
    inertia_tensor: Quantity | np.ndarray,
    rotation: np.ndarray | list | tuple,
) -> Quantity:
    """惯量张量随姿态的变换。

    I′ = R · I · Rᵀ

    :param inertia_tensor: 惯量张量(kg·m²)，裸数组按 kg·m² 解释
    :param rotation: 3×3 旋转矩阵（rot_x/rot_y/rot_z 返回值，或任意正交矩阵）
    :return: 变换后的惯量张量(kg·m²)
    """
```

### 公式与单位

- 公式：**I′ = R·I·Rᵀ**（R 为基变换矩阵，语义见下）
- 单位：输入 kg·m² → 输出 kg·m²（旋转矩阵无量纲）
- 输出数值上仍为对称矩阵

### 旋转语义约定（重要决策点）

采用与 `basic.motion3d.gravity_force(rotation=...)` **一致的语义**：
`rotation` 是把向量从**世界系变换到本体系**的矩阵（`v_body = R @ v_world`），
因此 `R·I·Rᵀ` 给出"同一物体按 R 摆放后，在世界系中的惯量张量"。

验证示例（圆柱，z 为对称轴，Ixx=Iyy=0.0396, Izz=0.0125）：

| 操作 | 结果 |
|---|---|
| 绕 z 转任意角 | 张量不变（对称轴） |
| 绕 y 转 90°（圆柱倒放） | Ixx ↔ Izz（0.0125 ↔ 0.0396） |

### 校验

1. `inertia_tensor` 形状 (3,3)
2. `rotation` 形状 (3,3)
3. **正交性检查**：`R·Rᵀ ≈ E`（容差 1e-6），不满足则 `raise ValueError("rotation 必须是正交旋转矩阵")`
4. 输出对称性：数值误差容忍（不做硬校验）

---

## API 2：`principal_inertia` — 主惯量分解

### 签名

```python
def principal_inertia(inertia_tensor: Quantity | np.ndarray) -> dict:
    """对称惯量张量的主惯量分解。

    I = V · diag(J1, J2, J3) · Vᵀ

    :param inertia_tensor: 惯量张量(kg·m²)，裸数组按 kg·m² 解释
    :return: {
        'J_principal': 主惯量数组(kg·m²)，升序排列
        'axes': 主轴方向矩阵(3×3)，列为对应主轴（无量纲）
        'J_max': 最大主惯量(kg·m²)
        'J_min': 最小主惯量(kg·m²)
    }
    """
```

### 公式与单位

- 公式：`eig(I)` → 特征值 Λ（主惯量，单位 kg·m²）+ 特征向量 V（主轴，无量纲）
- 实现直接复用 `mechcalc.core.units_linalg.eig`（已支持带单位）
- 特征值**升序排列**，主轴矩阵列向量与之对应

### 校验

1. 形状 (3,3)
2. **对称性检查**：`|I − Iᵀ|` 超过容差（1e-9）则 `raise ValueError("惯量张量必须是对称矩阵")`
   （对非对称输入做 eig 会给出复数特征值，物理无意义，提前拦截）
3. 退化说明（文档注明）：对称圆柱/球存在**相等主惯量**，此时主轴方向不唯一，`eig` 返回的是某一组可行解

### 返回结构（与 Result 兼容）

返回 dict，其中 Quantity 值可被 `to_result` / `_format_results` 直接格式化；
主轴矩阵是裸 ndarray（无量纲），序列化为嵌套 list。

---

## API 3：`composite_inertia` — 组合体惯量合成

### 签名

```python
def composite_inertia(parts: list[tuple]) -> Quantity:
    """多部件组合体的总惯量张量（相对公共参考点）。

    I_total = Σᵢ [ Iᵢ + mᵢ·(rᵢ·rᵢ·E − rᵢ·rᵢᵀ) ]

    :param parts: 部件列表，每项 (inertia_tensor, mass, offset)
        inertia_tensor: 部件**质心系**惯量张量(kg·m²)
        mass: 部件质量(kg)
        offset: 部件质心相对公共参考点的位移向量 [x, y, z](m)
    :return: 组合体总惯量张量(kg·m²，相对同一参考点)
    """
```

### 公式与单位

- 公式：对每个部件做**平行移轴**（等价于 `parallel_axis_tensor`），再矩阵求和
- 单位：kg·m²
- `parts` 支持裸数组张量或 Quantity 张量混用

### 校验

1. `parts` 非空
2. 每项：张量 (3,3)、质量 > 0、offset 为三维向量
3. 语义约束（文档注明）：所有 offset 必须相对**同一参考点**；
   若参考点是组合体质心，需先自行用各部件质心坐标计算（进阶版见待决策点）

### 示例（与手算对照）

转盘（m=20kg, D=300mm, L=30mm）+ 偏心工件（m=2kg, D=100mm, L=50mm, 偏心 200mm）：

```
I_disk.Izz = 0.225 kg·m²
I_part.Izz = 0.0025 + 2×0.2² = 0.0825 kg·m²
I_total.Izz = 0.3075 kg·m²
```

---

## 测试计划（落地时写入 `tests/test_tensor.py`）

| 函数 | 用例 |
|---|---|
| `rotate_tensor` | ① 绕对称轴(z)旋转不变 ② 绕 y 转 90° Ixx↔Izz ③ 输出单位 kg·m² ④ 非正交矩阵抛 ValueError |
| `principal_inertia` | ① 圆柱主惯量=[Ixx,Ixx,Izz] ② 球三主惯量相等 ③ 主轴正交 V·Vᵀ=E ④ 非对称输入抛 ValueError ⑤ 单位 kg·m² |
| `composite_inertia` | ① 单部件零偏移=原张量 ② 转盘+偏心工件手算对照 ③ 与 parallel_axis_tensor 互锁 ④ 空列表/负质量抛 ValueError |

---

## 待决策点（评审时请确认）

1. **`rotate_tensor` 的旋转语义**：采用"世界系→本体系"（与 `gravity_force` 一致）还是主动旋转？文档已默认前者，请确认。
2. **`composite_inertia` 的参考点**：
   - 方案 A（本稿）：用户直接给 offset（相对任意参考点），最简单
   - 方案 B（进阶）：再提供 `composite_centroid(parts)` 自动算组合体质心，部件传**绝对坐标**而非 offset
   - 建议：先做 A，B 作为后续扩展
3. **parts 参数形式**：元组 `(tensor, mass, offset)` vs 命名 dict `{'tensor':…, 'mass':…, 'offset':…}`（可读性更好，前端友好）
4. **返回结构**：`principal_inertia` 返回 dict（含 J_max/J_min 快捷键）还是仅 `(J, axes)` 元组？
5. 落地后是否同步到 `mechcalc-api` 项目并补充对应路由？

---

## 相关文件

- 实现位置：`src/mechcalc/inertia/tensor.py`（新增三个函数，复用 `_as_tensor`）
- 依赖：`core/units_linalg.eig`（已实现）
- 导出：`inertia/__init__.py` + 顶层 `mechcalc/__init__.py` + `__all__`
- 文档：`docs/theory/inertia.md` 补充高级运算章节
