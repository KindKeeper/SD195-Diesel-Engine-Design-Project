# SD195柴油机动力计算程序

## 程序结构

```
src/dynamic_calculation/
├── main.py           # 主程序入口
├── parameters.py     # 发动机参数定义
├── kinematics.py     # 运动学计算（位移、速度、加速度）
├── dynamics.py       # 动力学计算（各力计算）
├── bearing_load.py   # 轴承负荷计算
├── strength_check.py # 强度校核计算（曲轴、连杆）
├── plotting.py       # 绘图模块
├── io_utils.py       # 输入输出工具
├── requirements.txt  # Python依赖
└── README.md         # 本文件
```

## 使用方法

### 1. 安装依赖

```bash
cd src/dynamic_calculation
pip install -r requirements.txt
```

### 2. 准备数据

确保 `data/original/` 目录下有：
- `engine_specifications_SD195.csv` - 发动机规格
- `pressure_data_SD195.csv` - 气体压力数据
- `mass_parameters_SD195.csv` - 质量参数

如果缺少数据文件，程序会自动创建示例文件（需要替换为实际数据）。

### 3. 运行计算

```bash
python main.py
```

程序将自动完成：
- 运动学计算
- 动力学计算
- 轴承负荷计算
- 保存计算结果到 `data/processed/`
- 生成曲线图到 `results/plots/`

## 各模块说明

### parameters.py
- 定义所有发动机参数
- 提供参数打印函数

### kinematics.py
- `calculate_piston_displacement()` - 活塞位移
- `calculate_piston_velocity()` - 活塞速度
- `calculate_piston_acceleration()` - 活塞加速度
- `calculate_all_kinematics()` - 批量计算

### dynamics.py
- `calculate_inertia_force()` - 往复惯性力
- `calculate_gas_force()` - 气体作用力
- `calculate_resultant_force()` - 合力
- `calculate_rod_force()` - 连杆力
- `calculate_side_force()` - 侧向力
- `calculate_tangential_force()` - 切向力
- `calculate_radial_force()` - 径向力

### bearing_load.py
- `calculate_rod_bearing_load()` - 连杆轴颈负荷
- `calculate_main_bearing_load()` - 主轴颈负荷
- `prepare_polar_plot_data()` - 极坐标图数据准备

### strength_check.py
- `calculate_crankshaft_stress()` - 曲柄销圆角应力计算
- `calculate_crankshaft_safety_factor()` - 曲轴安全系数计算
- `calculate_rod_small_end_stress()` - 连杆小头应力计算
- `calculate_rod_small_end_stiffness()` - 连杆小头刚度计算
- `perform_strength_check()` - 执行完整强度校核
- `save_strength_report()` - 保存强度校核报告

### plotting.py
- `plot_piston_motion()` - 附图1
- `plot_forces()` - 附图2
- `plot_rod_and_transverse_forces()` - 附图3
- `plot_bearing_load_polar()` - 附图4、附图5

### io_utils.py
- `load_pressure_data()` - 加载压力数据
- `save_to_csv()` - 保存CSV
- `create_sample_data_files()` - 创建示例数据

## 输出文件

### 数据表格（results/tables/）
- `附表1_活塞运动学数据.csv` - 活塞位移、速度、加速度
- `附表2_气体力与合力.csv` - 气体力、惯性力、合力
- `附表3_连杆及侧压力.csv` - 连杆力、侧压力、切向力、径向力
- `附表4_连杆轴颈负荷.csv` - 连杆轴颈负荷
- `附表5_主轴颈负荷.csv` - 主轴颈负荷

### 计算报告（results/calculations/）
- `强度校核报告.txt` - 曲轴和连杆强度校核计算结果

### 曲线图（results/plots/）
- `附图1_位移速度加速度曲线.png`
- `附图2_气体力_惯性力_合力曲线.png`
- `附图3_侧压力_连杆力_切向_径向力曲线.png`
- `附图4_连杆轴颈负荷极坐标图.png`
- `附图5_主轴颈负荷极坐标图.png`
