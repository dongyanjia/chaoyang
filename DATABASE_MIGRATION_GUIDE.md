# Database.py 迁移到 Doris 完整指南

## 概述

将 `backend/database.py` 从 SQLite 迁移到 Apache Doris 需要以下修改：

## 1. 导入模块修改

**原代码：**
```python
import sqlite3
```

**修改为：**
```python
import pymysql
```

## 2. 数据库配置修改

**原代码：**
```python
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'flu_monitoring.db')
```

**修改为：**
```python
DB_CONFIG = {
    'host': os.getenv('DORIS_HOST', 'localhost'),
    'port': int(os.getenv('DORIS_PORT', 9030)),
    'user': os.getenv('DORIS_USER', 'root'),
    'password': os.getenv('DORIS_PASSWORD', ''),
    'database': os.getenv('DORIS_DATABASE', 'flu_monitoring'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}
```

## 3. SQL 语法修改规则

### 3.1 占位符
- SQLite: `?`
- Doris/MySQL: `%s`

### 3.2 数据类型
- `INTEGER PRIMARY KEY AUTOINCREMENT` → `BIGINT AUTO_INCREMENT PRIMARY KEY`
- `TEXT` → `VARCHAR(255)` 或 `TEXT`（根据实际长度）
- `INTEGER` → `INT` 或 `BIGINT`
- `DATETIME` → `DATETIME`（相同）

### 3.3 表创建语法
Doris 需要添加表属性：

```sql
CREATE TABLE IF NOT EXISTS table_name (
    ...
) ENGINE=OLAP
DUPLICATE KEY(id)
DISTRIBUTED BY HASH(id) BUCKETS 10
PROPERTIES (
    "replication_num" = "1",
    "storage_format" = "V2"
)
```

### 3.4 INSERT OR REPLACE
- SQLite: `INSERT OR REPLACE INTO ...`
- Doris: `INSERT INTO ... ON DUPLICATE KEY UPDATE ...`

### 3.5 字段检查
- SQLite: `PRAGMA table_info(table_name)`
- Doris: `SHOW COLUMNS FROM table_name`

### 3.6 异常处理
- SQLite: `sqlite3.OperationalError`
- Doris: `pymysql.Error` 或 `Exception`

## 4. 关键方法修改示例

### 4.1 connect() 方法

**原代码：**
```python
def connect(self):
    self.connection = sqlite3.connect(self.db_path)
    self.connection.row_factory = sqlite3.Row
    self._create_tables()
    return self.connection
```

**修改为：**
```python
def connect(self):
    # 先创建数据库（如果不存在）
    temp_config = self.db_config.copy()
    database = temp_config.pop('database')
    try:
        temp_conn = pymysql.connect(**temp_config)
        cursor = temp_conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.close()
        temp_conn.close()
    except Exception as e:
        print(f'[WARN] 创建数据库失败: {e}', flush=True)
    
    # 连接到指定数据库
    self.connection = pymysql.connect(**self.db_config)
    self._create_tables()
    return self.connection
```

### 4.2 _create_tables() 方法

需要修改所有 `CREATE TABLE` 语句，添加 Doris 表属性。

**示例：**
```python
cursor.execute('''
    CREATE TABLE IF NOT EXISTS people (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        ...
    ) ENGINE=OLAP
    DUPLICATE KEY(id)
    DISTRIBUTED BY HASH(id) BUCKETS 10
    PROPERTIES (
        "replication_num" = "1",
        "storage_format" = "V2"
    )
''')
```

### 4.3 查询方法修改

所有使用 `?` 占位符的地方改为 `%s`：

**原代码：**
```python
cursor.execute('SELECT * FROM people WHERE id = ?', (person_id,))
```

**修改为：**
```python
cursor.execute('SELECT * FROM people WHERE id = %s', (person_id,))
```

### 4.4 _row_to_dict() 方法

**原代码：**
```python
def _row_to_dict(self, row) -> Dict:
    if not row:
        return {}
    result = {}
    for key in row.keys():
        value = row[key]
        ...
```

**修改为：**
```python
def _row_to_dict(self, row) -> Dict:
    if not row:
        return {}
    
    # pymysql 使用 DictCursor，row 已经是字典
    if isinstance(row, dict):
        result = row.copy()
    else:
        result = {}
        for key in row.keys():
            result[key] = row[key]
    ...
```

## 5. 需要修改的方法列表

以下方法需要将 `?` 改为 `%s`：

1. `get_people()` - LIMIT ? OFFSET ?
2. `get_person()` - WHERE id = ?
3. `create_person()` - VALUES (?, ?, ...)
4. `update_person()` - SET ... = ? WHERE id = ?
5. `delete_person()` - WHERE id = ?
6. `get_movements()` - WHERE ... = ?
7. `create_movement()` - VALUES (?, ?, ...)
8. `update_map_data()` - INSERT OR REPLACE
9. `get_trend_data()` - WHERE date >= ? AND date <= ?
10. `create_trend_data()` - INSERT OR REPLACE
11. `get_flow_statistics()` - WHERE period = ?
12. `create_flow_statistics()` - INSERT OR REPLACE
13. `get_key_persons()` - WHERE category = ?
14. `add_key_person()` - INSERT OR REPLACE
15. `remove_key_person()` - WHERE person_id = ? AND category = ?
16. `update_key_person()` - WHERE person_id = ? AND category = ?
17. `get_stats()` - WHERE status = ?
18. `get_province_confirmed_ranking()` - WHERE status = ?
19. `batch_create_local_people()` - VALUES (?, ?, ...)
20. `get_local_people()` - SELECT * FROM ...
21. `get_local_person()` - WHERE id = ?
22. `batch_delete_local_people()` - WHERE id IN (...)
23. `clear_all_data()` - DELETE FROM ...

## 6. 自动化迁移脚本

可以使用以下 Python 脚本批量替换：

```python
import re

def replace_placeholders(content):
    # 替换 SQL 语句中的 ? 为 %s（但不在字符串字面量中）
    # 注意：这需要小心处理，最好手动检查
    content = re.sub(r'(\?)(?=\s*[,\)])', r'%s', content)
    return content
```

## 7. 测试验证

迁移完成后，运行以下测试：

```python
from backend.database import Database

# 测试连接
db = Database()
db.connect()
print("连接成功！")

# 测试查询
people = db.get_people(page=1, page_size=10)
print(f"查询到 {len(people)} 条记录")

# 测试创建
test_person = {
    'name': '测试用户',
    'idCard': '123456789012345678',
    'region': '北京',
    'age': 25,
    'phone': '13800138000',
    'status': '正常'
}
result = db.create_person(test_person)
print(f"创建成功: {result}")

db.disconnect()
```

## 8. 注意事项

1. **事务处理**: Doris 支持事务，但某些操作可能需要显式提交
2. **字符编码**: 确保使用 `utf8mb4` 字符集
3. **日期时间**: Doris 的 DATETIME 格式与 SQLite 相同
4. **JSON 字段**: TEXT 类型存储 JSON 字符串，需要手动序列化/反序列化
5. **索引**: Doris 的索引语法与 MySQL 相同
6. **外键**: Doris 可能不支持外键约束，需要应用层保证数据一致性

## 9. 性能优化建议

1. 根据数据量调整 `BUCKETS` 数量
2. 根据查询模式选择合适的 `DUPLICATE KEY`
3. 添加适当的索引
4. 考虑使用分区表（如果数据量大）
