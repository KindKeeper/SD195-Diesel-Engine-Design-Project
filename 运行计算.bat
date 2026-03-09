@echo off
chcp 65001 >nul
echo ========================================
echo SD195柴油机设计项目 - 一键运行计算
echo ========================================
echo.

REM 设置Python IO编码
set PYTHONIOENCODING=utf-8

REM 检查conda
conda --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到conda/Miniforge
    echo 请先运行 "安装环境.bat" 进行安装
    pause
    exit /b 1
)

REM 检查环境
conda env list | findstr "sd195" >nul
if %errorlevel% neq 0 (
    echo [提示] 环境 sd195 不存在，请先运行 "安装环境.bat"
    pause
    exit /b 1
)

echo 正在运行计算程序...
echo.

REM 使用conda run直接运行（避免激活问题）
conda run -n sd195 --live-stream env PYTHONIOENCODING=utf-8 python src/dynamic_calculation/main.py

echo.
echo ========================================
echo 计算完成！
echo.
echo 输出文件位置:
echo   results/
echo   ├── tables/          附表1-5 (CSV格式)
echo   ├── calculations/    强度校核报告 (TXT格式)
echo   └── plots/           附图1-5 (PNG格式)
echo.
echo 提示: CSV文件可用Excel/WPS直接打开打印
echo ========================================
pause
