"""
SD195柴油机动力计算主程序

功能：一键完成全部计算并输出结果
"""

import os
import sys
import io
import numpy as np

# 修复Windows控制台UTF-8编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 获取项目根目录（脚本所在目录的上两级）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))

# 添加模块路径
sys.path.insert(0, SCRIPT_DIR)

from parameters import print_engine_parameters, CRANK_RADIUS, ANGULAR_VELOCITY, RATED_SPEED
from kinematics import calculate_all_kinematics
from dynamics import calculate_all_dynamics
from bearing_load import calculate_all_bearing_loads
from plotting import generate_all_plots
from strength_check import perform_strength_check, save_strength_report
from io_utils import (
    load_pressure_data,
    save_kinematics_to_csv,
    save_dynamics_to_csv,
    save_bearing_load_to_csv,
    create_sample_data_files
)


def check_data_files():
    """检查必要的输入数据文件是否存在"""
    data_dir = os.path.join(PROJECT_ROOT, 'data', 'original')
    required_files = [
        'engine_specifications_SD195.csv',
        'pressure_data_SD195.csv',
        'mass_parameters_SD195.csv'
    ]
    
    missing = []
    for f in required_files:
        if not os.path.exists(os.path.join(data_dir, f)):
            missing.append(f)
    
    return missing


