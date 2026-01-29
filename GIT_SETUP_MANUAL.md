# Git 配置和 SSH Key 手动设置指南

由于权限限制，请按照以下步骤手动配置：

## 步骤 1: 配置 Git 用户信息

### 方法 A: 使用 Git Bash（推荐）

1. 打开 **Git Bash**（在开始菜单搜索 "Git Bash"）

2. 运行以下命令：

```bash
# 配置全局用户信息
git config --global user.name "tianzhaoruixiang"
git config --global user.email "tianzhaoruixiang@users.noreply.github.com"

# 验证配置
git config --global --list | grep user
```

### 方法 B: 使用 PowerShell（以管理员身份）

1. **右键点击 PowerShell**，选择"以管理员身份运行"

2. 运行以下命令：

```powershell
git config --global user.name "tianzhaoruixiang"
git config --global user.email "tianzhaoruixiang@users.noreply.github.com"
git config --global --list | Select-String "user"
```

## 步骤 2: 生成 SSH Key

### 方法 A: 使用 Git Bash（推荐）

1. 打开 **Git Bash**

2. 运行以下命令：

```bash
# 生成 SSH Key（Ed25519，推荐）
ssh-keygen -t ed25519 -C "tianzhaoruixiang@users.noreply.github.com"

# 按提示操作：
# - 文件位置：直接按回车使用默认位置 (~/.ssh/id_ed25519)
# - 密码：直接按回车（不使用密码）或输入密码
# - 确认密码：再次按回车或输入相同密码
```

3. 查看公钥：

```bash
cat ~/.ssh/id_ed25519.pub
```

### 方法 B: 使用 PowerShell（以管理员身份）

1. **右键点击 PowerShell**，选择"以管理员身份运行"

2. 运行以下命令：

```powershell
# 确保 .ssh 目录存在
$sshDir = "$env:USERPROFILE\.ssh"
if (-not (Test-Path $sshDir)) {
    New-Item -ItemType Directory -Path $sshDir -Force
}

# 生成 SSH Key
ssh-keygen -t ed25519 -C "tianzhaoruixiang@users.noreply.github.com" -f "$sshDir\id_ed25519"

# 按提示操作（直接按回车使用默认设置）

# 查看公钥
Get-Content "$sshDir\id_ed25519.pub"
```

### 方法 C: 使用 Windows OpenSSH（如果已安装）

```powershell
# 以管理员身份运行 PowerShell
ssh-keygen -t ed25519 -C "tianzhaoruixiang@users.noreply.github.com"
```

## 步骤 3: 复制公钥

### 使用 Git Bash

```bash
# 显示公钥并复制
cat ~/.ssh/id_ed25519.pub
```

### 使用 PowerShell

```powershell
# 显示公钥
Get-Content "$env:USERPROFILE\.ssh\id_ed25519.pub"

# 或复制到剪贴板
Get-Content "$env:USERPROFILE\.ssh\id_ed25519.pub" | Set-Clipboard
```

公钥内容类似：
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... tianzhaoruixiang@users.noreply.github.com
```

## 步骤 4: 将公钥添加到 GitHub

1. **访问 GitHub SSH 设置页面**:
   - https://github.com/settings/keys
   - 或：GitHub → 右上角头像 → Settings → SSH and GPG keys

2. **点击 "New SSH key"**

3. **填写信息**:
   - **Title**: 输入描述性名称（如 "My Windows PC" 或 "Work Laptop"）
   - **Key**: 粘贴刚才复制的公钥内容（整个 `ssh-ed25519 ...` 行）
   - **Key type**: 选择 "Authentication Key"

4. **点击 "Add SSH key"**

5. **输入 GitHub 密码确认**

## 步骤 5: 测试 SSH 连接

### 使用 Git Bash

```bash
ssh -T git@github.com
```

### 使用 PowerShell

```powershell
ssh -T git@github.com
```

**成功输出**:
```
Hi tianzhaoruixiang! You've successfully authenticated, but GitHub does not provide shell access.
```

## 步骤 6: 配置 SSH Agent（可选，但推荐）

### Windows 10/11

```powershell
# 启动 ssh-agent 服务
Start-Service ssh-agent

# 设置服务为自动启动
Set-Service -Name ssh-agent -StartupType Automatic

# 添加 SSH key 到 agent
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

## 步骤 7: 更改仓库远程 URL（如果使用 HTTPS）

如果当前仓库使用 HTTPS URL，可以改为 SSH URL：

```bash
# 查看当前远程 URL
git remote -v

# 更改为 SSH URL
git remote set-url origin git@github.com:dongyanjia/chaoyang.git

# 验证更改
git remote -v
```

## 验证所有配置

运行以下命令验证：

```bash
# Git 配置
git config --global --list | grep user

# SSH key 列表
ssh-add -l

# GitHub 连接测试
ssh -T git@github.com
```

## 如果遇到权限问题

### 解决方案 1: 使用 Git Bash

Git Bash 通常有更好的权限处理，推荐使用。

### 解决方案 2: 以管理员身份运行

右键点击 PowerShell 或命令提示符，选择"以管理员身份运行"。

### 解决方案 3: 检查文件权限

```powershell
# 检查 .ssh 目录权限
icacls "$env:USERPROFILE\.ssh"

# 如果需要，修改权限
icacls "$env:USERPROFILE\.ssh" /grant "$env:USERNAME:(OI)(CI)F"
```

## 快速命令参考

```bash
# Git 配置
git config --global user.name "tianzhaoruixiang"
git config --global user.email "tianzhaoruixiang@users.noreply.github.com"

# 生成 SSH Key
ssh-keygen -t ed25519 -C "tianzhaoruixiang@users.noreply.github.com"

# 查看公钥
cat ~/.ssh/id_ed25519.pub

# 测试连接
ssh -T git@github.com

# 添加 key 到 agent
ssh-add ~/.ssh/id_ed25519
```

## 完成！

配置完成后，您就可以：
- ✅ 使用 SSH URL 克隆仓库（无需密码）
- ✅ 推送代码到 GitHub（无需密码）
- ✅ 使用 Git 进行版本控制

如有问题，请查看 `GIT_SETUP.md` 获取更多帮助。
