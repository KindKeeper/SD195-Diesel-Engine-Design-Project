"""
强度校核计算模块

曲轴：曲柄销圆角安全系数计算
连杆：小头强度校核和刚度校核

参考：课程设计指导书
"""

import numpy as np
from parameters import CRANK_RADIUS, ROD_LENGTH, ANGULAR_VELOCITY, BORE


# ==================== 曲轴尺寸经验公式 ====================

def calculate_crankshaft_dimensions(bore_mm):
    """
    根据缸径计算曲轴主要尺寸（经验公式）
    来源：柴油机设计手册
    """
    return {
        'crank_pin_diameter': 0.63 * bore_mm,      # (0.6~0.7)D
        'crank_pin_length': 0.42 * bore_mm,        # (0.35~0.45)D
        'main_journal_diameter': 0.74 * bore_mm,   # (0.7~0.8)D
        'main_journal_length': 0.47 * bore_mm,     # (0.35~0.50)D
        'crank_web_thickness': 0.23 * bore_mm,     # (0.2~0.3)D
        'crank_web_width': 1.05 * bore_mm,         # (0.9~1.3)D
        'fillet_radius': 0.032 * bore_mm,          # (0.03~0.04)D
    }


# 自动计算SD195曲轴尺寸（D=95mm）
_CRANK_DIMS = calculate_crankshaft_dimensions(BORE * 1000)

# 曲柄销尺寸参数
CRANK_PIN_DIAMETER = _CRANK_DIMS['crank_pin_diameter']      # 60 mm
CRANK_PIN_LENGTH = _CRANK_DIMS['crank_pin_length']          # 40 mm
FILLET_RADIUS = _CRANK_DIMS['fillet_radius']                # 3 mm

# 曲柄臂尺寸参数
CRANK_WEB_THICKNESS = _CRANK_DIMS['crank_web_thickness']    # 22 mm
CRANK_WEB_WIDTH = _CRANK_DIMS['crank_web_width']            # 100 mm

# 材料参数（45钢）
MATERIAL_YIELD_STRENGTH = 355e6  # 屈服强度 [Pa]
MATERIAL_FATIGUE_LIMIT = 270e6   # 疲劳极限 [Pa]

# 影响系数
STRESS_CONCENTRATION_FACTOR_K = 1.8  # 应力集中系数
SIZE_FACTOR_EPSILON = 0.85           # 尺寸系数
SURFACE_FACTOR_BETA = 0.9            # 表面质量系数


# ==================== 连杆强度校核参数 ====================

# 连杆小头尺寸参数
ROD_SMALL_END_OUTER_DIA = 45.0  # 小头外径 [mm]
ROD_SMALL_END_INNER_DIA = 25.0  # 小头内径 [mm]
ROD_SMALL_END_WIDTH = 35.0      # 小头宽度 [mm]

# 连杆材料参数（45钢）
ROD_MATERIAL_YIELD = 355e6      # 屈服强度 [Pa]
ROD_ELASTIC_MODULUS = 210e9     # 弹性模量 [Pa]


# ==================== 曲轴强度校核 ====================

def calculate_crankshaft_stress(max_rod_force, max_torque):
    """
    计算曲柄销圆角处的应力
    """
    d = CRANK_PIN_DIAMETER / 1000  # 曲柄销直径 [m]
    
    # 弯曲应力计算
    arm_length = CRANK_RADIUS + (CRANK_WEB_THICKNESS / 1000) / 2
    bending_moment = max_rod_force * arm_length
    section_modulus_bending = np.pi * d**3 / 32
    nominal_bending_stress = bending_moment / section_modulus_bending
    bending_stress = nominal_bending_stress * STRESS_CONCENTRATION_FACTOR_K
    
    # 扭转应力计算
    section_modulus_torsion = np.pi * d**3 / 16
    nominal_torsion_stress = max_torque / section_modulus_torsion
    torsion_stress = nominal_torsion_stress * STRESS_CONCENTRATION_FACTOR_K
    
    # 等效应力（第三强度理论）
    equivalent_stress = np.sqrt(bending_stress**2 + 4 * torsion_stress**2)
    
    return {
        'bending_stress': bending_stress,
        'torsion_stress': torsion_stress,
        'equivalent_stress': equivalent_stress
    }


def calculate_crankshaft_safety_factor(stress_data, load_type='static'):
    """
    计算曲柄销圆角安全系数
    
    采用安全系数法：n = σ_limit / (σ_eq * K_σ / (ε_σ * β))
    """
    if load_type == 'static':
        # 静强度安全系数
        n_equivalent = MATERIAL_YIELD_STRENGTH / stress_data['equivalent_stress']
        
        return {
            'n_equivalent': n_equivalent,
            'conclusion': '合格' if n_equivalent >= 1.5 else '不合格'
        }
    
    else:  # fatigue
        # 疲劳强度安全系数（简化计算）
        # 疲劳安全系数通常要求≥1.8，高于静强度(≥1.5)
        corrected_fatigue_limit = (MATERIAL_FATIGUE_LIMIT * 
                                   SIZE_FACTOR_EPSILON * 
                                   SURFACE_FACTOR_BETA / 
                                   STRESS_CONCENTRATION_FACTOR_K)
        
        n_fatigue = corrected_fatigue_limit / stress_data['equivalent_stress']
        
        return {
            'n_fatigue': n_fatigue,
            'corrected_fatigue_limit': corrected_fatigue_limit,
            'conclusion': '合格' if n_fatigue >= 1.8 else '不合格'
        }


