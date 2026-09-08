# 气动计算

## 气缸推力

工作压力 $P$（MPa）、缸径 $D$（mm）、效率 $\eta$：

$$
F = P \cdot A \cdot \eta, \qquad A = \frac{\pi D^2}{4}
$$

单位巧合：$1\ \text{MPa} \cdot \text{mm}^2 = 1\ \text{N}$，数值上直接相等。

```python
raw = mc.push_force(0.4, 32)
raw['F']   # 273.4 N   （0.4 MPa、32mm 缸径、默认 η=0.85）
raw['A']   # 804.2 mm²
```

**拉力**（有杆腔，需扣掉活塞杆面积）：

$$
F_{pull} = P \cdot \frac{\pi(D^2 - d^2)}{4} \cdot \eta
$$

```python
mc.pull_force(0.4, 32, d=12)
```

## 缸径选型

已知所需推力 $F$、气压 $P$、负载率 $\eta$、安全系数 $S$，反算所需缸径：

$$
D = \sqrt{\frac{4 F S}{\pi P \eta}}
$$

```python
r = mc.cylinder_select(200, 0.4, 100)   # 推力200N、气压0.4MPa、杆径100mm 用途
# 返回所需缸径和推荐标准缸径
```

## 耗气量

单循环时间 $t$、行程 $L$，按绝压比折算到大气状态：

$$
Q = \frac{2 A L}{t} \cdot \frac{P + P_{atm}}{P_{atm}} \times 60
$$

系数 2 为双作用缸一个循环两行程；$P_{atm}$ 默认 0.1013 MPa（可传参）。

```python
mc.air_consumption(32, 100, 2, 0.5)
# {'air_consumption': ..., 'volume_per_stroke': ...}
```
