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
    """
    pressure_data = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            angle = int(row['crank_angle'])
            pressure = float(row['pressure_mpa']) * 1e6  # MPa 转 Pa
            pressure_data[angle] = pressure
    
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


def save_dynamics_to_csv(dynamics_data, filepath):
    """
    保存动力学计算结果到CSV
    
    参数:
        dynamics_data: 动力学计算结果
        filepath: 保存路径
    """
    # 转换为kN单位
    data = {'曲轴转角(度)': dynamics_data['crank_angle']}
    
    # 根据可用字段添加数据
    if 'gas_force' in dynamics_data:
        data['气体力(kN)'] = dynamics_data['gas_force'] / 1e3
    if 'inertia_force' in dynamics_data:
        data['往复惯性力(kN)'] = dynamics_data['inertia_force'] / 1e3
    if 'resultant_force' in dynamics_data:
        data['合力(kN)'] = dynamics_data['resultant_force'] / 1e3
    if 'rod_force' in dynamics_data:
        data['连杆力(kN)'] = dynamics_data['rod_force'] / 1e3
    if 'side_force' in dynamics_data:
        data['侧向力(kN)'] = dynamics_data['side_force'] / 1e3
    if 'tangential_force' in dynamics_data:
        data['切向力(kN)'] = dynamics_data['tangential_force'] / 1e3
    if 'radial_force' in dynamics_data:
        data['径向力(kN)'] = dynamics_data['radial_force'] / 1e3
    
    save_to_csv(data, filepath)


def save_bearing_load_to_csv(bearing_data, bearing_type, filepath):
    """
    保存轴承负荷计算结果到CSV
    
    参数:
        bearing_data: 轴承负荷计算结果
        bearing_type: 'rod' 或 'main'
        filepath: 保存路径
    """
    key = f'{bearing_type}_bearing'
    
    data = {
        '曲轴转角(度)': bearing_data['crank_angle'],
        'Fx(kN)': bearing_data[key]['x'] / 1e3,
        'Fy(kN)': bearing_data[key]['y'] / 1e3,
        '合力(kN)': bearing_data[key]['magnitude'] / 1e3,
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
        pressure_data.append([angle, 0.0857])
    
    # 压缩冲程 (180-360°) - 简化为线性增加
    for angle in range(180, 360, 10):
        p = 0.0857 + (6.7025 - 0.0857) * (angle - 180) / 180
        pressure_data.append([angle, round(p, 4)])
    
    # 做功冲程 (360-540°)
    pressure_data.append([360, 6.7025])
    pressure_data.append([370, 7.0849])  # 峰值
    pressure_data.append([380, 6.5])
    for angle in range(390, 540, 10):
        p = 0.4 + (6.5 - 0.4) * (540 - angle) / 160
        pressure_data.append([angle, round(p, 4)])
    
    # 排气冲程 (540-720°)
    for angle in range(540, 721, 10):
        pressure_data.append([angle, 0.0936])
    
    with open(os.path.join(data_dir, 'pressure_data_SD195.csv'), 
              'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(pressure_data)
    
    print(f"示例气体压力数据文件已创建")
    print(f"注意：请将 data/original/pressure_data_SD195.csv 替换为实际测量数据")


if __name__ == "__main__":
    print("创建示例数据文件...")
    create_sample_data_files()
    print("\n示例数据文件创建完成！")
