"""
动力学计算模块
计算气体力、惯性力、合力、连杆力、侧向力、切向力、径向力
"""

import numpy as np
from parameters import (
    RECIPROCATING_MASS, PISTON_AREA, LAMBDA, ROD_LENGTH,
    CRANK_ANGLES, ANGULAR_VELOCITY, CRANK_RADIUS, PISTON_OFFSET
)
from kinematics import calculate_piston_acceleration


def get_gas_pressure(phi_deg, pressure_data):
    """
    获取指定曲轴转角的气体压力
    
    参数:
        phi_deg: 曲轴转角 [度]
        pressure_data: 压力数据字典
    
    返回:
        气体压力 [Pa]
    
    异常:
        KeyError: 当角度不在数据集中且无合理默认值时
    """
    if phi_deg in pressure_data:
        return pressure_data[phi_deg]
    
    # 如果角度不存在，尝试找最近的
    if pressure_data:
        nearest_angle = min(pressure_data.keys(), key=lambda x: abs(x - phi_deg))
        print(f"警告: 角度 {phi_deg}° 不在数据中，使用最近的角度 {nearest_angle}°")
        return pressure_data[nearest_angle]
    
    raise KeyError(f"压力数据为空，无法获取角度 {phi_deg}° 的压力值")


def calculate_inertia_force(phi_deg):
    """
    计算往复惯性力
    
    公式: Fj = -mj × a
    
    参数:
        phi_deg: 曲轴转角 [度]
    
    返回:
        往复惯性力 [N]，与加速度方向相反
    """
    acceleration = calculate_piston_acceleration(phi_deg)
    Fj = -RECIPROCATING_MASS * acceleration
    return Fj


def calculate_gas_force(phi_deg, pressure_data):
    """
    计算气体作用力
    
    公式: Fg = pg × A
    
    参数:
        phi_deg: 曲轴转角 [度]
        pressure_data: 压力数据字典
    
    返回:
        气体作用力 [N]，向下为正
    """
    # 表压（减去大气压）
    gas_pressure = get_gas_pressure(phi_deg, pressure_data) - 0.101325e6
    Fg = gas_pressure * PISTON_AREA
    return Fg


def calculate_resultant_force(phi_deg, pressure_data):
    """
    计算沿气缸中心线的合力
    
    公式: F = Fg + Fj
    
    参数:
        phi_deg: 曲轴转角 [度]
        pressure_data: 压力数据字典
    
    返回:
        合力 [N]，向下为正
    """
    Fg = calculate_gas_force(phi_deg, pressure_data)
    Fj = calculate_inertia_force(phi_deg)
    return Fg + Fj


def calculate_rod_angle(phi_deg):
    """
    计算连杆摆角
    
    公式: β = arcsin((R·sinφ + e) / L)
    
    参数:
        phi_deg: 曲轴转角 [度]
    
    返回:
        连杆摆角 [弧度]
    """
    phi = np.radians(phi_deg)
    
    # 带活塞偏移的公式
    sin_beta = (CRANK_RADIUS * np.sin(phi) + PISTON_OFFSET) / ROD_LENGTH
    sin_beta = np.clip(sin_beta, -1.0, 1.0)
    
    beta = np.arcsin(sin_beta)
    return beta


def calculate_rod_force(phi_deg, pressure_data):
    """
    计算连杆力
    
    公式: Fc = F / cosβ
    
    参数:
        phi_deg: 曲轴转角 [度]
        pressure_data: 压力数据字典
    
    返回:
        连杆力 [N]，受压为正
    """
    F = calculate_resultant_force(phi_deg, pressure_data)
    beta = calculate_rod_angle(phi_deg)
    
    # 数值稳定性保护：防止cos(β)接近0时除法溢出
    cos_beta = np.cos(beta)
    if abs(cos_beta) < 1e-10:
        cos_beta = np.sign(cos_beta) * 1e-10 if cos_beta != 0 else 1e-10
    
    Fc = F / cos_beta
    return Fc


def calculate_side_force(phi_deg, pressure_data):
    """
    计算侧向力
    
    公式: Fn = F × tanβ = F × sinβ / cosβ
    
    参数:
        phi_deg: 曲轴转角 [度]
        pressure_data: 压力数据字典
    
    返回:
        侧向力 [N]，指向主推力侧为正
    """
    F = calculate_resultant_force(phi_deg, pressure_data)
    beta = calculate_rod_angle(phi_deg)
    
    # 使用 sin/cos 避免 tan 在接近90°时溢出
    sin_beta = np.sin(beta)
    cos_beta = np.cos(beta)
    
    # 数值稳定性保护
    if abs(cos_beta) < 1e-10:
        cos_beta = np.sign(cos_beta) * 1e-10 if cos_beta != 0 else 1e-10
    
    Fn = F * sin_beta / cos_beta
    return Fn


