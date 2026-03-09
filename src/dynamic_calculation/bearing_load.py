"""
轴承负荷计算模块
计算连杆轴颈负荷和主轴颈负荷
"""

import numpy as np
from parameters import (
    CRANK_ANGLES, ROD_LENGTH, CRANK_RADIUS,
    ROD_ROT_MASS, CRANK_PIN_MASS, CRANK_WEB_MASS, BALANCE_WEIGHT_MASS,
    CRANK_PIN_COG_R, CRANK_WEB_COG_R, BALANCE_WEIGHT_COG_R,
    ANGULAR_VELOCITY
)
from dynamics import calculate_rod_force, calculate_rod_angle


def calculate_rod_bearing_load(phi_deg, pressure_data):
    """
    计算连杆轴颈负荷
    
    连杆轴颈承受连杆传来的力，需要分解到坐标系中
    
    参数:
        phi_deg: 曲轴转角 [度]
        pressure_data: 压力数据字典
    
    返回:
        dict: {'x': x方向负荷, 'y': y方向负荷, 'magnitude': 合力大小, 'angle': 方向角}
    """
    Fc = calculate_rod_force(phi_deg, pressure_data)
    beta = calculate_rod_angle(phi_deg)
    phi = np.radians(phi_deg)
    
    # 连杆力在曲柄销坐标系中的分解
    # 连杆受压时，力指向曲柄中心
    # x轴：沿曲柄向外为正
    # y轴：垂直曲柄，旋转方向90°为正
    
    Fx = -Fc * np.cos(phi + beta)  # x方向
    Fy = -Fc * np.sin(phi + beta)  # y方向
    
    magnitude = np.sqrt(Fx**2 + Fy**2)
    angle = np.degrees(np.arctan2(Fy, Fx))
    
    return {
        'x': Fx,
        'y': Fy,
        'magnitude': magnitude,
        'angle': angle
    }


def calculate_rotating_inertia_force_components(phi_deg):
    """
    计算旋转质量离心力分量
    
    旋转质量包括：连杆旋转部分、曲柄销、曲柄臂、平衡重
    各质量产生的离心力方向：
    - 连杆旋转质量、曲柄销、曲柄臂：沿曲柄方向向外（角度φ）
    - 平衡重：通常安装在曲柄对面（角度φ+180°），用于抵消部分旋转质量
    
    参数:
        phi_deg: 曲轴转角 [度]
    
    返回:
        dict: {'x': x方向离心力, 'y': y方向离心力, 'magnitude': 合力大小}
    """
    phi = np.radians(phi_deg)
    omega2 = ANGULAR_VELOCITY ** 2
    
    # 沿曲柄方向的旋转质量（连杆大头、曲柄销、曲柄臂）
    # 这些质量的重心都在曲柄半径或其附近，方向沿曲柄向外
    mass_along_crank = ROD_ROT_MASS + CRANK_PIN_MASS + CRANK_WEB_MASS
    radius_along_crank = (ROD_ROT_MASS * CRANK_RADIUS + 
                          CRANK_PIN_MASS * CRANK_PIN_COG_R + 
                          CRANK_WEB_MASS * CRANK_WEB_COG_R) / mass_along_crank
    
    F_crank = mass_along_crank * radius_along_crank * omega2
    
    # 平衡重：通常安装在曲柄对面（180°方向）
    # 平衡重的重心半径不同，方向与曲柄相反
    F_balance = BALANCE_WEIGHT_MASS * BALANCE_WEIGHT_COG_R * omega2
    
    # 离心力分量计算
    # 曲柄方向质量：沿角度phi方向
    Fx_crank = F_crank * np.cos(phi)
    Fy_crank = F_crank * np.sin(phi)
    
    # 平衡重：沿角度phi+π方向（与曲柄相反）
    Fx_balance = F_balance * np.cos(phi + np.pi)
    Fy_balance = F_balance * np.sin(phi + np.pi)
    
    # 合成离心力
    Fx_total = Fx_crank + Fx_balance
    Fy_total = Fy_crank + Fy_balance
    
    return {
        'x': Fx_total,
        'y': Fy_total,
        'magnitude': np.sqrt(Fx_total**2 + Fy_total**2),
        'F_crank': F_crank,
        'F_balance': F_balance
    }


