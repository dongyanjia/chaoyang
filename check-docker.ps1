# Docker 环境检查脚本

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Docker 环境检查" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker 是否安装
Write-Host "1. 检查 Docker 安装..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "   [OK] Docker 已安装: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "   [错误] Docker 未安装或不在 PATH 中" -ForegroundColor Red
    exit 1
}

# 检查 Docker Compose
Write-Host ""
Write-Host "2. 检查 Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker compose version 2>&1
    Write-Host "   [OK] Docker Compose 已安装: $composeVersion" -ForegroundColor Green
} catch {
    try {
        $composeVersion = docker-compose --version 2>&1
        Write-Host "   [OK] Docker Compose 已安装: $composeVersion" -ForegroundColor Green
    } catch {
        Write-Host "   [错误] Docker Compose 未安装" -ForegroundColor Red
        exit 1
    }
}

# 检查 Docker 是否运行
Write-Host ""
Write-Host "3. 检查 Docker 服务状态..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] Docker 服务正在运行" -ForegroundColor Green
    } else {
        Write-Host "   [错误] Docker 服务未运行或无法访问" -ForegroundColor Red
        Write-Host "   请确保 Docker Desktop 已启动" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "   [错误] 无法连接到 Docker 服务" -ForegroundColor Red
    Write-Host "   请确保 Docker Desktop 已启动" -ForegroundColor Yellow
    exit 1
}

# 检查 Docker 镜像
Write-Host ""
Write-Host "4. 检查 Docker 镜像..." -ForegroundColor Yellow
try {
    $images = docker images 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] 可以访问 Docker 镜像" -ForegroundColor Green
    }
} catch {
    Write-Host "   [警告] 无法列出 Docker 镜像" -ForegroundColor Yellow
}

# 检查端口占用
Write-Host ""
Write-Host "5. 检查端口占用..." -ForegroundColor Yellow
$ports = @(80, 8000, 8030, 8040)
$portOccupied = $false
foreach ($port in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Host "   [警告] 端口 $port 已被占用" -ForegroundColor Yellow
        $portOccupied = $true
    } else {
        Write-Host "   [OK] 端口 $port 可用" -ForegroundColor Green
    }
}

# 检查 docker-compose.yml
Write-Host ""
Write-Host "6. 检查配置文件..." -ForegroundColor Yellow
if (Test-Path "docker-compose.yml") {
    Write-Host "   [OK] docker-compose.yml 存在" -ForegroundColor Green
} else {
    Write-Host "   [错误] docker-compose.yml 不存在" -ForegroundColor Red
    exit 1
}

if (Test-Path "backend\Dockerfile") {
    Write-Host "   [OK] backend\Dockerfile 存在" -ForegroundColor Green
} else {
    Write-Host "   [错误] backend\Dockerfile 不存在" -ForegroundColor Red
}

if (Test-Path "frontend\Dockerfile") {
    Write-Host "   [OK] frontend\Dockerfile 存在" -ForegroundColor Green
} else {
    Write-Host "   [错误] frontend\Dockerfile 不存在" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
if ($portOccupied) {
    Write-Host "检查完成，但有端口被占用" -ForegroundColor Yellow
    Write-Host "请修改 docker-compose.yml 中的端口映射" -ForegroundColor Yellow
} else {
    Write-Host "环境检查通过！可以开始部署" -ForegroundColor Green
    Write-Host ""
    Write-Host "下一步操作:" -ForegroundColor Cyan
    Write-Host "  docker compose build" -ForegroundColor White
    Write-Host "  docker compose up -d" -ForegroundColor White
}
Write-Host "==========================================" -ForegroundColor Cyan
