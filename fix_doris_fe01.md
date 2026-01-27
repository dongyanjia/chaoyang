# 修复 doris-fe-01 启动问题

## 问题分析

从 `docker-compose ps` 输出可以看到：
- ✅ doris-fe-02 正常运行
- ✅ doris-fe-03 正常运行  
- ❌ doris-fe-01 未启动
- ✅ 所有 BE 节点正常运行

## 可能的原因

1. **卷挂载路径问题**：Windows 上 `/data/fe-01/...` 路径可能不存在
2. **第一个 FE 节点初始化失败**：FE-01 是集群的第一个节点，需要特殊处理
3. **端口冲突**：端口 8031 或 9031 可能被占用
4. **网络配置问题**：IP 地址 172.20.80.2 可能冲突

## 解决步骤

### 步骤 1: 检查容器状态和日志

```powershell
# 查看所有容器（包括已停止的）
docker ps -a | Select-String "doris-fe-01"

# 查看 doris-fe-01 的日志
docker logs doris-fe-01 --tail 100

# 查看容器详细信息
docker inspect doris-fe-01
```

### 步骤 2: 检查端口占用

```powershell
# 检查端口 8031 和 9031 是否被占用
netstat -ano | findstr ":8031"
netstat -ano | findstr ":9031"
```

### 步骤 3: 尝试手动启动

```powershell
# 尝试启动 doris-fe-01
docker-compose up -d docker-fe-01

# 或者直接使用 docker 命令
docker start doris-fe-01
```

### 步骤 4: 如果启动失败，检查卷挂载

Windows 上 `/data/fe-01/...` 路径可能不存在。可以：

1. **创建本地目录**（如果使用 Docker Desktop 的卷映射）：
   ```powershell
   # 创建本地目录
   New-Item -ItemType Directory -Force -Path "F:\doris-data\fe-01\doris-meta"
   New-Item -ItemType Directory -Force -Path "F:\doris-data\fe-01\log"
   ```

2. **修改 docker-compose.yaml** 使用 Windows 路径：
   ```yaml
   volumes:
     - F:/doris-data/fe-01/doris-meta:/opt/apache-doris/fe/doris-meta
     - F:/doris-data/fe-01/log:/opt/apache-doris/fe/log
   ```

### 步骤 5: 如果仍然失败，重新创建容器

```powershell
# 停止并删除容器
docker-compose stop docker-fe-01
docker-compose rm -f docker-fe-01

# 重新创建并启动
docker-compose up -d docker-fe-01
```

### 步骤 6: 检查网络配置

```powershell
# 检查网络是否存在
docker network ls | Select-String "doris"

# 检查网络详细信息
docker network inspect chaoyangv102_doris-network
```

## 快速修复命令

运行以下 PowerShell 脚本：

```powershell
# 检查状态
Write-Host "检查 doris-fe-01 状态..." -ForegroundColor Cyan
docker ps -a --filter "name=doris-fe-01"

# 查看日志
Write-Host "`n查看日志..." -ForegroundColor Cyan
docker logs doris-fe-01 --tail 50

# 尝试启动
Write-Host "`n尝试启动..." -ForegroundColor Cyan
docker-compose up -d docker-fe-01

# 等待并检查
Start-Sleep -Seconds 5
Write-Host "`n检查启动结果..." -ForegroundColor Cyan
docker ps --filter "name=doris-fe-01"
```

## 注意事项

1. **FE-01 是主节点**：在 Doris 集群中，第一个 FE 节点（FE-01）是主节点，需要先启动
2. **数据持久化**：如果删除容器，确保数据卷已正确挂载，否则数据会丢失
3. **集群配置**：FE-02 和 FE-03 依赖 FE-01，如果 FE-01 未启动，集群可能无法正常工作

## 如果问题仍然存在

请提供以下信息以便进一步诊断：
1. `docker logs doris-fe-01` 的完整输出
2. `docker inspect doris-fe-01` 的输出
3. `docker-compose ps` 的完整输出