def run_calculation():
    """
    执行完整计算流程
    
    流程：
    1. 检查输入数据文件
    2. 打印发动机参数
    3. 运动学计算
    4. 动力学计算
    5. 轴承负荷计算
    6. 保存计算结果（CSV格式）
    7. 生成曲线图
    8. 能量验证
    9. 强度校核计算
    """
    print("=" * 70)
    print("SD195柴油机动力计算程序")
    print("=" * 70)
    
    # 检查输入文件
    print("\n[1/9] 检查输入数据文件...")
    missing = check_data_files()
    if missing:
        print(f"警告：以下文件不存在: {missing}")
        print("创建示例数据文件...")
        create_sample_data_files()
    else:
        print("所有输入文件已就绪")
    
    # 打印参数
    print("\n[2/9] 发动机参数:")
    print_engine_parameters()
    
    # 加载压力数据
    print("\n[3/9] 运动学计算...")
    kinematics_data = calculate_all_kinematics()
    print(f"  计算完成: {len(kinematics_data['crank_angle'])} 个数据点")
    
    print("\n[4/9] 动力学计算...")
    pressure_data = load_pressure_data(
        os.path.join(PROJECT_ROOT, 'data', 'original', 'pressure_data_SD195.csv')
    )
    dynamics_data = calculate_all_dynamics(pressure_data)
    print(f"  计算完成: 气体力、惯性力、合力、连杆力、侧向力、切向力、径向力")
    
    print("\n[5/9] 轴承负荷计算...")
    bearing_data = calculate_all_bearing_loads(pressure_data)
    print(f"  计算完成: 连杆轴颈负荷、主轴颈负荷")
    
    # 保存结果
    print("\n[6/9] 保存计算结果...")
    
    # 创建输出目录
    tables_dir = os.path.join(PROJECT_ROOT, 'results', 'tables')
    calculations_dir = os.path.join(PROJECT_ROOT, 'results', 'calculations')
    plots_dir = os.path.join(PROJECT_ROOT, 'results', 'plots')
    os.makedirs(tables_dir, exist_ok=True)
    os.makedirs(calculations_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)
    
    # 保存为CSV（附表1-5）
    save_kinematics_to_csv(kinematics_data,
                           os.path.join(tables_dir, '附表1_活塞运动学数据.csv'))
    
    save_dynamics_to_csv(dynamics_data,
                         os.path.join(tables_dir, '附表2_气体力与合力.csv'))
    
    # 附表3：连杆力及侧压力（使用压力单位MPa）
    rod_data = {
        'crank_angle': dynamics_data['crank_angle'],
        'rod_force': dynamics_data['rod_force'],
        'side_force': dynamics_data['side_force'],
        'tangential_force': dynamics_data['tangential_force'],
        'radial_force': dynamics_data['radial_force']
    }
    save_dynamics_to_csv(rod_data,
                         os.path.join(tables_dir, '附表3_连杆及侧压力.csv'),
                         use_pressure_unit=False)  # 使用力的单位kN
    
    # 附表5：扭矩曲线数据
    from io_utils import save_torque_to_csv
    save_torque_to_csv(dynamics_data,
                       os.path.join(tables_dir, '附表5_扭矩曲线数据.csv'))
    
    save_bearing_load_to_csv(bearing_data, 'rod',
                             os.path.join(tables_dir, '附表4_连杆轴颈负荷.csv'),
                             use_pressure_unit=False)  # 使用力的单位kN
    
    save_bearing_load_to_csv(bearing_data, 'main',
                             os.path.join(tables_dir, '附表6_主轴颈负荷.csv'),
                             use_pressure_unit=False)  # 使用力的单位kN
    
    # 生成图表
    print("\n[7/9] 生成曲线图...")
    generate_all_plots(kinematics_data, dynamics_data, bearing_data)
    
    # 能量验证
    print("\n[8/9] 能量验证...")
    # 计算指示功：扭矩 × 角度 的积分
    tangential_forces = dynamics_data['tangential_force']
    angles_rad = np.radians(dynamics_data['crank_angle'])
    
    # 扭矩 = 切向力 × 曲柄半径
    torque = tangential_forces * CRANK_RADIUS
    
    # 数值积分（梯形法）计算指示功
    indicated_work = np.trapezoid(torque, angles_rad)
    
    # 指示功率 = 指示功 × 转速 / 120（四冲程，每2转做功一次）
    indicated_power = indicated_work * RATED_SPEED / 120
    
    # 对比额定功率（考虑机械效率约0.75-0.85）
    rated_power_watts = 8.8e3
    estimated_mechanical_efficiency = 0.8
    expected_indicated_power = rated_power_watts / estimated_mechanical_efficiency
    
    power_error = abs(abs(indicated_power) - expected_indicated_power) / expected_indicated_power * 100
    
    print(f"  指示功: {indicated_work:.2f} J/循环")
    print(f"  指示功率: {abs(indicated_power)/1000:.2f} kW")
    print(f"  额定功率: {rated_power_watts/1000:.2f} kW")
    print(f"  估计机械效率: {estimated_mechanical_efficiency*100:.0f}%")
    print(f"  预期指示功率: {expected_indicated_power/1000:.2f} kW")
    print(f"  偏差: {power_error:.2f}%")
    
    if power_error > 20:
        print(f"  ⚠️ 警告: 功率偏差较大")
        print(f"     可能原因: 使用示例数据、气体压力数据异常或计算误差")
    else:
        print(f"  ✅ 能量验证通过")
    
    # 强度校核计算
    print("\n[9/9] 强度校核计算...")
    strength_results = perform_strength_check(dynamics_data, bearing_data)
    
    # 保存强度校核报告
    save_strength_report(strength_results,
                         os.path.join(calculations_dir, '强度校核报告.txt'))
    
    print("  曲轴：曲柄销圆角安全系数计算完成")
    print("  连杆：小头强度与刚度校核完成")
    
    print("\n" + "=" * 70)
    print("计算完成！")
    print("=" * 70)
    print("\n输出文件:")
    print("  📊 附表1-6 (CSV格式): results/tables/")
    print("     - 附表1: 活塞运动学数据")
    print("     - 附表2: 气体力与合力")
    print("     - 附表3: 连杆力及侧压力")
    print("     - 附表4: 连杆轴颈负荷")
    print("     - 附表5: 扭矩曲线数据")
    print("     - 附表6: 主轴颈负荷")
    print("     - 可用Excel直接打开并打印")
    print("\n  📝 强度校核报告: results/calculations/")
    print("     - 包含曲轴和连杆的安全系数计算")
    print("\n  📈 附图1-5 (PNG格式): results/plots/")
    print("     - 可直接插入Word文档")
    print("=" * 70)


def main():
    """主函数"""
    try:
        run_calculation()
    except FileNotFoundError as e:
        print(f"\n❌ 文件错误: {e}")
        print("请检查数据文件是否存在，或运行程序创建示例数据。")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ 数据错误: {e}")
        print("请检查输入数据的格式和数值范围。")
        sys.exit(1)
    except ZeroDivisionError as e:
        print(f"\n❌ 计算错误: 发生除零错误")
        print("请检查参数设置，特别是几何参数（如连杆长度不能为零）。")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 未预期的错误: {e}")
        print("错误详情:")
        import traceback
        traceback.print_exc()
        print("\n如果问题持续存在，请检查:")
        print("  1. Python版本是否兼容（推荐3.10+）")
        print("  2. 依赖包是否正确安装（numpy, matplotlib）")
        print("  3. 项目文件是否完整")
        sys.exit(1)


if __name__ == "__main__":
    main()
