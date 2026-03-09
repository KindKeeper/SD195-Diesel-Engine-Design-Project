# Python 环境使用说明（Miniforge方案）

本项目使用 **Miniforge** 管理Python环境，自带Python解释器，无需单独安装Python。

---

## 前置要求

### 方案A：自行安装Miniforge（推荐）

1. 访问 https://github.com/conda-forge/miniforge/releases
2. 下载 `Miniforge3-Windows-x86_64.exe`（约100MB）
3. 双击安装，**建议勾选"Add Miniforge to my PATH environment variable"**
4. 安装完成后，打开命令行输入 `conda --version` 验证



---

## 快速开始（3步）

### 第1步：安装Miniforge（只需一次）

1. 下载 **Miniforge3-Windows-x86_64.exe**
   - 官网：https://github.com/conda-forge/miniforge/releases
   - 约100MB，下载时间取决于网速

2. 双击安装
   - **勾选"Add Miniforge to my PATH environment variable"**
   - 其他选项保持默认即可

3. 验证安装
   - 打开命令行，输入 `conda --version`
   - 显示版本号即表示安装成功

### 第2步：创建Python环境（只需一次）

双击运行：**`安装环境.bat`**

- 自动创建名为 `sd195` 的conda环境
- 自动安装 **Python 3.14** 及所需依赖包（NumPy、Matplotlib）
- 约需 3-5 分钟（取决于网速）

### 第3步：运行计算

双击运行：**`运行计算.bat`**

- 一键运行动力计算程序
- 自动生成附表（CSV格式）和附图（PNG格式）

### 第4步：查看结果

计算结果自动保存到：
- **附表1-5**：`data/processed/`（CSV格式，可用Excel/WPS直接打开打印）
- **附图1-5**：`results/plots/`（PNG格式，可直接插入Word）

---

## 文件说明

| 文件 | 用途 | 使用频率 |
|------|------|---------|
| `安装环境.bat` | 创建conda环境，安装Python 3.14和依赖包 | 只需一次 |
| `启动环境.bat` | 激活conda环境，打开命令行 | 需要调试时 |
| `运行计算.bat` | 一键运行动力计算程序 | 需要计算时 |
| `删除环境.bat` | 删除conda环境（如遇到问题需重装）| troubleshooting |

---

## 环境信息

本次配置的环境：

| 组件 | 版本 |
|------|------|
| Python | 3.14.3 |
| NumPy | 2.4.3 |
| Matplotlib | 3.10.8 |

### Python 3.14 新特性

- **改进的错误消息**：更清晰的语法错误提示
- **性能优化**：解释器启动速度提升
- **类型系统增强**：更好的类型推断支持

---

## 手动命令（供参考）

如需手动操作，可使用以下命令：

```bash
# 查看所有环境
conda env list

# 创建环境（本项目已自动完成）
conda create -n sd195 python=3.14

# 激活环境
conda activate sd195

# 退出环境
conda deactivate

# 删除环境
conda env remove -n sd195

# 运行计算
conda run -n sd195 python src/dynamic_calculation/main.py
```

---

## 常见问题

### Q1: 安装Miniforge后，命令行仍找不到conda

**解决**：
1. 检查安装时是否勾选了"Add to PATH"
2. 重新打开命令行窗口（或重启电脑）
3. 如仍不行，从开始菜单打开 "Miniforge Prompt" 使用

### Q2: 如何打开CSV文件？

**Excel/WPS**：
- 双击CSV文件即可用Excel或WPS打开
- 支持直接编辑、打印、另存为

**记事本**（查看原始数据）：
- 右键CSV文件 → 打开方式 → 记事本

### Q3: 如何打印附表？

1. 用 **Excel** 或 **WPS** 打开 `data/processed/附表1_xxx.csv`
2. 调整列宽、字体大小（建议宋体/黑体，10-12号字）
3. 页面设置 → 调整为适合A4纸
4. 直接打印或导出为PDF

### Q4: 安装依赖时网络超时

**解决**：脚本已配置清华PyPI镜像，如仍失败：
1. 配置conda使用国内镜像
2. 重新运行安装脚本

---

## 实测验证 ✅

**测试时间**：2026-03-09  
**测试环境**：Windows 11 + Anaconda(conda 25.5.1) + Python 3.14.3  
**测试状态**：✅ 全部通过

| 测试项 | 结果 |
|--------|------|
| 环境创建 | ✅ Python 3.14.3 安装成功 |
| NumPy 2.4.3 | ✅ 数值计算正常 |
| Matplotlib 3.10.8 | ✅ 图表生成正常 |
| 运动学计算 | ✅ 位移/速度/加速度计算正确 |
| 动力学计算 | ✅ 各力计算正确 |
| 轴承负荷计算 | ✅ 负荷计算正确 |
| CSV输出 | ✅ 5个附表生成正确 |
| 曲线图生成 | ✅ 5个附图生成正确 |

---

## 技术说明

- **Miniforge**：基于conda的Python发行版，使用conda-forge作为默认频道
- **conda环境**：隔离的Python运行环境，本项目使用名为 `sd195` 的环境
- **Python 3.14**：最新稳定版本，支持最新特性
- **CSV格式**：通用数据格式，Excel/WPS均可直接打开

---

## Miniforge vs Anaconda

| 特性 | Miniforge | Anaconda |
|------|-----------|----------|
| 安装包大小 | ~100MB | ~500MB |
| 安装后大小 | ~400MB | ~3GB |
| 默认频道 | conda-forge（开源）| 官方频道 |
| 商业许可 | 完全免费开源 | 部分组件需商业许可 |
| 适用场景 | 本项目推荐 | 数据科学工作站 |

Miniforge是Anaconda的轻量级替代品，完全免费，适合课程设计使用。
