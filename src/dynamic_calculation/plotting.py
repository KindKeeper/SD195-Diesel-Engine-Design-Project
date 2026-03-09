"""
绘图模块
生成课程设计所需的曲线图
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置论文标准字体：中文宋体，英文Times New Roman
rcParams['font.family'] = ['Times New Roman', 'SimSun']
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.sans-serif'] = ['SimSun']
rcParams['axes.unicode_minus'] = False  # 正确显示负号


def plot_piston_motion(kinematics_data, save_path=None):
    """
    绘制附图1：活塞位移、速度、加速度曲线
    
    参数:
        kinematics_data: 运动学计算结果字典
        save_path: 保存路径
    """
    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    
    angles = kinematics_data['crank_angle']
    
    # 位移
    axes[0].plot(angles, kinematics_data['displacement'] * 1e3, 'b-', linewidth=1.5)
    axes[0].set_ylabel('位移 [mm]', fontsize=11)
    axes[0].set_title('附图1：活塞运动学曲线', fontsize=13)
    axes[0].grid(True, alpha=0.3)
    axes[0].axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    
    # 速度
    axes[1].plot(angles, kinematics_data['velocity'], 'r-', linewidth=1.5)
    axes[1].set_ylabel('速度 [m/s]', fontsize=11)
    axes[1].grid(True, alpha=0.3)
    axes[1].axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    
    # 加速度
    axes[2].plot(angles, kinematics_data['acceleration'], 'g-', linewidth=1.5)
    axes[2].set_ylabel('加速度 [m/s²]', fontsize=11)
    axes[2].set_xlabel('曲轴转角 [°]', fontsize=11)
    axes[2].grid(True, alpha=0.3)
    axes[2].axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"附图1已保存: {save_path}")
    
    return fig


def plot_forces(dynamics_data, save_path=None):
    """
    绘制附图2：气体力、惯性力、合力曲线
    
    参数:
        dynamics_data: 动力学计算结果字典
        save_path: 保存路径
    """
    fig, ax = plt.subplots(figsize=(12, 5))
    
    angles = dynamics_data['crank_angle']
    
    # 使用力的单位 kN (F[N] / 1000)
    ax.plot(angles, dynamics_data['gas_force'] / 1e3, 'b-', 
            linewidth=1.5, label='气体力(Fg)')
    ax.plot(angles, dynamics_data['inertia_force'] / 1e3, 'r-', 
            linewidth=1.5, label='往复惯性力(Fj)')
    ax.plot(angles, dynamics_data['resultant_force'] / 1e3, 'g-', 
            linewidth=2, label='合力(F)')
    
    ax.set_xlabel('曲轴转角 [°]', fontsize=11)
    ax.set_ylabel('力 [kN]', fontsize=11)
    ax.set_title('附图2：气体力、惯性力与合力曲线', fontsize=13)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"附图2已保存: {save_path}")
    
    return fig


def plot_rod_and_transverse_forces(dynamics_data, save_path=None):
    """
    绘制附图3：侧压力、连杆力、切向力、径向力曲线
    
    参数:
        dynamics_data: 动力学计算结果字典
        save_path: 保存路径
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    angles = dynamics_data['crank_angle']
    
    # 侧压力和连杆力
    axes[0].plot(angles, dynamics_data['side_force'] / 1e3, 'b-', 
                 linewidth=1.5, label='侧压力(FN)')
    axes[0].plot(angles, dynamics_data['rod_force'] / 1e3, 'r-', 
                 linewidth=1.5, label='连杆力(Fc)')
    axes[0].set_ylabel('力 [kN]', fontsize=11)
    axes[0].set_title('附图3：侧压力、连杆力、切向力与径向力曲线', fontsize=13)
    axes[0].legend(loc='upper right', fontsize=10)
    axes[0].grid(True, alpha=0.3)
    axes[0].axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    
    # 切向力和径向力
    axes[1].plot(angles, dynamics_data['tangential_force'] / 1e3, 'g-', 
                 linewidth=1.5, label='切向力(Ft)')
    axes[1].plot(angles, dynamics_data['radial_force'] / 1e3, 'm-', 
                 linewidth=1.5, label='径向力(Fr)')
    axes[1].set_xlabel('曲轴转角 [°]', fontsize=11)
    axes[1].set_ylabel('力 [kN]', fontsize=11)
    axes[1].legend(loc='upper right', fontsize=10)
    axes[1].grid(True, alpha=0.3)
    axes[1].axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"附图3已保存: {save_path}")
    
    return fig


def plot_bearing_load_polar(bearing_data, bearing_type='rod', save_path=None):
    """
    绘制轴承负荷极坐标图
    
    参数:
        bearing_data: 轴承负荷计算结果
        bearing_type: 'rod'(连杆轴颈) 或 'main'(主轴颈)
        save_path: 保存路径
    """
    from bearing_load import prepare_polar_plot_data
    
    angles, magnitudes = prepare_polar_plot_data(bearing_data, bearing_type)
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    
    # 极坐标图（使用力的单位kN）
    ax.plot(angles, magnitudes / 1e3, 'b-', linewidth=1.5)
    ax.fill(angles, magnitudes / 1e3, alpha=0.25)
    
    # 标记0°位置
    ax.plot([0, 0], [0, magnitudes.max() / 1e3], 'r--', linewidth=1, alpha=0.5)
    
    if bearing_type == 'rod':
        title = '附图4：连杆轴颈负荷极坐标图'
    else:
        title = '附图5：主轴颈负荷极坐标图'
    
    ax.set_title(title, fontsize=13, pad=20)
    ax.set_theta_zero_location('N')  # 0°在上方
    ax.set_theta_direction(-1)  # 顺时针方向
    ax.set_ylabel('负荷 [kN]', fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"{'附图4' if bearing_type == 'rod' else '附图5'}已保存: {save_path}")
    
    return fig


def generate_all_plots(kinematics_data, dynamics_data, bearing_data, output_dir=None):
    """
    一键生成所有曲线图
    
    参数:
        kinematics_data: 运动学数据
        dynamics_data: 动力学数据
        bearing_data: 轴承负荷数据
        output_dir: 输出目录（默认使用项目results/plots/）
    """
    import os
    
    # 如果未指定输出目录，使用默认路径
    if output_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'results', 'plots'))
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成各图
    plot_piston_motion(kinematics_data, 
                       save_path=os.path.join(output_dir, '附图1_位移速度加速度曲线.png'))
    plt.close()
    
    plot_forces(dynamics_data, 
                save_path=os.path.join(output_dir, '附图2_气体力_惯性力_合力曲线.png'))
    plt.close()
    
    plot_rod_and_transverse_forces(dynamics_data, 
                                   save_path=os.path.join(output_dir, '附图3_侧压力_连杆力_切向_径向力曲线.png'))
    plt.close()
    
    plot_bearing_load_polar(bearing_data, bearing_type='rod',
                            save_path=os.path.join(output_dir, '附图4_连杆轴颈负荷极坐标图.png'))
    plt.close()
    
    plot_bearing_load_polar(bearing_data, bearing_type='main',
                            save_path=os.path.join(output_dir, '附图5_主轴颈负荷极坐标图.png'))
    plt.close()
    
    print("\n所有曲线图生成完成！")


if __name__ == "__main__":
    print("绘图模块测试")
    print("运行 main.py 生成所有图表")
