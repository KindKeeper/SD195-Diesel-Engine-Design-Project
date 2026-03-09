"""
强度校核计算模块

曲轴：曲柄销圆角安全系数计算
连杆：小头强度校核和刚度校核

使用方法：
1. 根据实际零件尺寸修改本文件中的结构参数
2. 运行 main.py 自动完成强度校核计算
3. 查看生成的强度校核报告
"""

import numpy as np
from parameters import CRANK_RADIUS, ROD_LENGTH, ANGULAR_VELOCITY


# ==================== 曲轴强度校核参数（需根据实际图纸修改）====================

# 曲柄销尺寸参数（单位：mm）
CRANK_PIN_DIAMETER = 45.0  # 曲柄销直径
crank_pin_length = 40.0  # 曲柄销长度
fillet_radius = 3.0  # 圆角半径

# 曲柄臂尺寸参数（单位：mm）
CRANK_WEB_THICKNESS = 20.0  # 曲柄臂厚度
crank_web_width = 80.0  # 曲柄臂宽度

# 材料参数（以45钢为例，需根据实际材料修改）
MATERIAL_YIELD_STRENGTH = 355e6  # 屈服强度 [Pa]
MATERIAL_ULTIMATE_STRENGTH = 600e6  # 抗拉强度 [Pa]
MATERIAL_FATIGUE_LIMIT = 270e6  # 疲劳极限 [Pa]（对称循环）

# 影响系数（根据机械设计手册选取）
STRESS_CONCENTRATION_FACTOR_K = 1.8  # 有效应力集中系数
SIZE_FACTOR_EPSILON = 0.85  # 尺寸系数
SURFACE_FACTOR_BETA = 0.9  # 表面质量系数


# ==================== 连杆强度校核参数（需根据实际图纸修改）====================

# 连杆小头尺寸参数（单位：mm）
ROD_SMALL_END_OUTER_DIA = 45.0  # 小头外径
ROD_SMALL_END_INNER_DIA = 25.0  # 小头内径（活塞销直径）
ROD_SMALL_END_WIDTH = 35.0  # 小头宽度

# 连杆材料参数（以45钢为例）
ROD_MATERIAL_YIELD = 355e6  # 屈服强度 [Pa]
ROD_MATERIAL_FATIGUE = 270e6  # 疲劳极限 [Pa]
ROD_ELASTIC_MODULUS = 210e9  # 弹性模量 [Pa]


# ==================== 曲轴强度校核计算 ====================

def calculate_crankshaft_stress(max_rod_force, max_torque):
    """
    计算曲柄销圆角处的应力
    
    参数:
        max_rod_force: 最大连杆力 [N]
        max_torque: 最大扭矩 [N·m]
    
    返回:
        dict: 包含弯曲应力、扭转应力、等效应力的字典
    """
    # 转换为基本单位（m）
    d = CRANK_PIN_DIAMETER / 1000  # 曲柄销直径 [m]
    r = fillet_radius / 1000  # 圆角半径 [m]
    
    # 弯曲应力计算（简化模型：简支梁）
    # 弯矩 = 力 × 力臂
    bending_moment = max_rod_force * CRANK_RADIUS
    
    # 抗弯截面系数
    section_modulus_bending = np.pi * d**3 / 32
    
    # 名义弯曲应力
    nominal_bending_stress = bending_moment / section_modulus_bending
    
    # 考虑应力集中的弯曲应力
    bending_stress = nominal_bending_stress * STRESS_CONCENTRATION_FACTOR_K
    
    # 扭转应力计算
    # 抗扭截面系数
    section_modulus_torsion = np.pi * d**3 / 16
    
    # 名义扭转应力
    nominal_torsion_stress = max_torque / section_modulus_torsion
    
    # 考虑应力集中的扭转应力
    torsion_stress = nominal_torsion_stress * STRESS_CONCENTRATION_FACTOR_K
    
    # 等效应力（第三强度理论）
    equivalent_stress = np.sqrt(bending_stress**2 + 4 * torsion_stress**2)
    
    return {
        'bending_stress': bending_stress,
        'torsion_stress': torsion_stress,
        'equivalent_stress': equivalent_stress,
        'nominal_bending': nominal_bending_stress,
        'nominal_torsion': nominal_torsion_stress
    }


