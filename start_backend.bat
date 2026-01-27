@echo off
chcp 65001 >nul
echo ====================================
echo 启动后端服务
echo ====================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

cd backend

REM 检查依赖
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装后端依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 后端依赖安装失败
        pause
        exit /b 1
    )
) else (
    REM 检查pandas（Excel导入功能必需）
    pip show pandas >nul 2>&1
    if errorlevel 1 (
        echo [安装] 检测到缺少pandas，正在安装后端依赖...
        pip install -r requirements.txt
        if errorlevel 1 (
            echo [错误] 后端依赖安装失败
            pause
            exit /b 1
        )
    )
)

echo.
echo [启动] 启动后端服务...
echo 后端API地址: http://localhost:8000
echo.
python run.py

pause

