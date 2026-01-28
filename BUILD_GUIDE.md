# 构建镜像指南

## 当前状态

Docker Desktop 未运行，需要先启动 Docker Desktop 才能构建镜像。

## 构建步骤

### 步骤 1: 启动 Docker Desktop

1. **打开 Docker Desktop 应用程序**
   - 在 Windows 开始菜单中搜索 "Docker Desktop"
   - 或者从系统托盘启动

2. **等待 Docker Desktop 完全启动**
   - 状态栏应显示 "Docker Desktop is running"
   - 等待约 10-30 秒

3. **验证 Docker 是否运行**
   ```powershell
   docker info
   ```
   如果成功显示 Docker 信息，说明已就绪。

### 步骤 2: 构建镜像

#### 方式 1: 使用构建脚本（推荐）

```powershell
cd d:\chaoyang
powershell -ExecutionPolicy Bypass -File build-images.ps1
```

#### 方式 2: 手动构建

**构建后端镜像**:
```powershell
docker compose build backend
```

**构建前端镜像**:
```powershell
docker compose build frontend
```

**同时构建所有镜像**:
```powershell
docker compose build
```

### 步骤 3: 验证镜像

构建完成后，查看镜像列表：

```powershell
docker images
```

应该能看到类似以下镜像：
- `chaoyang-backend` 或 `chaoyang-backend`
- `chaoyang-frontend` 或 `chaoyang-frontend`

## 构建选项

### 强制重新构建（不使用缓存）

```powershell
docker compose build --no-cache backend
docker compose build --no-cache frontend
```

### 只构建特定服务

```powershell
# 只构建后端
docker compose build backend

# 只构建前端
docker compose build frontend
```

### 并行构建（加快速度）

```powershell
docker compose build --parallel
```

## 构建时间估算

- **后端镜像**: 约 2-5 分钟（首次构建，需要下载 Python 基础镜像和安装依赖）
- **前端镜像**: 约 1-3 分钟（首次构建，需要下载 Node.js 基础镜像和安装依赖）
- **后续构建**: 约 30 秒 - 2 分钟（使用缓存）

## 常见问题

### 问题 1: "Access is denied" 错误

**原因**: Docker Desktop 未运行或权限不足

**解决方法**:
1. 确保 Docker Desktop 正在运行
2. 以管理员身份运行 PowerShell
3. 重启 Docker Desktop

### 问题 2: "buildx lock" 错误

**原因**: 另一个构建进程正在运行

**解决方法**:
1. 等待当前构建完成
2. 或者重启 Docker Desktop

### 问题 3: 构建速度慢

**解决方法**:
1. 使用国内镜像源（配置 Docker Desktop 镜像加速）
2. 使用 `--parallel` 并行构建
3. 确保网络连接正常

### 问题 4: 构建失败 - 依赖安装错误

**后端构建失败**:
```powershell
# 检查 requirements.txt 是否正确
cat backend\requirements.txt

# 尝试手动安装依赖测试
cd backend
pip install -r requirements.txt
```

**前端构建失败**:
```powershell
# 检查 package.json 是否正确
cat frontend\package.json

# 尝试手动安装依赖测试
cd frontend
npm install
```

## 构建优化建议

1. **使用多阶段构建**: 已在前端 Dockerfile 中实现
2. **合理使用缓存**: 先复制依赖文件，再复制源代码
3. **使用 .dockerignore**: 排除不必要的文件，加快构建速度
4. **定期清理**: 清理未使用的镜像和缓存

## 下一步

构建完成后，可以启动服务：

```powershell
docker compose up -d
```

查看服务状态：

```powershell
docker compose ps
```
