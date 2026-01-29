# Git 配置和 SSH Key 生成脚本

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Git 配置和 SSH Key 生成" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$username = "tianzhaoruixiang"
$email = "tianzhaoruixiang@users.noreply.github.com"

# 1. 配置 Git 用户信息
Write-Host "1. 配置 Git 用户信息..." -ForegroundColor Yellow

# 尝试全局配置
try {
    git config --global user.name $username
    git config --global user.email $email
    Write-Host "   [OK] 全局 Git 配置成功" -ForegroundColor Green
} catch {
    Write-Host "   [警告] 全局配置失败，尝试项目级配置" -ForegroundColor Yellow
    try {
        git config user.name $username
        git config user.email $email
        Write-Host "   [OK] 项目级 Git 配置成功" -ForegroundColor Green
    } catch {
        Write-Host "   [错误] Git 配置失败: $_" -ForegroundColor Red
    }
}

# 显示当前配置
Write-Host ""
Write-Host "当前 Git 配置:" -ForegroundColor Cyan
git config --list | Select-String "user\." | ForEach-Object { Write-Host "   $_" -ForegroundColor White }

# 2. 检查 SSH 目录
Write-Host ""
Write-Host "2. 检查 SSH 目录..." -ForegroundColor Yellow
$sshDir = "$env:USERPROFILE\.ssh"
if (-not (Test-Path $sshDir)) {
    try {
        New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
        Write-Host "   [OK] 创建 SSH 目录: $sshDir" -ForegroundColor Green
    } catch {
        Write-Host "   [错误] 无法创建 SSH 目录: $_" -ForegroundColor Red
        Write-Host "   请手动创建目录: $sshDir" -ForegroundColor Yellow
    }
} else {
    Write-Host "   [OK] SSH 目录已存在: $sshDir" -ForegroundColor Green
}

# 3. 检查是否已有 SSH key
Write-Host ""
Write-Host "3. 检查现有 SSH Key..." -ForegroundColor Yellow
$keyPath = "$sshDir\id_ed25519"
$pubKeyPath = "$sshDir\id_ed25519.pub"

if (Test-Path $keyPath) {
    Write-Host "   [信息] SSH Key 已存在: $keyPath" -ForegroundColor Yellow
    Write-Host "   是否要重新生成？(Y/N): " -ForegroundColor Yellow -NoNewline
    $response = Read-Host
    if ($response -ne "Y" -and $response -ne "y") {
        Write-Host "   跳过 SSH Key 生成" -ForegroundColor Yellow
        $skipKeyGen = $true
    } else {
        Write-Host "   将覆盖现有 Key" -ForegroundColor Yellow
        Remove-Item $keyPath -ErrorAction SilentlyContinue
        Remove-Item $pubKeyPath -ErrorAction SilentlyContinue
    }
}

# 4. 生成 SSH Key
if (-not $skipKeyGen) {
    Write-Host ""
    Write-Host "4. 生成 SSH Key..." -ForegroundColor Yellow
    try {
        ssh-keygen -t ed25519 -C $email -f $keyPath -N '""'
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   [OK] SSH Key 生成成功" -ForegroundColor Green
        } else {
            Write-Host "   [错误] SSH Key 生成失败" -ForegroundColor Red
        }
    } catch {
        Write-Host "   [错误] SSH Key 生成失败: $_" -ForegroundColor Red
        Write-Host "   请手动运行以下命令:" -ForegroundColor Yellow
        Write-Host "   ssh-keygen -t ed25519 -C `"$email`" -f `"$keyPath`"" -ForegroundColor White
    }
}

# 5. 显示公钥
Write-Host ""
Write-Host "5. SSH 公钥内容:" -ForegroundColor Cyan
if (Test-Path $pubKeyPath) {
    Write-Host ""
    $publicKey = Get-Content $pubKeyPath
    Write-Host $publicKey -ForegroundColor White
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "请将上面的公钥添加到 GitHub/GitLab:" -ForegroundColor Yellow
    Write-Host "1. 复制上面的公钥内容" -ForegroundColor White
    Write-Host "2. 访问 https://github.com/settings/keys" -ForegroundColor White
    Write-Host "3. 点击 'New SSH key'" -ForegroundColor White
    Write-Host "4. 粘贴公钥并保存" -ForegroundColor White
    Write-Host "==========================================" -ForegroundColor Cyan
} else {
    Write-Host "   [警告] 公钥文件不存在" -ForegroundColor Yellow
}

# 6. 测试 SSH 连接（如果配置了 GitHub）
Write-Host ""
Write-Host "6. 测试 SSH 连接..." -ForegroundColor Yellow
Write-Host "   运行以下命令测试 GitHub SSH 连接:" -ForegroundColor White
Write-Host "   ssh -T git@github.com" -ForegroundColor Cyan

Write-Host ""
Write-Host "配置完成！" -ForegroundColor Green
