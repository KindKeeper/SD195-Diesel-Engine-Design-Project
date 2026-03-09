"""
运动学计算模块
计算活塞位移、速度、加速度

注：使用带活塞偏移的公式（e = 7mm）
"""

import numpy as np
from parameters import (
    CRANK_RADIUS, ROD_LENGTH, LAMBDA,
    ANGULAR_VELOCITY, CRANK_ANGLES, PISTON_OFFSET
)


def calculate_piston_displacement(phi_deg):
    """
    计算活塞位移
    
    公式: x = R(1 - cosφ) + L(1 - cosβ)
          其中 sin(β) = (R·sinφ + e) / L
    
    参数:
        phi_deg: 曲轴转角 [度]
    
    返回:
        活塞位移 [m]，从上止点开始测量
    """
    phi = np.radians(phi_deg)
    sin_phi = np.sin(phi)
    cos_phi = np.cos(phi)
    
    # 连杆摆角 sin(β) = (R·sinφ + e) / L
    sin_beta = (CRANK_RADIUS * sin_phi + PISTON_OFFSET) / ROD_LENGTH
    sin_beta = np.clip(sin_beta, -1.0, 1.0)  # 数值稳定性
    cos_beta = np.sqrt(max(1 - sin_beta**2, 1e-10))
    
    # 活塞位移
    x = CRANK_RADIUS * (1 - cos_phi) + ROD_LENGTH * (1 - cos_beta)
    return x


def calculate_piston_velocity(phi_deg):
    """
    计算活塞速度
    
    公式: v = Rω[sinφ + cosφ·tanβ]
          其中 sin(β) = (R·sinφ + e) / L
    
    参数:
        phi_deg: 曲轴转角 [度]
    
    返回:
        活塞速度 [m/s]
    """
    phi = np.radians(phi_deg)
    sin_phi = np.sin(phi)
    cos_phi = np.cos(phi)
    
    # 连杆摆角
    sin_beta = (CRANK_RADIUS * sin_phi + PISTON_OFFSET) / ROD_LENGTH
    sin_beta = np.clip(sin_beta, -1.0, 1.0)
    cos_beta = np.sqrt(max(1 - sin_beta**2, 1e-10))
    
    # 活塞速度
    v = CRANK_RADIUS * ANGULAR_VELOCITY * (sin_phi + cos_phi * sin_beta / cos_beta)
    return v


def calculate_piston_acceleration(phi_deg):
    """
    计算活塞加速度
    
    公式: a = Rω²[cos(φ+β)/cosβ + λ·cos²φ/cos³β]
          其中 sin(β) = (R·sinφ + e) / L
    
    参数:
        phi_deg: 曲轴转角 [度]
    
    返回:
        活塞加速度 [m/s²]
    """
    phi = np.radians(phi_deg)
    sin_phi = np.sin(phi)
    cos_phi = np.cos(phi)
    
    # 连杆摆角
    sin_beta = (CRANK_RADIUS * sin_phi + PISTON_OFFSET) / ROD_LENGTH
    sin_beta = np.clip(sin_beta, -1.0, 1.0)
    cos_beta = np.sqrt(max(1 - sin_beta**2, 1e-10))
    
    # 活塞加速度
    a = CRANK_RADIUS * (ANGULAR_VELOCITY ** 2) * (
        np.cos(phi + np.arcsin(sin_beta)) / cos_beta + 
        (LAMBDA * cos_phi**2) / (cos_beta**3)
    )
    return a


def calculate_all_kinematics():
    """
    计算所有曲轴转角的运动学参数
    
    返回:
        dict: 包含位移、速度、加速度数组的字典
    """
    displacement = []
    velocity = []
    acceleration = []
    
    for phi in CRANK_ANGLES:
        displacement.append(calculate_piston_displacement(phi))
        velocity.append(calculate_piston_velocity(phi))
        acceleration.append(calculate_piston_acceleration(phi))
    
    return {
        'crank_angle': CRANK_ANGLES,
        'displacement': np.array(displacement),
        'velocity': np.array(velocity),
        'acceleration': np.array(acceleration)
    }


def verify_kinematics():
    """验证运动学计算"""
    print("=" * 60)
    print("运动学计算验证")
    print("=" * 60)
    
    # 验证点：上止点(0°)
    x_0 = calculate_piston_displacement(0)
    v_0 = calculate_piston_velocity(0)
    a_0 = calculate_piston_acceleration(0)
    
    print(f"上止点(0°):")
    print(f"  位移 x = {x_0*1e3:.4f} mm (应为0)")
    print(f"  速度 v = {v_0:.4f} m/s (应为0)")
    print(f"  加速度 a = {a_0:.2f} m/s²")
    
    # 验证点：下止点(180°)
    x_180 = calculate_piston_displacement(180)
    v_180 = calculate_piston_velocity(180)
    a_180 = calculate_piston_acceleration(180)
    
    print(f"下止点(180°):")
    print(f"  位移 x = {x_180*1e3:.4f} mm (应为2R={2*CRANK_RADIUS*1e3:.1f}mm)")
    print(f"  速度 v = {v_180:.4f} m/s (应为0)")
    print(f"  加速度 a = {a_180:.2f} m/s²")
    
    print("=" * 60)


if __name__ == "__main__":
    verify_kinematics()
    
    kin = calculate_all_kinematics()
    print(f"\n计算完成，共 {len(kin['crank_angle'])} 个数据点")
    print(f"位移范围: {kin['displacement'].min()*1e3:.2f} ~ {kin['displacement'].max()*1e3:.2f} mm")
    print(f"速度范围: {kin['velocity'].min():.2f} ~ {kin['velocity'].max():.2f} m/s")
    print(f"加速度范围: {kin['acceleration'].min():.2f} ~ {kin['acceleration'].max():.2f} m/s²")
