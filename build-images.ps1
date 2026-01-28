# 构建前后端镜像脚本

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "构建前后端 Docker 镜像" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker 是否可用
Write-Host "1. 检查 Docker 环境..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   [错误] Docker Desktop 未运行或无法访问" -ForegroundColor Red
        Write-Host ""
        Write-Host "请执行以下操作:" -ForegroundColor Yellow
        Write-Host "  1. 打开 Docker Desktop 应用程序" -ForegroundColor White
        Write-Host "  2. 等待 Docker Desktop 完全启动（状态栏显示 'Docker Desktop is running'）" -ForegroundColor White
        Write-Host "  3. 重新运行此脚本" -ForegroundColor White
        Write-Host ""
        exit 1
    }
    Write-Host "   [OK] Docker 环境正常" -ForegroundColor Green
} catch {
    Write-Host "   [错误] 无法连接到 Docker: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2. 构建后端镜像..." -ForegroundColor Yellow
docker compose build backend
if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] 后端镜像构建成功" -ForegroundColor Green
} else {
    Write-Host "   [错误] 后端镜像构建失败" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "3. 构建前端镜像..." -ForegroundColor Yellow
docker compose build frontend
if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] 前端镜像构建成功" -ForegroundColor Green
} else {
    Write-Host "   [错误] 前端镜像构建失败" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "镜像构建完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "查看镜像:" -ForegroundColor Cyan
Write-Host "  docker images | findstr chaoyang" -ForegroundColor White
Write-Host ""
Write-Host "下一步操作:" -ForegroundColor Cyan
Write-Host "  docker compose up -d" -ForegroundColor White
Write-Host ""
