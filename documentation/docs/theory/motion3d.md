# 三维运动

一维标量公式解决不了的三维问题：方向在变化、绕任意轴旋转、姿态变换。统一约定：**右手坐标系，z 轴向上，向量形状 (3,)，批量 (N, 3)**。

## 旋转刚体上一点的速度

$$
\mathbf{v} = \boldsymbol{\omega} \times \mathbf{r}
$$

代码里叉乘写成反对称矩阵乘：$\boldsymbol{\omega} \times \mathbf{r} = [\boldsymbol{\omega}]_\times \, \mathbf{r}$

```python
mc.point_velocity([0, 0, 10], [0.1, 0, 0])
# <Quantity([0., 1., 0.], 'm/s')>   ω=(0,0,10), r=(0.1,0,0) → v=(0,1,0)
```

## 向心加速度

$$
\mathbf{a} = \boldsymbol{\omega} \times (\boldsymbol{\omega} \times \mathbf{r})
$$

```python
mc.centripetal_acceleration([0, 0, 10], [0.1, 0, 0])
# <Quantity([-10., 0., 0.], 'm/s²')>   指向轴心
```

## 转动动能与角动量

$$
T = \frac{1}{2}\, \boldsymbol{\omega}^{\mathsf{T}} \mathbf{I}\, \boldsymbol{\omega}
\qquad
\mathbf{L} = \mathbf{I}\, \boldsymbol{\omega}
$$

```python
I = mc.solid_cylinder_tensor(10, 100, 200)
mc.rotational_kinetic_energy(I, [0, 0, 10])   # 0.625 J
mc.angular_momentum(I, [0, 0, 10])
```

## 重力向量

世界系（z 轴向上）中重力 $\mathbf{F} = [0,\, 0,\, -mg]$；本体系转过角度后，用旋转矩阵变换分量：

```python
import math
mc.gravity_force(10)                              # [0, 0, -98.07] N
mc.gravity_force(10, rotation=mc.rot_x(math.pi / 2))   # 绕 x 转 90° 后的本体系分量
```

## 旋转矩阵

`rot_x / rot_y / rot_z(angle)` 生成 $3\times3$ 旋转矩阵，语义 $\mathbf{v}_{new} = \mathbf{R}\,\mathbf{v}_{old}$：

$$
\mathbf{R}_z(\theta) = \begin{bmatrix} \cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1 \end{bmatrix}
$$

angle 传裸数字按弧度，传 `Q_(90, 'deg')` 自动换算。

!!! tip "什么时候需要这些"
    直线运动、固定轴旋转用 `basic/` 里的标量函数即可；只有**方向在三维空间中变化**（斜置机构、摆动、机械臂）才需要本页的三维形式。
