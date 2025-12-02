@echo off
chcp 65001 >nul
echo ========================================
echo   GammaTool - 屏幕亮度调节工具
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo.
    pause
    exit /b 1
)

echo [信息] Python 已安装
echo.

REM 检查依赖是否安装
echo [信息] 检查依赖...
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo [警告] 依赖未安装，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
    echo [信息] 依赖安装完成
) else (
    echo [信息] 依赖已安装
)

echo.
echo [信息] 启动 GammaTool...
echo.

REM 运行程序
python src/main.py

if errorlevel 1 (
    echo.
    echo [错误] 程序运行失败
    pause
)