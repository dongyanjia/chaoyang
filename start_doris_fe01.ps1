# 启动 doris-fe-01 的诊断和修复脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Doris FE-01 启动诊断和修复" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 步骤 1: 检查容器状态
Write-Host "`n[1] 检查 doris-fe-01 容器状态..." -ForegroundColor Yellow
$container = docker ps -a --filter "name=doris-fe-01" --format "{{.Names}} {{.Status}}"
if ($container) {
    Write-Host "容器状态: $container" -ForegroundColor White
} else {
    Write-Host "容器不存在，将创建新容器" -ForegroundColor Red
}

# 步骤 2: 查看日志
Write-Host "`n[2] 查看 doris-fe-01 日志（最后50行）..." -ForegroundColor Yellow
docker logs doris-fe-01 --tail 50 2>&1 | Out-String

# 步骤 3: 检查端口占用
Write-Host "`n[3] 检查端口占用..." -ForegroundColor Yellow
$port8031 = netstat -ano | findstr ":8031"
$port9031 = netstat -ano | findstr ":9031"
if ($port8031) {
    Write-Host "端口 8031 被占用:" -ForegroundColor Red
    Write-Host $port8031
} else {
    Write-Host "端口 8031 可用" -ForegroundColor Green
}
if ($port9031) {
    Write-Host "端口 9031 被占用:" -ForegroundColor Red
    Write-Host $port9031
} else {
    Write-Host "端口 9031 可用" -ForegroundColor Green
}

# 步骤 4: 检查网络
Write-Host "`n[4] 检查网络配置..." -ForegroundColor Yellow
docker network ls | Select-String "doris"

# 步骤 5: 尝试启动
Write-Host "`n[5] 尝试启动 doris-fe-01..." -ForegroundColor Yellow
docker-compose up -d docker-fe-01

# 步骤 6: 等待并检查
Write-Host "`n[6] 等待5秒后检查状态..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
$status = docker ps --filter "name=doris-fe-01" --format "{{.Names}} {{.Status}}"
if ($status) {
    Write-Host "✅ doris-fe-01 已启动: $status" -ForegroundColor Green
} else {
    Write-Host "❌ doris-fe-01 启动失败" -ForegroundColor Red
    Write-Host "`n查看最新日志:" -ForegroundColor Yellow
    docker logs doris-fe-01 --tail 20 2>&1 | Out-String
}

# 步骤 7: 显示所有 Doris 容器状态
Write-Host "`n[7] 所有 Doris 容器状态:" -ForegroundColor Yellow
docker ps --filter "name=doris" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
