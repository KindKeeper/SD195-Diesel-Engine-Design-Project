@echo off
chcp 65001 >nul
echo ========================================
echo SD195柴油机设计项目 - 启动Miniforge环境
echo ========================================
echo.

REM 检查conda
conda --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到conda/Miniforge
    echo 请先运行 "安装环境.bat" 进行安装
    pause
    exit /b 1
)

REM 检查环境是否存在
conda env list | findstr "sd195" >nul
if %errorlevel% neq 0 (
    echo [提示] 环境 sd195 不存在，请先运行 "安装环境.bat"
    pause
    exit /b 1
)

echo [1/2] 正在激活conda环境 sd195...
call conda activate sd195
if errorlevel 1 (
    echo [错误] 环境激活失败
    echo 尝试使用完整路径激活...
    call C:\Users\%USERNAME%\.conda\envs\sd195\Scripts\activate sd195
)

echo [2/2] 环境已激活！
echo.
echo 当前Python版本:
python --version
echo.
echo ========================================
echo 可用命令:
echo   python src/dynamic_calculation/main.py  - 运行动力计算
echo   python                                   - 进入Python交互模式
echo   conda deactivate                         - 退出环境
echo ========================================
echo.

REM 保持窗口打开
cmd /k
