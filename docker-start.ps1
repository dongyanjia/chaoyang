# Docker 快速启动脚本 (PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "全国流感人群流动监测系统 - Docker 启动脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker 是否安装
try {
    docker --version | Out-Null
} catch {
    Write-Host "错误: 未找到 Docker，请先安装 Docker" -ForegroundColor Red
    exit 1
}

# 检查 Docker Compose 是否安装
$dockerComposeCmd = $null
try {
    docker compose version | Out-Null
    $dockerComposeCmd = "docker compose"
} catch {
    try {
        docker-compose --version | Out-Null
        $dockerComposeCmd = "docker-compose"
    } catch {
        Write-Host "错误: 未找到 Docker Compose，请先安装 Docker Compose" -ForegroundColor Red
        exit 1
    }
}

Write-Host "1. 构建 Docker 镜像..." -ForegroundColor Yellow
& $dockerComposeCmd.Split(' ') build

Write-Host ""
Write-Host "2. 启动所有服务..." -ForegroundColor Yellow
& $dockerComposeCmd.Split(' ') up -d

Write-Host ""
Write-Host "3. 等待服务启动（30秒）..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "4. 检查服务状态..." -ForegroundColor Yellow
& $dockerComposeCmd.Split(' ') ps

Write-Host ""
Write-Host "5. 初始化数据库表结构..." -ForegroundColor Yellow
try {
    & $dockerComposeCmd.Split(' ') exec -T backend python init_doris_tables.py
} catch {
    Write-Host "数据库初始化可能已存在，跳过" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "启动完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "访问地址:" -ForegroundColor Cyan
Write-Host "  前端: http://localhost"
Write-Host "  后端API: http://localhost:8000"
Write-Host "  Doris FE: http://localhost:8030"
Write-Host ""
Write-Host "常用命令:" -ForegroundColor Cyan
Write-Host "  查看日志: $dockerComposeCmd logs -f"
Write-Host "  停止服务: $dockerComposeCmd down"
Write-Host "  查看状态: $dockerComposeCmd ps"
Write-Host ""
Write-Host "初始化数据（可选）:" -ForegroundColor Cyan
Write-Host "  初始化标签: $dockerComposeCmd exec backend python init_tags.py"
Write-Host "  初始化测试数据: $dockerComposeCmd exec backend python init_database.py --people 100"
Write-Host ""
