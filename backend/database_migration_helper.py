"""
数据库迁移辅助脚本
用于将 SQLite 语法转换为 Doris/MySQL 语法

主要转换：
1. ? 占位符 -> %s
2. INTEGER PRIMARY KEY AUTOINCREMENT -> BIGINT AUTO_INCREMENT PRIMARY KEY
3. TEXT -> VARCHAR(n) 或 TEXT
4. INSERT OR REPLACE -> INSERT ... ON DUPLICATE KEY UPDATE
5. PRAGMA table_info -> SHOW COLUMNS FROM
6. sqlite3.OperationalError -> pymysql.Error
"""

import re

def convert_sqlite_to_doris(sql):
    """将 SQLite SQL 转换为 Doris/MySQL SQL"""
    
    # 转换占位符
    sql = sql.replace('?', '%s')
    
    # 转换 AUTOINCREMENT
    sql = re.sub(r'INTEGER PRIMARY KEY AUTOINCREMENT', 'BIGINT AUTO_INCREMENT PRIMARY KEY', sql, flags=re.IGNORECASE)
    
    # 转换 TEXT 类型（根据上下文决定长度）
    # 注意：这需要根据实际字段含义手动调整
    
    # 转换 INSERT OR REPLACE
    if 'INSERT OR REPLACE' in sql.upper():
        # 这需要根据表结构手动处理
        pass
    
    return sql

# 需要手动修改的方法列表
MANUAL_CHANGES = [
    '_create_tables',  # 需要添加 Doris 表属性
    'get_people',  # LIMIT ? OFFSET ? -> LIMIT %s OFFSET %s
    'create_person',  # VALUES (?, ...) -> VALUES (%s, ...)
    'update_person',  # SET ... = ? -> SET ... = %s
    'delete_person',  # WHERE id = ? -> WHERE id = %s
    # ... 所有使用 ? 占位符的地方
]

print("请手动修改以下方法中的 SQL 语句：")
for method in MANUAL_CHANGES:
    print(f"  - {method}")
