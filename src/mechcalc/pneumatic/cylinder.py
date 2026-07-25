"""气缸计算模块

提供气缸推力、拉力、耗气量计算及综合选型功能。

标准缸径表:
  STD_BORES = [6, 8, 10, 12, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 320]

用法:
    raw = push_force(0.4, 32)
    print(raw['F'])            # 273.4 N

    # 需要 Result（带参数记录）时：
    result = to_result(push_force, 0.4, 32)
    print(result.F)            # {'value': 273.4, 'unit': 'N'}
"""

import math
from ..core.units import mm, ensure_quantity
from ..core.units import to_mag

# 标准缸径表（单位: mm）
STD_BORES = [6, 8, 10, 12, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 320]

# 活塞杆直径估算系数（缸径的倍数）及最小直径
ROD_DIA_RATIO = 0.35
ROD_DIA_MIN = 2.0


def push_force(P, D, d=None, efficiency=0.85):
    """
    气缸推力计算。

    :param P: 工作压力(MPa)
    :param D: 气缸缸径(mm)
    :param d: 活塞杆直径(mm)，可选
    :param efficiency: 机械效率(None)，默认 0.85
    :return: {'F': 推力(N), 'A': 面积(mm²)}
    """
    P = ensure_quantity(P, 'MPa')
    D = ensure_quantity(D, 'mm')
    eta = float(efficiency)

    A = math.pi * (D / 2) ** 2
    F = (P * A * eta).to('N')   # MPa·mm² 数值上等于 N，但单位需显式换算

    return {'F': F, 'A': A}


def pull_force(P, D, d=None, efficiency=0.85):
    """
    气缸拉力计算。

    :param P: 工作压力(MPa)
    :param D: 气缸缸径(mm)
    :param d: 活塞杆直径(mm)，可选
    :param efficiency: 机械效率(None)，默认 0.85
    :return: {'F': 拉力(N), 'A': 面积(mm²)}
    """
    P = ensure_quantity(P, 'MPa')
    D = ensure_quantity(D, 'mm')
    if d is None:
        d = mm(max(round(float(D.magnitude) * ROD_DIA_RATIO), ROD_DIA_MIN))
    else:
        d = ensure_quantity(d, 'mm')
    eta = float(efficiency)

    A = math.pi * ((D / 2) ** 2 - (d / 2) ** 2)
    F = (P * A * eta).to('N')   # MPa·mm² 数值上等于 N，但单位需显式换算

    return {'F': F, 'A': A}


def air_consumption(D, L, t, P, atm=0.1013):
    """
    气缸耗气量计算。

    :param D: 气缸缸径(mm)
    :param L: 行程(mm)
    :param t: 单循环时间(s)
    :param P: 工作压力(MPa)
    :param atm: 大气压(MPa)，默认 0.1013
    :return: {'air_consumption': 耗气量(L/min), 'volume_per_stroke': 单行程容积(L)}
    """
    D = ensure_quantity(D, 'mm')
    L = ensure_quantity(L, 'mm')
    t_val = float(t)
    P = ensure_quantity(P, 'MPa')
    atm_q = ensure_quantity(atm, 'MPa')

    A = math.pi * (D / 2) ** 2
    vol_per_stroke = (A * L).to('L')

    P_abs = P + atm_q
    ratio = P_abs / atm_q
    vol_std = vol_per_stroke * ratio

    cycles_per_min = 60.0 / t_val
    Q = vol_std * ensure_quantity(cycles_per_min, '1/min')

    return {
        'air_consumption': Q.to('L/min'),
        'volume_per_stroke': vol_std.to('L'),
    }


def cylinder_select(F, P, L, eta=0.85, S=1.3):
    """
    气缸综合选型。

    :param F: 需求推力(N)
    :param P: 工作压力(MPa)
    :param L: 行程(mm)
    :param eta: 机械效率(None)，默认 0.85
    :param S: 安全系数(None)，默认 1.3
    :return: 选型结果
    """
    F = ensure_quantity(F, 'N')
    P = ensure_quantity(P, 'MPa')
    L = ensure_quantity(L, 'mm')
    eta = float(eta)
    S = float(S)

    F_N = to_mag(F, 'N')
    P_MPa = to_mag(P, 'MPa')
    D_theory_mm = math.sqrt(4 * F_N * S / (math.pi * P_MPa * eta))
    D_theory = ensure_quantity(D_theory_mm, 'mm')

    selected_bore = None
    for bore in STD_BORES:
        if bore >= D_theory_mm:
            selected_bore = bore
            break
    if selected_bore is None:
        selected_bore = STD_BORES[-1]

    raw_push = push_force(P, selected_bore, efficiency=eta)
    F_actual = raw_push['F']

    d_rod = mm(max(round(selected_bore * ROD_DIA_RATIO), ROD_DIA_MIN))
    raw_pull = pull_force(P, selected_bore, d=d_rod, efficiency=eta)
    F_pull = raw_pull['F']

    return {
        'theoretical_bore': D_theory.to('mm'),
        'selected_bore': ensure_quantity(selected_bore, 'mm'),
        'push_force': F_actual.to('N'),
        'pull_force': F_pull.to('N'),
        'rod_diameter': d_rod.to('mm'),
    }