def calculate_main_bearing_load(phi_deg, pressure_data):
    """
    计算主轴颈负荷
    
    主轴颈负荷由连杆轴颈负荷和旋转质量离心力合成
    
    参数:
        phi_deg: 曲轴转角 [度]
        pressure_data: 压力数据字典
    
    返回:
        dict: {'x': x方向负荷, 'y': y方向负荷, 'magnitude': 合力大小, 'angle': 方向角}
    """
    # 连杆轴颈负荷
    rod_load = calculate_rod_bearing_load(phi_deg, pressure_data)
    
    # 旋转质量离心力（按角度矢量合成）
    rot_force = calculate_rotating_inertia_force_components(phi_deg)
    
    # 主轴颈负荷 = 连杆轴颈负荷 + 离心力
    Fx = rod_load['x'] + rot_force['x']
    Fy = rod_load['y'] + rot_force['y']
    
    magnitude = np.sqrt(Fx**2 + Fy**2)
    angle = np.degrees(np.arctan2(Fy, Fx))
    
    return {
        'x': Fx,
        'y': Fy,
        'magnitude': magnitude,
        'angle': angle
    }


def calculate_all_bearing_loads(pressure_data):
    """
    计算所有曲轴转角的轴承负荷
    
    参数:
        pressure_data: 压力数据字典
    
    返回:
        dict: 包含连杆轴颈负荷和主轴颈负荷的字典
    """
    rod_bearing_x = []
    rod_bearing_y = []
    rod_bearing_mag = []
    rod_bearing_angle = []
    
    main_bearing_x = []
    main_bearing_y = []
    main_bearing_mag = []
    main_bearing_angle = []
    
    for phi in CRANK_ANGLES:
        # 连杆轴颈负荷
        rod = calculate_rod_bearing_load(phi, pressure_data)
        rod_bearing_x.append(rod['x'])
        rod_bearing_y.append(rod['y'])
        rod_bearing_mag.append(rod['magnitude'])
        rod_bearing_angle.append(rod['angle'])
        
        # 主轴颈负荷
        main = calculate_main_bearing_load(phi, pressure_data)
        main_bearing_x.append(main['x'])
        main_bearing_y.append(main['y'])
        main_bearing_mag.append(main['magnitude'])
        main_bearing_angle.append(main['angle'])
    
    return {
        'crank_angle': CRANK_ANGLES,
        'rod_bearing': {
            'x': np.array(rod_bearing_x),
            'y': np.array(rod_bearing_y),
            'magnitude': np.array(rod_bearing_mag),
            'angle': np.array(rod_bearing_angle)
        },
        'main_bearing': {
            'x': np.array(main_bearing_x),
            'y': np.array(main_bearing_y),
            'magnitude': np.array(main_bearing_mag),
            'angle': np.array(main_bearing_angle)
        }
    }


def prepare_polar_plot_data(bearing_load_data, bearing_type='rod'):
    """
    准备极坐标图数据
    
    参数:
        bearing_load_data: 轴承负荷计算结果
        bearing_type: 'rod' 或 'main'
    
    返回:
        tuple: (角度数组, 负荷大小数组)
    """
    key = f'{bearing_type}_bearing'
    angles = np.radians(CRANK_ANGLES)
    magnitudes = bearing_load_data[key]['magnitude']
    
    return angles, magnitudes


if __name__ == "__main__":
    # 测试计算
    from io_utils import load_pressure_data
    
    try:
        pressure_data = load_pressure_data('../../data/original/pressure_data_SD195.csv')
        loads = calculate_all_bearing_loads(pressure_data)
        
        print("=" * 60)
        print("轴承负荷计算结果")
        print("=" * 60)
        
        # 测试几个角度的旋转离心力
        test_angles = [0, 90, 180, 270]
        print("旋转质量离心力（不同角度）：")
        for phi in test_angles:
            rot = calculate_rotating_inertia_force_components(phi)
            print(f"  {phi}°: 合力={rot['magnitude']/1e3:.2f} kN, "
                  f"曲柄质量={rot['F_crank']/1e3:.2f} kN, "
                  f"平衡重={rot['F_balance']/1e3:.2f} kN")
        print()
        print("连杆轴颈负荷:")
        print(f"  范围: {loads['rod_bearing']['magnitude'].min()/1e3:.2f} ~ {loads['rod_bearing']['magnitude'].max()/1e3:.2f} kN")
        print()
        print("主轴颈负荷:")
        print(f"  范围: {loads['main_bearing']['magnitude'].min()/1e3:.2f} ~ {loads['main_bearing']['magnitude'].max()/1e3:.2f} kN")
        print("=" * 60)
    except FileNotFoundError:
        print("请先创建气体压力数据文件")
