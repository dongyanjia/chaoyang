@echo off
chcp 65001 >nul
echo ========================================
echo Git 推送到 GitHub 脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/5] 检查 Git 状态...
git status --short
echo.

echo [2/5] 添加所有更改...
git add .
if %errorlevel% neq 0 (
    echo 错误: git add 失败
    echo 请先运行 fix_git_lock.ps1 修复锁文件问题
    pause
    exit /b 1
)
echo.

echo [3/5] 提交更改...
git commit -m "Add tag management feature and update project files"
if %errorlevel% neq 0 (
    echo 错误: git commit 失败
    pause
    exit /b 1
)
echo.

echo [4/5] 检查远程仓库...
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo 添加远程仓库...
    git remote add origin https://github.com/dongyanjia/chaoyang.git
    if %errorlevel% neq 0 (
        echo 错误: 添加远程仓库失败
        pause
        exit /b 1
    )
) else (
    echo 更新远程仓库地址...
    git remote set-url origin https://github.com/dongyanjia/chaoyang.git
)
echo.

echo [5/5] 推送到 GitHub...
git push -u origin master
if %errorlevel% neq 0 (
    echo 错误: 推送失败
    echo 如果这是第一次推送，可能需要先拉取远程仓库
    echo 或者检查 GitHub 认证设置
    pause
    exit /b 1
)

echo.
echo ========================================
echo 完成！代码已成功推送到 GitHub
echo ========================================
pause
