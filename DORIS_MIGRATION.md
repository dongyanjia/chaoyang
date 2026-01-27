# Doris 数据库迁移指南

本文档说明如何将系统从 SQLite 迁移到 Apache Doris 4.0。

## 前置要求

1. Docker 和 Docker Compose 已安装
2. Python 3.8+ 已安装
3. 已安装 pymysql: `pip install pymysql==1.1.0`

## 步骤 1: 启动 Doris 服务

使用 Docker Compose 启动 Doris：

```bash
docker-compose up -d
```

等待服务启动完成（约1-2分钟），可以通过以下命令检查状态：

```bash
docker-compose ps
docker-compose logs doris-fe
docker-compose logs doris-be
```

## 步骤 2: 配置数据库连接

创建 `.env` 文件（如果不存在）或更新现有配置：

```env
DORIS_HOST=localhost
DORIS_PORT=9030
DORIS_USER=root
DORIS_PASSWORD=
DORIS_DATABASE=flu_monitoring
```

## 步骤 3: 修改 database.py

将 `backend/database.py` 中的 SQLite 连接改为 Doris（MySQL协议）连接。

主要修改点：
1. 导入 `pymysql` 替代 `sqlite3`
2. 修改连接方法使用 MySQL 协议
3. 修改 SQL 语句：
   - `?` 占位符改为 `%s`
   - `INTEGER PRIMARY KEY AUTOINCREMENT` 改为 `BIGINT AUTO_INCREMENT PRIMARY KEY`
   - `TEXT` 改为 `VARCHAR` 或 `TEXT`（根据长度）
   - `CREATE TABLE IF NOT EXISTS` 语法需要添加 Doris 特定的表属性
   - `INSERT OR REPLACE` 改为 `INSERT ... ON DUPLICATE KEY UPDATE`

## 步骤 4: 数据迁移（可选）

如果已有 SQLite 数据需要迁移：

1. 导出 SQLite 数据：
```bash
python migrate_sqlite_to_doris.py
```

2. 或手动迁移：
   - 导出 SQLite 数据为 CSV/JSON
   - 使用 `init_database.py` 重新生成数据

## 步骤 5: 验证连接

运行以下命令测试连接：

```bash
python -c "from backend.database import Database; db = Database(); db.connect(); print('连接成功！'); db.disconnect()"
```

## 步骤 6: 启动应用

```bash
python backend/app.py
```

## 常见问题

### 1. 连接失败

- 检查 Docker 容器是否正常运行：`docker-compose ps`
- 检查端口是否被占用：`netstat -an | grep 9030`
- 检查防火墙设置

### 2. 表创建失败

- 检查 Doris FE 日志：`docker-compose logs doris-fe`
- 检查 Doris BE 日志：`docker-compose logs doris-be`
- 确保数据库已创建

### 3. 性能问题

- 调整 Doris 的资源配置（内存、CPU）
- 优化表的分桶和副本数
- 添加适当的索引

## Doris 表结构说明

Doris 使用 OLAP 引擎，表结构需要指定：
- `ENGINE=OLAP`: 使用 OLAP 引擎
- `DUPLICATE KEY`: 指定重复键（用于去重）
- `DISTRIBUTED BY HASH`: 数据分布方式
- `BUCKETS`: 分桶数量
- `PROPERTIES`: 表属性（副本数、存储格式等）

## 参考资源

- [Apache Doris 官方文档](https://doris.apache.org/)
- [Doris Docker 部署指南](https://doris.apache.org/docs/dev/install/construct-docker/)
