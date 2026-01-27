# SQLite 到 Doris 数据迁移状态

## 当前状态

### ✅ 已完成
1. **后端代码已切换到 Doris**
   - `backend/database.py` 使用 `pymysql` 连接 Doris
   - 配置端口：9032 (FE-02)
   - 数据库：`flu_monitoring`

2. **Doris 表结构已创建**
   - 所有表结构已适配 Doris 语法
   - 表包括：people, key_persons, movements, map_data, trend_data, flow_statistics, local_people

3. **BE 节点状态正常**
   - 3个 BE 节点均为 `Alive = true`
   - 可以接收数据

### ❌ 待完成
1. **数据迁移未完成**
   - 之前迁移了 100 条 people 记录
   - 其他表数据未迁移成功
   - 原因：内存分配失败和连接问题

2. **Doris FE-02 连接失败**
   - 当前无法连接到端口 9032
   - 需要检查并启动 Doris 服务

## 迁移步骤

### 步骤 1: 确保 Doris 服务运行

```powershell
# 检查容器状态
docker-compose ps

# 如果 FE-02 未运行，启动它
docker-compose up -d docker-fe-02

# 等待服务启动（约30秒）
Start-Sleep -Seconds 30

# 测试连接
python test_doris_fe02.py
```

### 步骤 2: 运行数据迁移

```powershell
# 运行迁移脚本
python migrate_to_doris.py
```

迁移脚本会：
1. 创建 Doris 表结构（如果不存在）
2. 从 SQLite 读取数据
3. 批量插入到 Doris（批量大小已优化为50条，内存不足时自动减小到10条）
4. 验证迁移结果

### 步骤 3: 验证迁移结果

```powershell
# 检查表数据
python check_doris_tables.py
```

## 迁移脚本优化

已优化的功能：
- ✅ 批量大小从 100 减小到 50
- ✅ 内存不足时自动减小到 10 条/批
- ✅ 改进错误处理和重试机制
- ✅ 使用 FE-02 端口 (9032)

## 数据统计

SQLite 数据库中的数据：
- people: 8000 条
- key_persons: 4747 条
- movements: 16000 条
- map_data: 34 条
- trend_data: 69 条
- flow_statistics: 588 条
- local_people: 4 条

**总计：约 28,442 条记录**

## 注意事项

1. **内存问题**：如果遇到内存分配失败，脚本会自动减小批量大小
2. **连接问题**：确保 Doris FE-02 服务正常运行
3. **数据完整性**：迁移完成后会验证记录数是否匹配

## 故障排除

### 如果连接失败：
```powershell
# 检查端口是否被占用
netstat -ano | findstr ":9032"

# 检查 Docker 容器日志
docker logs doris-fe-02 --tail 50
```

### 如果内存不足：
- 脚本会自动减小批量大小
- 如果仍然失败，可以手动修改 `batch_size` 为更小的值（如 10 或 5）

### 如果迁移中断：
- 可以重新运行迁移脚本
- 脚本会跳过已存在的记录（如果表有唯一约束）

## 下一步

1. 启动 Doris FE-02 服务
2. 运行迁移脚本
3. 验证数据迁移结果
4. 重启后端服务以使用 Doris 数据库
