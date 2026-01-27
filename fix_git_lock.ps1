# Git 锁文件修复脚本
# 请以管理员身份运行此脚本

Write-Host "正在尝试删除 Git 锁文件..." -ForegroundColor Yellow

$lockFiles = @(
    ".git\index.lock",
    ".git\config.lock"
)

foreach ($file in $lockFiles) {
    if (Test-Path $file) {
        Write-Host "发现锁文件: $file" -ForegroundColor Cyan
        try {
            # 尝试获取文件所有权
            $acl = Get-Acl $file
            $owner = $acl.Owner
            Write-Host "当前所有者: $owner" -ForegroundColor Gray
            
            # 尝试删除
            Remove-Item $file -Force -ErrorAction Stop
            Write-Host "✓ 成功删除: $file" -ForegroundColor Green
        } catch {
            Write-Host "✗ 删除失败: $file" -ForegroundColor Red
            Write-Host "  错误信息: $_" -ForegroundColor Red
            Write-Host "  请尝试手动删除此文件" -ForegroundColor Yellow
        }
    } else {
        Write-Host "锁文件不存在: $file" -ForegroundColor Gray
    }
}

Write-Host "`n检查 Git 状态..." -ForegroundColor Yellow
git status --short | Select-Object -First 5
