# Docker 部署指南

本文档说明如何使用 Docker 和 Docker Compose 部署全国流感人群流动监测系统。

## 前置要求

- Docker Engine 20.10+
- Docker Compose 2.0+

## 快速开始

### 1. 构建并启动所有服务

```bash
docker-compose up -d
```

### 2. 初始化数据库

等待所有服务启动后（约30-60秒），执行数据库初始化：

```bash
# 初始化数据库表结构
docker-compose exec backend python init_doris_tables.py

# 初始化标签数据（可选）
docker-compose exec backend python init_tags.py

# 初始化测试数据（可选）
docker-compose exec backend python init_database.py --people 100
```

### 3. 访问应用

- **前端**: http://localhost
- **后端API**: http://localhost:8000
- **Doris FE**: http://localhost:8030
- **Doris BE**: http://localhost:8040

## 服务说明

### 服务列表

| 服务名 | 容器名 | 端口 | 说明 |
|--------|--------|------|------|
| frontend | flu-monitoring-frontend | 80 | 前端应用（Nginx） |
| backend | flu-monitoring-backend | 8000 | 后端API服务（Flask） |
| doris-fe | doris-fe | 8030, 9030 | Doris 前端节点 |
| doris-be | doris-be | 8040 | Doris 后端节点 |

### 网络配置

所有服务运行在 `app-network` 网络中，子网为 `172.20.81.0/24`：
- Doris FE: `172.20.81.2`
- Doris BE: `172.20.81.3`

## 环境变量

### 后端环境变量

在 `docker-compose.yml` 中可以配置以下环境变量：

```yaml
environment:
  - DORIS_HOST=doris-fe          # Doris 前端地址
  - DORIS_PORT=9030              # Doris MySQL 协议端口
  - DORIS_USER=root              # Doris 用户名
  - DORIS_PASSWORD=              # Doris 密码
  - DORIS_DATABASE=flu_monitoring # 数据库名
  - FLASK_ENV=production         # Flask 环境
```

## 常用命令

### 查看服务状态

```bash
docker-compose ps
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f doris-fe
```

### 停止服务

```bash
docker-compose down
```

### 停止并删除数据卷（谨慎操作）

```bash
docker-compose down -v
```

### 重新构建镜像

```bash
# 重新构建所有镜像
docker-compose build

# 重新构建特定服务
docker-compose build backend
docker-compose build frontend

# 强制重新构建（不使用缓存）
docker-compose build --no-cache
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend sh
```

## 数据持久化

以下数据通过 Docker 卷持久化存储：

- `doris-fe-meta`: Doris FE 元数据
- `doris-fe-log`: Doris FE 日志
- `doris-be-storage`: Doris BE 数据存储
- `doris-be-log`: Doris BE 日志
- `backend-avatars`: 后端头像文件
- `backend-documents`: 后端文档文件
- `backend-chroma`: 向量数据库数据

## 开发模式

使用开发模式配置（支持热重载）：

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

开发模式下：
- 后端代码变更会自动重载
- 前端代码变更会触发 Vite 热更新
- 源代码挂载到容器中

## 故障排查

### 1. 服务无法启动

检查服务健康状态：

```bash
docker-compose ps
```

查看详细日志：

```bash
docker-compose logs [service-name]
```

### 2. 数据库连接失败

检查 Doris 服务是否正常：

```bash
# 检查 Doris FE
curl http://localhost:8030/api/bootstrap

# 检查 Doris BE
curl http://localhost:8040/api/health
```

### 3. 前端无法访问后端API

检查网络连接：

```bash
# 从前端容器测试后端连接
docker-compose exec frontend wget -O- http://backend:8000/api/stats
```

### 4. 端口冲突

如果端口被占用，可以修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8080:80"      # 前端改为 8080
  - "8001:8000"    # 后端改为 8001
```

## 生产环境建议

1. **使用环境变量文件**: 创建 `.env` 文件管理敏感信息
2. **配置 HTTPS**: 使用 Nginx 反向代理配置 SSL 证书
3. **资源限制**: 在 `docker-compose.yml` 中添加资源限制
4. **日志管理**: 配置日志轮转和集中日志管理
5. **备份策略**: 定期备份 Docker 卷数据

## 更新应用

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build
```

## 清理

```bash
# 停止并删除容器
docker-compose down

# 删除所有相关资源（包括数据卷）
docker-compose down -v

# 清理未使用的镜像
docker image prune -a
```
