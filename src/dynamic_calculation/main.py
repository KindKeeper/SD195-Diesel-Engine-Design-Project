"""
SD195柴油机动力计算主程序

功能：一键完成全部计算并输出结果
"""

import os
import sys
import io

# 修复Windows控制台UTF-8编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 获取项目根目录（脚本所在目录的上两级）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))

# 添加模块路径
sys.path.insert(0, SCRIPT_DIR)

from parameters import print_engine_parameters
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
    1. 打印发动机参数
    2. 运动学计算
    3. 动力学计算
    4. 轴承负荷计算
    5. 保存计算结果（CSV格式）
    6. 生成曲线图
    """
    print("=" * 70)
    print("SD195柴油机动力计算程序")
    print("=" * 70)
    
    # 检查输入文件
    print("\n[1/6] 检查输入数据文件...")
    missing = check_data_files()
    if missing:
        print(f"警告：以下文件不存在: {missing}")
        print("创建示例数据文件...")
        create_sample_data_files()
    else:
        print("所有输入文件已就绪")
    
    # 打印参数
    print("\n[2/6] 发动机参数:")
    print_engine_parameters()
    
    # 加载压力数据
    print("\n[3/6] 运动学计算...")
    kinematics_data = calculate_all_kinematics()
    print(f"  计算完成: {len(kinematics_data['crank_angle'])} 个数据点")
    
    print("\n[4/6] 动力学计算...")
    pressure_data = load_pressure_data(
        os.path.join(PROJECT_ROOT, 'data', 'original', 'pressure_data_SD195.csv')
    )
    dynamics_data = calculate_all_dynamics(pressure_data)
    print(f"  计算完成: 气体力、惯性力、合力、连杆力、侧向力、切向力、径向力")
    
    print("\n[5/6] 轴承负荷计算...")
    bearing_data = calculate_all_bearing_loads(pressure_data)
    print(f"  计算完成: 连杆轴颈负荷、主轴颈负荷")
    
    # 保存结果
    print("\n[6/6] 保存计算结果...")
    
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
    
    # 附表3：连杆力及侧压力
    rod_data = {
        'crank_angle': dynamics_data['crank_angle'],
        'rod_force': dynamics_data['rod_force'],
        'side_force': dynamics_data['side_force'],
        'tangential_force': dynamics_data['tangential_force'],
        'radial_force': dynamics_data['radial_force']
    }
    save_dynamics_to_csv(rod_data,
                         os.path.join(tables_dir, '附表3_连杆及侧压力.csv'))
    
    save_bearing_load_to_csv(bearing_data, 'rod',
                             os.path.join(tables_dir, '附表4_连杆轴颈负荷.csv'))
    
    save_bearing_load_to_csv(bearing_data, 'main',
                             os.path.join(tables_dir, '附表5_主轴颈负荷.csv'))
    
    # 生成图表
    print("\n[7/7] 生成曲线图...")
    generate_all_plots(kinematics_data, dynamics_data, bearing_data)
    
    # 强度校核计算
    print("\n[8/8] 强度校核计算...")
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
    print("  📊 附表1-5 (CSV格式): results/tables/")
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
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
