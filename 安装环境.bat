@echo off
chcp 65001 >nul
echo ========================================
echo SD195柴油机设计项目 - Miniforge环境安装
echo ========================================
echo.

REM 检查是否已有conda
conda --version >nul 2>&1
if errorlevel 1 (
    echo [提示] 未检测到conda/Miniforge
    echo.
    echo 请按以下步骤安装Miniforge：
    echo   1. 访问 https://github.com/conda-forge/miniforge/releases
    echo   2. 下载 Miniforge3-Windows-x86_64.exe
    echo   3. 双击安装，建议勾选"Add to PATH"
    echo   4. 安装完成后重新运行此脚本
    echo.

    pause
    exit /b 1
)

echo [1/4] 检测到conda版本:
conda --version
echo.

REM 创建conda环境
echo [2/4] 正在创建conda环境（sd195）...
conda env list | findstr "sd195" >nul
if %errorlevel%==0 (
    echo [提示] 环境 sd195 已存在，跳过创建步骤
) else (
    conda create -n sd195 python=3.14 -y
    if errorlevel 1 (
        echo [错误] 创建环境失败
        pause
        exit /b 1
    )
    echo [成功] conda环境创建完成
)
echo.

REM 安装依赖
echo [3/4] 正在安装Python依赖包...
conda run -n sd195 pip install numpy matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple

if errorlevel 1 (
    echo.
    echo [错误] 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)

echo.
echo [4/4] 验证安装...
conda run -n sd195 python -c "import numpy, matplotlib; print('所有依赖安装成功')"

echo.
echo ========================================
echo [成功] Miniforge环境配置完成！
echo ========================================
echo.
echo 环境名称: sd195
echo Python版本: 3.14
echo 已安装: NumPy, Matplotlib
echo.
echo 使用方法:
echo   1. 双击运行 "启动环境.bat"
echo   2. 或双击 "运行计算.bat" 直接运行计算
echo.
pause