def calculate_tangential_force(phi_deg, pressure_data):
    """
    计算切向力
    
    公式: Ft = F × sin(φ + β) / cosβ
    
    参数:
        phi_deg: 曲轴转角 [度]
        pressure_data: 压力数据字典
    
    返回:
        切向力 [N]，沿曲柄旋转切线方向
    """
    F = calculate_resultant_force(phi_deg, pressure_data)
    phi = np.radians(phi_deg)
    beta = calculate_rod_angle(phi_deg)
    
    cos_beta = np.cos(beta)
    # 数值稳定性保护
    if abs(cos_beta) < 1e-10:
        cos_beta = np.sign(cos_beta) * 1e-10 if cos_beta != 0 else 1e-10
    
    Ft = F * np.sin(phi + beta) / cos_beta
    return Ft


def calculate_radial_force(phi_deg, pressure_data):
    """
    计算径向力
    
    公式: Fr = F × cos(φ + β) / cosβ
    
    参数:
        phi_deg: 曲轴转角 [度]
        pressure_data: 压力数据字典
    
    返回:
        径向力 [N]，指向曲轴中心为正
    """
    F = calculate_resultant_force(phi_deg, pressure_data)
    phi = np.radians(phi_deg)
    beta = calculate_rod_angle(phi_deg)
    
    cos_beta = np.cos(beta)
    # 数值稳定性保护
    if abs(cos_beta) < 1e-10:
        cos_beta = np.sign(cos_beta) * 1e-10 if cos_beta != 0 else 1e-10
    
    Fr = F * np.cos(phi + beta) / cos_beta
    return Fr


def calculate_all_dynamics(pressure_data):
    """
    计算所有曲轴转角的动力学参数
    
    参数:
        pressure_data: 压力数据字典
    
    返回:
        dict: 包含各力数组的字典
    """
    gas_force = []
    inertia_force = []
    resultant_force = []
    rod_force = []
    side_force = []
    tangential_force = []
    radial_force = []
    
    for phi in CRANK_ANGLES:
        gas_force.append(calculate_gas_force(phi, pressure_data))
        inertia_force.append(calculate_inertia_force(phi))
        resultant_force.append(calculate_resultant_force(phi, pressure_data))
        rod_force.append(calculate_rod_force(phi, pressure_data))
        side_force.append(calculate_side_force(phi, pressure_data))
        tangential_force.append(calculate_tangential_force(phi, pressure_data))
        radial_force.append(calculate_radial_force(phi, pressure_data))
    
    return {
        'crank_angle': CRANK_ANGLES,
        'gas_force': np.array(gas_force),
        'inertia_force': np.array(inertia_force),
        'resultant_force': np.array(resultant_force),
        'rod_force': np.array(rod_force),
        'side_force': np.array(side_force),
        'tangential_force': np.array(tangential_force),
        'radial_force': np.array(radial_force)
    }


if __name__ == "__main__":
    # 测试计算
    from io_utils import load_pressure_data as load_pd
    
    try:
        pressure_data = load_pd('../../data/original/pressure_data_SD195.csv')
        dyn = calculate_all_dynamics(pressure_data)
        
        print("=" * 60)
        print("动力学计算结果")
        print("=" * 60)
        print(f"气体力范围: {dyn['gas_force'].min()/1e3:.2f} ~ {dyn['gas_force'].max()/1e3:.2f} kN")
        print(f"惯性力范围: {dyn['inertia_force'].min()/1e3:.2f} ~ {dyn['inertia_force'].max()/1e3:.2f} kN")
        print(f"合力范围: {dyn['resultant_force'].min()/1e3:.2f} ~ {dyn['resultant_force'].max()/1e3:.2f} kN")
        print(f"连杆力范围: {dyn['rod_force'].min()/1e3:.2f} ~ {dyn['rod_force'].max()/1e3:.2f} kN")
        print(f"侧向力范围: {dyn['side_force'].min()/1e3:.2f} ~ {dyn['side_force'].max()/1e3:.2f} kN")
        print(f"切向力范围: {dyn['tangential_force'].min()/1e3:.2f} ~ {dyn['tangential_force'].max()/1e3:.2f} kN")
        print(f"径向力范围: {dyn['radial_force'].min()/1e3:.2f} ~ {dyn['radial_force'].max()/1e3:.2f} kN")
        print("=" * 60)
    except FileNotFoundError:
        print("请先创建气体压力数据文件")
