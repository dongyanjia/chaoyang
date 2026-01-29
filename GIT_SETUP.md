# Git 配置和 SSH Key 设置指南

## 快速配置

### 方式 1: 使用配置脚本（推荐）

```powershell
cd d:\chaoyang
powershell -ExecutionPolicy Bypass -File setup-git.ps1
```

### 方式 2: 手动配置

## 手动配置步骤

### 1. 配置 Git 用户信息

#### 全局配置（推荐）

```powershell
git config --global user.name "tianzhaoruixiang"
git config --global user.email "tianzhaoruixiang@users.noreply.github.com"
```

#### 项目级配置（如果全局配置失败）

```powershell
cd d:\chaoyang
git config user.name "tianzhaoruixiang"
git config user.email "tianzhaoruixiang@users.noreply.github.com"
```

### 2. 验证配置

```powershell
git config --list | findstr "user"
```

应该看到：
```
user.name=tianzhaoruixiang
user.email=tianzhaoruixiang@users.noreply.github.com
```

### 3. 生成 SSH Key

#### 检查是否已有 SSH Key

```powershell
dir $env:USERPROFILE\.ssh\id_ed25519*
```

如果文件已存在，可以跳过生成步骤，直接查看公钥。

#### 生成新的 SSH Key

```powershell
# 创建 .ssh 目录（如果不存在）
mkdir $env:USERPROFILE\.ssh -ErrorAction SilentlyContinue

# 生成 SSH Key（Ed25519 算法，推荐）
ssh-keygen -t ed25519 -C "tianzhaoruixiang@users.noreply.github.com" -f "$env:USERPROFILE\.ssh\id_ed25519"

# 按提示操作：
# - 如果询问密码，直接按回车（不使用密码）
# - 如果询问覆盖，输入 y（如果已存在）
```

#### 或者使用 RSA 算法（如果 Ed25519 不支持）

```powershell
ssh-keygen -t rsa -b 4096 -C "tianzhaoruixiang@users.noreply.github.com" -f "$env:USERPROFILE\.ssh\id_rsa"
```

### 4. 查看公钥

```powershell
# Ed25519 公钥
cat $env:USERPROFILE\.ssh\id_ed25519.pub

# 或 RSA 公钥
cat $env:USERPROFILE\.ssh\id_rsa.pub
```

### 5. 将公钥添加到 GitHub

1. **复制公钥内容**（从上面的命令输出）

2. **访问 GitHub SSH 设置页面**:
   - https://github.com/settings/keys
   - 或：GitHub → Settings → SSH and GPG keys

3. **添加 SSH Key**:
   - 点击 "New SSH key"
   - Title: 输入一个描述性名称（如 "My Windows PC"）
   - Key: 粘贴公钥内容
   - 点击 "Add SSH key"

### 6. 测试 SSH 连接

```powershell
ssh -T git@github.com
```

如果成功，会看到类似以下消息：
```
Hi tianzhaoruixiang! You've successfully authenticated, but GitHub does not provide shell access.
```

## 配置 SSH Agent（可选）

### Windows 10/11（使用 OpenSSH）

```powershell
# 启动 ssh-agent
Start-Service ssh-agent

# 添加 SSH key 到 agent
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

### 自动启动 SSH Agent

创建或编辑 `$env:USERPROFILE\.ssh\config` 文件：

```
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

## 使用 SSH URL 克隆仓库

配置完成后，可以使用 SSH URL 克隆仓库：

```powershell
# 使用 SSH URL（推荐）
git clone git@github.com:dongyanjia/chaoyang.git

# 而不是 HTTPS URL
# git clone https://github.com/dongyanjia/chaoyang.git
```

## 更改现有仓库的远程 URL

如果仓库已经使用 HTTPS URL，可以改为 SSH URL：

```powershell
cd d:\chaoyang

# 查看当前远程 URL
git remote -v

# 更改为 SSH URL
git remote set-url origin git@github.com:dongyanjia/chaoyang.git

# 验证更改
git remote -v
```

## 常见问题

### 问题 1: 权限被拒绝

**错误信息**: `Permission denied (publickey)`

**解决方法**:
1. 确保公钥已添加到 GitHub
2. 检查 SSH key 是否正确加载：`ssh-add -l`
3. 测试连接：`ssh -T git@github.com`

### 问题 2: Git 配置文件锁定

**错误信息**: `could not lock config file`

**解决方法**:
1. 关闭所有 Git 相关程序（Git GUI、IDE 等）
2. 检查 `.gitconfig` 文件是否被其他程序占用
3. 以管理员身份运行 PowerShell

### 问题 3: SSH Key 已存在

**解决方法**:
1. 使用现有 key：直接查看公钥并添加到 GitHub
2. 或生成新 key：使用不同的文件名
   ```powershell
   ssh-keygen -t ed25519 -C "your-email@example.com" -f "$env:USERPROFILE\.ssh\id_ed25519_github"
   ```

### 问题 4: 多个 GitHub 账号

如果需要为不同账号使用不同的 SSH key：

1. **生成多个 SSH key**:
   ```powershell
   ssh-keygen -t ed25519 -C "account1@example.com" -f "$env:USERPROFILE\.ssh\id_ed25519_account1"
   ssh-keygen -t ed25519 -C "account2@example.com" -f "$env:USERPROFILE\.ssh\id_ed25519_account2"
   ```

2. **配置 SSH config** (`$env:USERPROFILE\.ssh\config`):
   ```
   # Account 1
   Host github.com-account1
       HostName github.com
       User git
       IdentityFile ~/.ssh/id_ed25519_account1

   # Account 2
   Host github.com-account2
       HostName github.com
       User git
       IdentityFile ~/.ssh/id_ed25519_account2
   ```

3. **使用不同的 Host 名称克隆**:
   ```powershell
   git clone git@github.com-account1:username/repo.git
   ```

## 验证配置

运行以下命令验证所有配置：

```powershell
# 检查 Git 配置
git config --list | findstr "user"

# 检查 SSH key
ssh-add -l

# 测试 GitHub 连接
ssh -T git@github.com

# 查看公钥
cat $env:USERPROFILE\.ssh\id_ed25519.pub
```

## 下一步

配置完成后，可以：
1. 使用 SSH URL 克隆仓库
2. 推送代码到 GitHub
3. 无需每次输入密码