# ==================== 连杆强度校核 ====================

def calculate_rod_small_end_stress(max_rod_force):
    """
    计算连杆小头应力（简化模型）
    
    按均匀拉伸/压缩计算：σ = F / A
    """
    # 尺寸参数
    d_outer = ROD_SMALL_END_OUTER_DIA / 1000
    d_inner = ROD_SMALL_END_INNER_DIA / 1000
    width = ROD_SMALL_END_WIDTH / 1000
    
    # 截面积
    area = np.pi * (d_outer**2 - d_inner**2) / 4
    
    # 应力计算
    stress = abs(max_rod_force) / area
    
    return {
        'area': area,
        'tensile_stress': stress,
        'compressive_stress': stress,
        'allowable_stress': ROD_MATERIAL_YIELD / 2.5
    }


def calculate_rod_small_end_stiffness(max_rod_force):
    """
    计算连杆小头刚度（简支梁模型）
    
    简化公式：δ = F·L³ / (48·E·I)
    """
    # 尺寸参数
    d_inner = ROD_SMALL_END_INNER_DIA / 1000
    width = ROD_SMALL_END_WIDTH / 1000
    
    # 简支梁模型参数
    L = d_inner  # 跨度取内径
    h = (ROD_SMALL_END_OUTER_DIA - ROD_SMALL_END_INNER_DIA) / 1000 / 2  # 壁厚
    
    # 截面惯性矩
    I = width * h**3 / 12
    
    # 变形量（简支梁中点受集中力）
    deformation = (abs(max_rod_force) * L**3 / 
                   (48 * ROD_ELASTIC_MODULUS * I))
    
    # 许用变形量（内径的0.0015倍）
    allowable_deformation = d_inner * 0.0015
    
    return {
        'deformation': deformation,
        'allowable_deformation': allowable_deformation,
        'conclusion': '合格' if deformation <= allowable_deformation else '不合格'
    }


def calculate_rod_safety_factor(stress_data, stiffness_data):
    """
    计算连杆安全系数
    """
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
    执行强度校核计算
    """
    # 提取数据
    rod_forces = dynamics_data['rod_force']
    max_rod_force = np.max(np.abs(rod_forces))
    
    torques = dynamics_data['tangential_force'] * CRANK_RADIUS
    max_torque = np.max(torques)
    
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
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("SD195柴油机强度校核计算报告\n")
        f.write("=" * 70 + "\n\n")
        
        # 设计参数
        f.write("设计参数（经验公式确定）\n")
        f.write("-" * 70 + "\n")
        f.write(f"气缸直径 D = 95 mm\n")
        f.write(f"曲柄销直径 dp = 0.63D = {CRANK_PIN_DIAMETER:.1f} mm\n")
        f.write(f"曲柄销长度 lp = 0.42D = {CRANK_PIN_LENGTH:.1f} mm\n")
        f.write(f"曲柄臂厚度 h = 0.23D = {CRANK_WEB_THICKNESS:.1f} mm\n")
        f.write(f"曲柄臂宽度 b = 1.05D = {CRANK_WEB_WIDTH:.1f} mm\n\n")
        
        # 曲轴部分
        f.write("一、曲轴强度校核（曲柄销圆角）\n")
        f.write("-" * 70 + "\n")
        f.write(f"最大连杆力: {results['crankshaft']['max_rod_force']/1e3:.2f} kN\n")
        f.write(f"最大扭矩: {results['crankshaft']['max_torque']:.2f} N·m\n\n")
        
        stress = results['crankshaft']['stress']
        f.write("应力计算结果:\n")
        f.write(f"  弯曲应力: {stress['bending_stress']/1e6:.2f} MPa\n")
        f.write(f"  扭转应力: {stress['torsion_stress']/1e6:.2f} MPa\n")
        f.write(f"  等效应力: {stress['equivalent_stress']/1e6:.2f} MPa\n\n")
        
        static = results['crankshaft']['safety_static']
        fatigue = results['crankshaft']['safety_fatigue']
        f.write("安全系数:\n")
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
        
        stiffness = results['connecting_rod']['stiffness']
        f.write("刚度校核:\n")
        f.write(f"  变形量: {stiffness['deformation']*1e6:.4f} μm\n")
        f.write(f"  许用变形: {stiffness['allowable_deformation']*1e6:.4f} μm\n")
        f.write(f"  结论: {stiffness['conclusion']}\n\n")
        
        rod_safety = results['connecting_rod']['safety']
        f.write("安全系数:\n")
        f.write(f"  拉伸安全系数: {rod_safety['n_tensile']:.2f} (要求≥2.0)\n")
        f.write(f"  压缩安全系数: {rod_safety['n_compressive']:.2f} (要求≥2.0)\n")
        f.write(f"  综合结论: {rod_safety['overall_conclusion']}\n\n")
        
        f.write("=" * 70 + "\n")
        f.write("注意：本报告基于简化计算模型，实际设计应参考零件图纸。\n")
        f.write("=" * 70 + "\n")


if __name__ == "__main__":
    print("强度校核模块")
    print("运行 main.py 执行完整的强度校核计算")
