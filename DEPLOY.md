# Docker 部署操作指南

## 当前状态

根据检查，Docker 环境可能存在以下问题：

1. **Docker Desktop 可能未启动**
   - 错误信息：`Access is denied` 和 `open //./pipe/dockerDesktopLinuxEngine`
   - 解决方法：请确保 Docker Desktop 正在运行

2. **Docker buildx 锁文件被占用**
   - 错误信息：`open C:\Users\gexia\.docker\buildx\.lock: Access is denied`
   - 解决方法：重启 Docker Desktop 或等待其他构建任务完成

## 部署步骤

### 步骤 1: 确保 Docker Desktop 正在运行

1. 打开 Docker Desktop 应用程序
2. 等待 Docker Desktop 完全启动（状态栏显示 "Docker Desktop is running"）
3. 如果 Docker Desktop 未安装，请从 https://www.docker.com/products/docker-desktop 下载安装

### 步骤 2: 检查 Docker 环境

在 PowerShell 中运行：

```powershell
# 检查 Docker 是否运行
docker info

# 检查 Docker Compose
docker compose version
```

如果出现权限错误，请：
- 以管理员身份运行 PowerShell
- 或者确保当前用户在 Docker 用户组中

### 步骤 3: 构建并启动服务

```powershell
# 进入项目目录
cd d:\chaoyang

# 构建镜像（如果遇到锁文件问题，等待几分钟后重试）
docker compose build

# 启动所有服务
docker compose up -d
```

### 步骤 4: 等待服务启动

等待约 30-60 秒，让所有服务完全启动：

```powershell
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f
```

### 步骤 5: 初始化数据库

```powershell
# 初始化数据库表结构
docker compose exec backend python init_doris_tables.py

# 初始化标签数据（可选）
docker compose exec backend python init_tags.py

# 初始化测试数据（可选）
docker compose exec backend python init_database.py --people 100
```

### 步骤 6: 访问应用

- **前端**: http://localhost
- **后端API**: http://localhost:8000
- **Doris FE**: http://localhost:8030

## 常见问题解决

### 问题 1: Docker Desktop 无法启动

**解决方法**:
1. 重启计算机
2. 检查 Windows 功能中是否启用了 "Hyper-V" 或 "WSL 2"
3. 更新 Docker Desktop 到最新版本

### 问题 2: 端口被占用

**检查端口占用**:
```powershell
# 检查端口占用
netstat -ano | findstr ":80"
netstat -ano | findstr ":8000"
netstat -ano | findstr ":8030"
```

**解决方法**:
修改 `docker-compose.yml` 中的端口映射，例如：
```yaml
ports:
  - "8080:80"      # 前端改为 8080
  - "8001:8000"    # 后端改为 8001
```

### 问题 3: 构建失败

**解决方法**:
1. 清理 Docker 缓存：`docker system prune -a`
2. 重启 Docker Desktop
3. 使用 `--no-cache` 强制重新构建：`docker compose build --no-cache`

### 问题 4: 服务无法连接数据库

**检查 Doris 服务**:
```powershell
# 检查 Doris FE
curl http://localhost:8030/api/bootstrap

# 查看 Doris 日志
docker compose logs doris-fe
docker compose logs doris-be
```

**解决方法**:
1. 确保 Doris 服务已完全启动（等待更长时间）
2. 检查网络配置是否正确
3. 查看后端日志：`docker compose logs backend`

## 下一步操作

1. **确保 Docker Desktop 正在运行**
2. **重新执行部署命令**：
   ```powershell
   docker compose build
   docker compose up -d
   ```
3. **如果仍有问题，请查看详细日志**：
   ```powershell
   docker compose logs
   ```

## 联系支持

如果问题持续存在，请提供以下信息：
- Docker Desktop 版本
- 错误日志（`docker compose logs`）
- 系统信息（Windows 版本、是否启用 WSL2/Hyper-V）
