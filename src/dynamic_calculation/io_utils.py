"""
输入输出工具模块
读写 CSV 文件
"""

import csv
import os
import numpy as np


def load_pressure_data(filepath):
    """
    从CSV文件加载气体压力数据
    
    参数:
        filepath: CSV文件路径
    
    返回:
        dict: {曲轴转角(度): 气体压力(Pa)}
    
    异常:
        ValueError: 数据格式错误或数值异常
    """
    pressure_data = {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required_columns = ['crank_angle', 'pressure_mpa']
            
            # 检查表头
            if not reader.fieldnames:
                raise ValueError("CSV文件为空或格式错误")
            
            missing_cols = [col for col in required_columns if col not in reader.fieldnames]
            if missing_cols:
                raise ValueError(f"CSV缺少必需列: {missing_cols}")
            
            for row in reader:
                try:
                    angle = int(row['crank_angle'])
                    pressure_mpa = float(row['pressure_mpa'])
                    
                    # 数据范围验证
                    if not (0 <= angle <= 720):
                        raise ValueError(f"曲轴转角 {angle}° 超出范围 [0, 720]")
                    
                    if not (-0.5 <= pressure_mpa <= 50):
                        raise ValueError(f"气体压力 {pressure_mpa} MPa 超出合理范围 [-0.5, 50]")
                    
                    pressure = pressure_mpa * 1e6  # MPa 转 Pa
                    pressure_data[angle] = pressure
                    
                except (ValueError, TypeError) as e:
                    raise ValueError(f"第 {reader.line_num} 行数据错误: {e}")
    
    except FileNotFoundError:
        raise FileNotFoundError(f"找不到气体压力数据文件: {filepath}")
    
    # 检查数据完整性
    expected_angles = set(range(0, 721, 10))  # 0, 10, 20, ..., 720
    actual_angles = set(pressure_data.keys())
    missing_angles = expected_angles - actual_angles
    
    if missing_angles:
        print(f"警告: 气体压力数据缺失以下角度: {sorted(missing_angles)}")
        # 使用插值填充缺失数据
        for angle in sorted(missing_angles):
            # 简单线性插值
            lower = max([a for a in actual_angles if a < angle], default=0)
            upper = min([a for a in actual_angles if a > angle], default=720)
            if lower in pressure_data and upper in pressure_data:
                ratio = (angle - lower) / (upper - lower) if upper != lower else 0
                pressure_data[angle] = pressure_data[lower] + ratio * (pressure_data[upper] - pressure_data[lower])
    
    return pressure_data


def load_engine_specs(filepath):
    """
    从CSV文件加载发动机规格参数
    
    参数:
        filepath: CSV文件路径
    
    返回:
        dict: 发动机参数字典
    """
    specs = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            param_name = row['parameter']
            param_value = float(row['value'])
            param_unit = row['unit']
            specs[param_name] = {'value': param_value, 'unit': param_unit}
    
    return specs


def save_to_csv(data_dict, filepath, columns=None):
    """
    将数据保存为CSV文件
    
    参数:
        data_dict: 数据字典，键为列名
        filepath: 保存路径
        columns: 列顺序列表（可选）
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # 确定列顺序
    if columns is None:
        columns = list(data_dict.keys())
    
    # 写入CSV
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # 写入表头
        writer.writerow(columns)
        # 写入数据
        n_rows = len(data_dict[columns[0]])
        for i in range(n_rows):
            row = [data_dict[col][i] for col in columns]
            writer.writerow(row)
    
    print(f"数据已保存: {filepath}")


def save_kinematics_to_csv(kinematics_data, filepath):
    """
    保存运动学计算结果到CSV
    
    参数:
        kinematics_data: 运动学计算结果
        filepath: 保存路径
    """
    # 转换为更友好的单位
    data = {
        '曲轴转角(度)': kinematics_data['crank_angle'],
        '位移(mm)': kinematics_data['displacement'] * 1e3,
        '速度(m/s)': kinematics_data['velocity'],
        '加速度(m/s2)': kinematics_data['acceleration']
    }
    
    save_to_csv(data, filepath)


def save_torque_to_csv(dynamics_data, filepath):
    """
    保存扭矩计算结果到CSV（附表5）
    
    参数:
        dynamics_data: 动力学计算结果
        filepath: 保存路径
    """
    from parameters import CRANK_RADIUS
    
    angles = dynamics_data['crank_angle']
    tangential_forces = dynamics_data['tangential_force']
    
    # 扭矩 = 切向力 × 曲柄半径
    torques = tangential_forces * CRANK_RADIUS  # [N·m]
    
    data = {
        '曲轴转角(度)': angles,
        '切向力(N)': tangential_forces,
        '扭矩(N·m)': torques
    }
    
    save_to_csv(data, filepath)


def save_dynamics_to_csv(dynamics_data, filepath, use_pressure_unit=False):
    """
    保存动力学计算结果到CSV
    
    参数:
        dynamics_data: 动力学计算结果
        filepath: 保存路径
        use_pressure_unit: 是否使用压力单位MPa（默认False，使用力的单位N）
        
    注:
        根据内燃机设计规范，"气体作用力"、"惯性力"、"连杆力"等本质都是力，
        应使用力的单位N（或kN）。只有"气体压力"本身使用压力单位MPa。
    """
    from parameters import PISTON_AREA
    
    data = {'曲轴转角(度)': dynamics_data['crank_angle']}
    
    # 转换系数：力[N] -> 压力[MPa] = F[N] / A[m²] / 1e6
    # 或 力[N] -> 力[kN] = F[N] / 1e3
    if use_pressure_unit:
        # 使用压力单位 MPa（除以活塞面积）- 仅用于特殊需求
        factor = 1e6 * PISTON_AREA  # N -> MPa 的转换系数
        unit_suffix = '(MPa)'
    else:
        # 使用力的单位 kN - 标准做法
        factor = 1e3  # N -> kN 的转换系数
        unit_suffix = '(kN)'
    
    # 根据可用字段添加数据
    if 'gas_force' in dynamics_data:
        data[f'气体力{unit_suffix}'] = dynamics_data['gas_force'] / factor
    if 'inertia_force' in dynamics_data:
        data[f'往复惯性力{unit_suffix}'] = dynamics_data['inertia_force'] / factor
    if 'resultant_force' in dynamics_data:
        data[f'合力{unit_suffix}'] = dynamics_data['resultant_force'] / factor
    if 'rod_force' in dynamics_data:
        data[f'连杆力{unit_suffix}'] = dynamics_data['rod_force'] / factor
    if 'side_force' in dynamics_data:
        data[f'侧向力{unit_suffix}'] = dynamics_data['side_force'] / factor
    if 'tangential_force' in dynamics_data:
        data[f'切向力{unit_suffix}'] = dynamics_data['tangential_force'] / factor
    if 'radial_force' in dynamics_data:
        data[f'径向力{unit_suffix}'] = dynamics_data['radial_force'] / factor
    
    save_to_csv(data, filepath)


def save_bearing_load_to_csv(bearing_data, bearing_type, filepath, use_pressure_unit=False):
    """
    保存轴承负荷计算结果到CSV
    
    参数:
        bearing_data: 轴承负荷计算结果
        bearing_type: 'rod' 或 'main'
        filepath: 保存路径
        use_pressure_unit: 是否使用压力单位MPa（默认False，使用力的单位kN）
        
    注:
        "轴颈负荷"、"轴承负荷"本质都是力，应使用力的单位N（或kN）。
    """
    from parameters import PISTON_AREA
    
    key = f'{bearing_type}_bearing'
    
    # 转换系数
    if use_pressure_unit:
        factor = 1e6 * PISTON_AREA  # N -> MPa
        unit_suffix = '(MPa)'
    else:
        factor = 1e3  # N -> kN
        unit_suffix = '(kN)'
    
    data = {
        '曲轴转角(度)': bearing_data['crank_angle'],
        f'Fx{unit_suffix}': bearing_data[key]['x'] / factor,
        f'Fy{unit_suffix}': bearing_data[key]['y'] / factor,
        f'合力{unit_suffix}': bearing_data[key]['magnitude'] / factor,
        '方向角(度)': bearing_data[key]['angle']
    }
    
    save_to_csv(data, filepath)


def create_sample_data_files(data_dir='../../data/original/'):
    """
    创建示例数据文件（用于测试）
    
    参数:
        data_dir: 数据目录路径
    """
    os.makedirs(data_dir, exist_ok=True)
    
    # 发动机规格
    engine_specs = [
        ['parameter', 'value', 'unit'],
        ['rated_power', '8.8', 'kW'],
        ['rated_speed', '2000', 'r/min'],
        ['bore', '95', 'mm'],
        ['stroke', '115', 'mm'],
        ['crank_radius', '57.5', 'mm'],
        ['rod_length', '175', 'mm'],
        ['lambda', '0.329', '-'],
        ['piston_mass', '1.38', 'kg'],
        ['rod_recip_mass', '0.543', 'kg'],
        ['rod_rot_mass', '1.267', 'kg']
    ]
    
    with open(os.path.join(data_dir, 'engine_specifications_SD195.csv'), 
              'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(engine_specs)
    
    print(f"示例发动机规格文件已创建")
    
    # 气体压力数据（简化示例）
    # 实际使用时需要替换为完整数据
    pressure_data = [['crank_angle', 'pressure_mpa']]
    
    # 进气冲程 (0-180°)
    for angle in range(0, 180, 10):
        pressure_data.append([str(angle), str(0.0857)])
    
    # 压缩冲程 (180-360°) - 简化为线性增加
    for angle in range(180, 360, 10):
        p = 0.0857 + (6.7025 - 0.0857) * (angle - 180) / 180
        pressure_data.append([str(angle), str(round(p, 4))])
    
    # 做功冲程 (360-540°)
    pressure_data.append(['360', '6.7025'])
    pressure_data.append(['370', '7.0849'])  # 峰值
    pressure_data.append(['380', '6.5'])
    for angle in range(390, 540, 10):
        p = 0.4 + (6.5 - 0.4) * (540 - angle) / 160
        pressure_data.append([str(angle), str(round(p, 4))])
    
    # 排气冲程 (540-720°)
    for angle in range(540, 721, 10):
        pressure_data.append([str(angle), str(0.0936)])
    
    with open(os.path.join(data_dir, 'pressure_data_SD195.csv'), 
              'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(pressure_data)
    
    print(f"⚠️  警告: 示例气体压力数据文件已创建")
    print(f"    该数据使用线性插值生成，仅供程序测试使用！")
    print(f"    实际课程设计计算必须使用真实测量数据。")
    print(f"    请将 data/original/pressure_data_SD195.csv 替换为指导书附录2的数据。")
    print(f"    使用示例数据会导致计算结果严重失真！")


if __name__ == "__main__":
    print("创建示例数据文件...")
    create_sample_data_files()
    print("\n示例数据文件创建完成！")
