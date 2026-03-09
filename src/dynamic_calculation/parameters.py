"""
SD195柴油机动力计算参数定义
来源：课程设计指导书附录1、附录3
"""

import numpy as np

# ==================== 发动机基本参数 ====================

# 额定工况参数
RATED_POWER = 8.8  # 额定功率 [kW]
RATED_SPEED = 2000  # 额定转速 [r/min]
FUEL_CONSUMPTION = 258  # 燃油消耗率 [g/(kW·h)]

# 几何参数
BORE = 95e-3  # 气缸直径 [m]
STROKE = 115e-3  # 活塞行程 [m]
CRANK_RADIUS = 57.5e-3  # 曲柄半径 [m]
ROD_LENGTH = 175e-3  # 连杆长度 [m]
LAMBDA = CRANK_RADIUS / ROD_LENGTH  # 连杆比
PISTON_OFFSET = 7e-3  # 活塞偏移 [m]

# 压缩比和燃烧室
COMPRESSION_RATIO = 19  # 压缩比（取中间值）
COMBUSTION_CHAMBER = "涡流室"

# 派生参数
PISTON_AREA = np.pi * (BORE ** 2) / 4  # 活塞顶面积 [m²]
DISPLACEMENT = PISTON_AREA * STROKE * 1e3  # 排量 [L]
MEAN_PISTON_SPEED = 2 * STROKE * RATED_SPEED / 60  # 活塞平均速度 [m/s]
MEAN_EFFECTIVE_PRESSURE = RATED_POWER * 1e3 / (DISPLACEMENT * 1e-3 * RATED_SPEED / 60 / 2) / 1e3  # 平均有效压力 [kPa]

# ==================== 质量参数 ====================

# 往复运动质量 [kg]
PISTON_MASS = 1.38  # 活塞组质量
ROD_RECIP_MASS = 0.543  # 连杆往复部分质量
RECIPROCATING_MASS = PISTON_MASS + ROD_RECIP_MASS  # 总往复质量

# 旋转运动质量 [kg]
ROD_ROT_MASS = 1.267  # 连杆旋转部分质量
CRANK_PIN_MASS = 0.563  # 曲柄销质量
CRANK_WEB_MASS = 1.15  # 曲柄臂质量
BALANCE_WEIGHT_MASS = 2.3  # 平衡重质量（每个）

# 旋转质量重心半径 [m]
CRANK_PIN_COG_R = 57.5e-3
CRANK_WEB_COG_R = 41.5e-3
BALANCE_WEIGHT_COG_R = 68.8e-3

# ==================== 计算参数 ====================

# 曲轴转角设置
CALC_STEP = 10  # 计算间隔 [度]
CALC_START = 0  # 起始角度 [度]
CALC_END = 720  # 终止角度 [度]
CRANK_ANGLES = np.arange(CALC_START, CALC_END + CALC_STEP, CALC_STEP)  # 曲轴转角数组 [度]

# 角速度计算 [rad/s]
ANGULAR_VELOCITY = 2 * np.pi * RATED_SPEED / 60

# ==================== 输出参数 ====================

def print_engine_parameters():
    """打印发动机参数信息"""
    print("=" * 60)
    print("SD195柴油机参数")
    print("=" * 60)
    print(f"额定功率: {RATED_POWER} kW")
    print(f"额定转速: {RATED_SPEED} r/min")
    print(f"气缸直径: {BORE*1e3:.1f} mm")
    print(f"活塞行程: {STROKE*1e3:.1f} mm")
    print(f"曲柄半径: {CRANK_RADIUS*1e3:.1f} mm")
    print(f"连杆长度: {ROD_LENGTH*1e3:.1f} mm")
    print(f"连杆比 λ: {LAMBDA:.4f}")
    print(f"活塞顶面积: {PISTON_AREA*1e4:.2f} cm²")
    print(f"排量: {DISPLACEMENT:.3f} L")
    print(f"平均有效压力: {MEAN_EFFECTIVE_PRESSURE:.1f} kPa")
    print("-" * 60)
    print(f"往复质量: {RECIPROCATING_MASS:.3f} kg")
    print(f"角速度: {ANGULAR_VELOCITY:.2f} rad/s")
    print(f"计算范围: {CALC_START}° ~ {CALC_END}°, 间隔 {CALC_STEP}°")
    print("=" * 60)


if __name__ == "__main__":
    print_engine_parameters()
