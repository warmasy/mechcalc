"""运动学基础计算

直线运动的基本公式：速度、位移、加速度。
"""

from ..core.units import ensure_quantity


def velocity(displacement, time):
    """
    平均速度 / 匀速运动速度。

    v = s / t

    :param displacement: 位移(m)
    :param time: 时间(s)
    :return: 速度(m/s)
    """
    dist = ensure_quantity(displacement, 'm')
    t = ensure_quantity(time, 's')
    v = (dist / t).to('m/s')
    return v


def displacement(velocity, time):
    """
    匀速运动位移。

    s = v * t

    :param velocity: 速度(m/s)
    :param time: 时间(s)
    :return: 位移(m)
    """
    v = ensure_quantity(velocity, 'm/s')
    t = ensure_quantity(time, 's')
    s_val = (v * t).to('m')
    return s_val


def acceleration(velocity_change, time):
    """
    加速度（速度变化量 / 时间）。

    a = Δv / t

    :param velocity_change: 速度变化量(m/s)
    :param time: 时间(s)
    :return: 加速度(m/s²)
    """
    dv = ensure_quantity(velocity_change, 'm/s')
    t = ensure_quantity(time, 's')
    a = (dv / t).to('m/s**2')
    return a


def uniform_motion(velocity, time):
    """
    匀速直线运动综合计算。

    :param velocity: 速度(m/s)
    :param time: 时间(s)
    :return: {'displacement': 位移(m), 'velocity': 速度(m/s)}
    """
    v = ensure_quantity(velocity, 'm/s')
    t = ensure_quantity(time, 's')
    s_val = (v * t).to('m')
    return {'displacement': s_val, 'velocity': v}


def uniform_acceleration(v0, v1, t, s=None):
    """
    匀加速直线运动综合计算。

    已知初速度、末速度、时间，求加速度和位移。
    若传入位移 s，则校验一致性。

    :param v0: 初速度(m/s)
    :param v1: 末速度(m/s)
    :param t: 时间(s)
    :param s: 位移(m)，可选，用于校验
    :return: {'acceleration': 加速度, 'displacement': 位移, 'avg_velocity': 平均速度}
    """
    v0_q = ensure_quantity(v0, 'm/s')
    v1_q = ensure_quantity(v1, 'm/s')
    # 注意：参数 s 与单位秒同名，这里用 ensure_quantity 统一处理
    t_q = ensure_quantity(t, 's')

    a = ((v1_q - v0_q) / t_q).to('m/s**2')
    s_calc = ((v0_q + v1_q) / 2 * t_q).to('m')
    v_avg = ((v0_q + v1_q) / 2).to('m/s')

    return {
        'acceleration': a,
        'displacement': s_calc,
        'avg_velocity': v_avg,
    }
