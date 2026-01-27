# Doris 数据库快速启动指南

## 快速开始

### 1. 启动 Doris 服务

```bash
docker-compose up -d
```

### 2. 检查服务状态

```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f doris-fe
docker-compose logs -f doris-be
```

### 3. 安装 Python 依赖

```bash
pip install -r backend/requirements.txt
```

### 4. 测试连接

创建测试脚本 `test_doris.py`:

```python
from backend.database import Database

try:
    db = Database()
    db.connect()
    print("✅ Doris 连接成功！")
    
    # 测试查询
    count = db.get_people_count()
    print(f"✅ 当前人员数量: {count}")
    
    db.disconnect()
except Exception as e:
    print(f"❌ 连接失败: {e}")
```

运行：
```bash
python test_doris.py
```

### 5. 初始化数据库（首次使用）

```bash
python backend/init_database.py
```

## 常见问题

### Q: Docker 容器启动失败？
A: 检查端口是否被占用：
```bash
netstat -an | grep 9030
netstat -an | grep 8030
```

### Q: 连接超时？
A: 等待 Doris FE 完全启动（约1-2分钟），然后重试。

### Q: 表创建失败？
A: 检查 Doris FE 日志：
```bash
docker-compose logs doris-fe | tail -50
```

### Q: 如何停止服务？
A: 
```bash
docker-compose down
```

### Q: 如何清理数据重新开始？
A:
```bash
docker-compose down -v  # 删除数据卷
docker-compose up -d    # 重新启动
```

## 配置说明

默认配置（可通过环境变量修改）：
- Host: localhost
- Port: 9030 (MySQL协议端口)
- User: root
- Password: (空)
- Database: flu_monitoring

## 下一步

1. ✅ 启动 Doris 服务
2. ✅ 测试连接
3. ✅ 初始化数据库
4. ✅ 启动应用: `python backend/app.py`
