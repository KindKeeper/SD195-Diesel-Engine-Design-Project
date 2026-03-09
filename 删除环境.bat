@echo off
chcp 65001 >nul
echo ========================================
echo SD195柴油机设计项目 - 删除conda环境
echo ========================================
echo.

REM 检查conda
conda --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到conda
    pause
    exit /b 1
)

echo [警告] 此操作将删除conda环境 sd195，已安装的所有包将被清除
echo.
set /p confirm="确定要删除吗？(输入 yes 确认): "

if /i "%confirm%"=="yes" (
    conda env remove -n sd195 -y
    if %errorlevel%==0 (
        echo [成功] 环境 sd195 已删除
    ) else (
        echo [提示] 环境删除失败或不存在
    )
) else (
    echo 操作已取消
)

echo.
pause
