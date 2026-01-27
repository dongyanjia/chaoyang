@echo off
chcp 65001 >nul
echo ====================================
echo 全国流感人群流动监测系统
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

REM 检查Node.js
REM 尝试使用默认路径
node --version >nul 2>&1
if errorlevel 1 (
    REM 尝试使用 D:\nodejs 路径
    if exist "D:\nodejs\node.exe" (
        set PATH=%PATH%;D:\nodejs
        node --version >nul 2>&1
        if errorlevel 1 (
            echo [错误] 未检测到Node.js，请先安装Node.js
            echo 下载地址: https://nodejs.org/
            echo.
            echo 安装完成后，请重新运行此脚本
            pause
            exit /b 1
        )
    ) else (
        echo [错误] 未检测到Node.js，请先安装Node.js
        echo 下载地址: https://nodejs.org/
        echo.
        echo 安装完成后，请重新运行此脚本
        pause
        exit /b 1
    )
)

REM 检查后端依赖
echo [检查] 检查后端依赖...
cd backend
if not exist "venv\" (
    echo [提示] 建议使用虚拟环境，正在检查依赖...
)
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装后端依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 后端依赖安装失败
        pause
        exit /b 1
    )
)

REM 检查前端依赖
echo [检查] 检查前端依赖...
cd ../frontend
if not exist "node_modules\" (
    echo [安装] 正在安装前端依赖...
    call npm install
    if errorlevel 1 (
        echo [错误] 前端依赖安装失败
        pause
        exit /b 1
    )
)

echo.
echo [1/2] 启动后端服务...
cd ../backend
start "后端服务" cmd /k "python run.py"
timeout /t 3 /nobreak >nul

echo [2/2] 启动前端服务...
cd ../frontend
REM 确保 Node.js 在 PATH 中
if exist "D:\nodejs\node.exe" (
    set PATH=%PATH%;D:\nodejs
)
start "前端服务" cmd /k "npm run dev"
timeout /t 2 /nobreak >nul

echo.
echo ====================================
echo 服务启动完成！
echo 前端地址: http://localhost:3000
echo 后端地址: http://localhost:8000
echo ====================================
echo.
echo 提示: 关闭服务窗口即可停止服务
pause