def calculate_crankshaft_safety_factor(stress_data, load_type='fatigue'):
    """
    计算曲柄销圆角安全系数
    
    参数:
        stress_data: calculate_crankshaft_stress()返回的应力数据
        load_type: 'static'（静强度）或 'fatigue'（疲劳强度）
    
    返回:
        dict: 各安全系数计算结果
    """
    if load_type == 'static':
        # 静强度安全系数
        n_bending = MATERIAL_YIELD_STRENGTH / stress_data['bending_stress']
        n_torsion = MATERIAL_YIELD_STRENGTH / (stress_data['torsion_stress'] * np.sqrt(3))
        n_equivalent = MATERIAL_YIELD_STRENGTH / stress_data['equivalent_stress']
        
        return {
            'type': '静强度安全系数',
            'n_bending': n_bending,
            'n_torsion': n_torsion,
            'n_equivalent': n_equivalent,
            'conclusion': '合格' if n_equivalent >= 1.5 else '不合格'
        }
    
    else:  # fatigue
        # 疲劳强度安全系数（考虑影响系数）
        # 修正的疲劳极限
        corrected_fatigue_limit = (MATERIAL_FATIGUE_LIMIT * 
                                   SIZE_FACTOR_EPSILON * 
                                   SURFACE_FACTOR_BETA / 
                                   STRESS_CONCENTRATION_FACTOR_K)
        
        # 弯曲疲劳安全系数
        n_bending_fatigue = corrected_fatigue_limit / stress_data['bending_stress']
        
        # 扭转疲劳安全系数
        n_torsion_fatigue = corrected_fatigue_limit / (stress_data['torsion_stress'] * np.sqrt(3))
        
        # 综合安全系数（简化计算）
        n_fatigue = corrected_fatigue_limit / stress_data['equivalent_stress']
        
        return {
            'type': '疲劳强度安全系数',
            'corrected_fatigue_limit': corrected_fatigue_limit,
            'n_bending': n_bending_fatigue,
            'n_torsion': n_torsion_fatigue,
            'n_fatigue': n_fatigue,
            'conclusion': '合格' if n_fatigue >= 1.8 else '不合格'
        }


# ==================== 连杆强度校核计算 ====================

def calculate_rod_small_end_stress(max_rod_force):
    """
    计算连杆小头应力
    
    参数:
        max_rod_force: 最大连杆力 [N]（拉力或压力）
    
    返回:
        dict: 拉应力和压应力
    """
    # 尺寸参数（转换为m）
    d_outer = ROD_SMALL_END_OUTER_DIA / 1000
    d_inner = ROD_SMALL_END_INNER_DIA / 1000
    width = ROD_SMALL_END_WIDTH / 1000
    
    # 截面积
    area = np.pi * (d_outer**2 - d_inner**2) / 4
    
    # 拉应力（进气冲程上止点，惯性力最大）
    tensile_stress = abs(max_rod_force) / area
    
    # 压应力（爆发压力时）
    compressive_stress = abs(max_rod_force) / area
    
    return {
        'area': area,
        'tensile_stress': tensile_stress,
        'compressive_stress': compressive_stress,
        'allowable_stress': ROD_MATERIAL_YIELD / 2.5  # 许用应力
    }


def calculate_rod_small_end_stiffness(max_rod_force):
    """
    计算连杆小头刚度（变形量）
    
    参数:
        max_rod_force: 最大连杆力 [N]
    
    返回:
        dict: 变形量和刚度评估
    """
    # 尺寸参数
    d_outer = ROD_SMALL_END_OUTER_DIA / 1000
    d_inner = ROD_SMALL_END_INNER_DIA / 1000
    width = ROD_SMALL_END_WIDTH / 1000
    
    # 简化计算：将圆环简化为曲梁
    # 平均半径
    mean_radius = (d_outer + d_inner) / 4
    
    # 截面惯性矩（矩形截面近似）
    h = (d_outer - d_inner) / 2  # 截面高度
    moment_of_inertia = width * h**3 / 12
    
    # 最大变形量（简化公式）
    # delta = F * R^3 / (E * I) * 系数
    deformation = (abs(max_rod_force) * mean_radius**3 / 
                   (ROD_ELASTIC_MODULUS * moment_of_inertia) * 0.1)
    
    # 许用变形量（通常取内径的0.001~0.002倍）
    allowable_deformation = d_inner * 0.0015
    
    return {
        'deformation': deformation,
        'allowable_deformation': allowable_deformation,
        'stiffness_ratio': deformation / allowable_deformation,
        'conclusion': '合格' if deformation <= allowable_deformation else '不合格'
    }


def calculate_rod_safety_factor(stress_data, stiffness_data):
    """
    计算连杆安全系数
    
    参数:
        stress_data: calculate_rod_small_end_stress()返回的应力数据
        stiffness_data: calculate_rod_small_end_stiffness()返回的刚度数据
    
    返回:
        dict: 安全系数评估结果
    """
    # 强度安全系数
    n_tensile = ROD_MATERIAL_YIELD / stress_data['tensile_stress']
    n_compressive = ROD_MATERIAL_YIELD / stress_data['compressive_stress']
    
    return {
        'n_tensile': n_tensile,
        'n_compressive': n_compressive,
        'stiffness_conclusion': stiffness_data['conclusion'],
        'overall_conclusion': '合格' if (n_tensile >= 2.0 and 
                                         n_compressive >= 2.0 and 
                                         stiffness_data['conclusion'] == '合格') else '不合格'
    }


