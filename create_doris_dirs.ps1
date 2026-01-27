# 创建 Doris 数据目录结构

$baseDir = "data"

# FE 节点目录
$feDirs = @("fe-01", "fe-02", "fe-03")
foreach ($fe in $feDirs) {
    $metaDir = Join-Path $baseDir "$fe\doris-meta"
    $logDir = Join-Path $baseDir "$fe\log"
    
    New-Item -ItemType Directory -Force -Path $metaDir | Out-Null
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    Write-Host "创建目录: $metaDir" -ForegroundColor Green
    Write-Host "创建目录: $logDir" -ForegroundColor Green
}

# BE 节点目录
$beDirs = @("be-01", "be-02", "be-03")
foreach ($be in $beDirs) {
    $storageDir = Join-Path $baseDir "$be\storage"
    $scriptDir = Join-Path $baseDir "$be\script"
    $logDir = Join-Path $baseDir "$be\log"
    
    New-Item -ItemType Directory -Force -Path $storageDir | Out-Null
    New-Item -ItemType Directory -Force -Path $scriptDir | Out-Null
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    Write-Host "创建目录: $storageDir" -ForegroundColor Green
    Write-Host "创建目录: $scriptDir" -ForegroundColor Green
    Write-Host "创建目录: $logDir" -ForegroundColor Green
}

Write-Host "`n所有目录创建完成！" -ForegroundColor Cyan
