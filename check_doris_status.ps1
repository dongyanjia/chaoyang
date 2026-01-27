# 检查 Doris 容器状态脚本

Write-Host "检查 Docker 容器状态..." -ForegroundColor Cyan
docker ps -a --filter "name=doris"

Write-Host "`n检查 doris-fe-01 日志（最后50行）..." -ForegroundColor Cyan
docker logs doris-fe-01 --tail 50 2>&1

Write-Host "`n检查端口占用..." -ForegroundColor Cyan
netstat -ano | findstr ":9031"
netstat -ano | findstr ":8031"

Write-Host "`n尝试启动 doris-fe-01..." -ForegroundColor Cyan
docker-compose up -d docker-fe-01

Write-Host "`n等待5秒后检查状态..." -ForegroundColor Cyan
Start-Sleep -Seconds 5
docker ps --filter "name=doris-fe-01"