# ==================== 主计算函数 ====================

def perform_strength_check(dynamics_data, bearing_data):
    """
    执行完整的强度校核计算
    
    参数:
        dynamics_data: 动力学计算结果
        bearing_data: 轴承负荷计算结果
    
    返回:
        dict: 包含所有强度校核结果的字典
    """
    # 提取极值
    max_rod_force = np.max(np.abs(dynamics_data['rod_force']))
    max_torque = np.max(np.abs(dynamics_data['tangential_force'])) * CRANK_RADIUS
    
    # 曲轴强度校核
    crankshaft_stress = calculate_crankshaft_stress(max_rod_force, max_torque)
    crankshaft_safety_static = calculate_crankshaft_safety_factor(crankshaft_stress, 'static')
    crankshaft_safety_fatigue = calculate_crankshaft_safety_factor(crankshaft_stress, 'fatigue')
    
    # 连杆强度校核
    rod_stress = calculate_rod_small_end_stress(max_rod_force)
    rod_stiffness = calculate_rod_small_end_stiffness(max_rod_force)
    rod_safety = calculate_rod_safety_factor(rod_stress, rod_stiffness)
    
    return {
        'crankshaft': {
            'stress': crankshaft_stress,
            'safety_static': crankshaft_safety_static,
            'safety_fatigue': crankshaft_safety_fatigue,
            'max_rod_force': max_rod_force,
            'max_torque': max_torque
        },
        'connecting_rod': {
            'stress': rod_stress,
            'stiffness': rod_stiffness,
            'safety': rod_safety
        }
    }


def save_strength_report(results, filepath):
    """
    保存强度校核报告
    
    参数:
        results: perform_strength_check()返回的结果
        filepath: 报告保存路径
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("SD195柴油机强度校核计算报告\n")
        f.write("=" * 70 + "\n\n")
        
        # 曲轴部分
        f.write("一、曲轴强度校核（曲柄销圆角）\n")
        f.write("-" * 70 + "\n")
        f.write(f"最大连杆力: {results['crankshaft']['max_rod_force']/1e3:.2f} kN\n")
        f.write(f"最大扭矩: {results['crankshaft']['max_torque']:.2f} N·m\n\n")
        
        f.write("应力计算结果:\n")
        stress = results['crankshaft']['stress']
        f.write(f"  弯曲应力: {stress['bending_stress']/1e6:.2f} MPa\n")
        f.write(f"  扭转应力: {stress['torsion_stress']/1e6:.2f} MPa\n")
        f.write(f"  等效应力: {stress['equivalent_stress']/1e6:.2f} MPa\n\n")
        
        f.write("安全系数:\n")
        static = results['crankshaft']['safety_static']
        fatigue = results['crankshaft']['safety_fatigue']
        f.write(f"  静强度安全系数: {static['n_equivalent']:.2f} (要求≥1.5) [{static['conclusion']}]\n")
        f.write(f"  疲劳安全系数: {fatigue['n_fatigue']:.2f} (要求≥1.8) [{fatigue['conclusion']}]\n\n")
        
        # 连杆部分
        f.write("二、连杆小头强度校核\n")
        f.write("-" * 70 + "\n")
        rod_stress = results['connecting_rod']['stress']
        f.write(f"截面积: {rod_stress['area']*1e6:.2f} mm²\n")
        f.write(f"拉应力: {rod_stress['tensile_stress']/1e6:.2f} MPa\n")
        f.write(f"压应力: {rod_stress['compressive_stress']/1e6:.2f} MPa\n")
        f.write(f"许用应力: {rod_stress['allowable_stress']/1e6:.2f} MPa\n\n")
        
        f.write("刚度校核:\n")
        stiffness = results['connecting_rod']['stiffness']
        f.write(f"  变形量: {stiffness['deformation']*1e6:.4f} μm\n")
        f.write(f"  许用变形: {stiffness['allowable_deformation']*1e6:.4f} μm\n")
        f.write(f"  结论: {stiffness['conclusion']}\n\n")
        
        f.write("安全系数:\n")
        rod_safety = results['connecting_rod']['safety']
        f.write(f"  拉伸安全系数: {rod_safety['n_tensile']:.2f} (要求≥2.0)\n")
        f.write(f"  压缩安全系数: {rod_safety['n_compressive']:.2f} (要求≥2.0)\n")
        f.write(f"  综合结论: {rod_safety['overall_conclusion']}\n\n")
        
        f.write("=" * 70 + "\n")
        f.write("注意：本报告基于简化计算模型，实际设计应参考零件图纸和\n")
        f.write("      相关设计手册进行详细计算。\n")
        f.write("=" * 70 + "\n")
    
    print(f"强度校核报告已保存: {filepath}")


if __name__ == "__main__":
    print("强度校核模块")
    print("运行 main.py 执行完整的强度校核计算")
    print("\n提示：请根据实际零件尺寸修改本文件中的结构参数")
