@echo off
chcp 65001 >nul
echo ====================================
echo 启动前端服务
echo ====================================
echo.

REM 添加 Node.js 到 PATH（如果存在）
if exist "D:\nodejs\node.exe" (
    set PATH=%PATH%;D:\nodejs
    echo [信息] 已添加 D:\nodejs 到 PATH
)

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Node.js
    echo 请确保 Node.js 已安装，或修改此脚本中的路径
    pause
    exit /b 1
)

echo [信息] Node.js 版本:
node --version
echo [信息] npm 版本:
npm --version
echo.

cd frontend

REM 检查依赖
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
echo [启动] 启动前端开发服务器...
echo 前端地址: http://localhost:3000
echo.
npm run dev

pause

