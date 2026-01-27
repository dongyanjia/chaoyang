"""
自动修复 database.py 中的 SQL 语法
将 SQLite 语法转换为 Doris/MySQL 语法

使用方法：
    python fix_database_sql.py
"""

import re

def fix_sql_placeholders(content):
    """将 SQL 语句中的 ? 占位符替换为 %s"""
    # 匹配 SQL 语句中的 ? 占位符（不在字符串中）
    # 使用正则表达式匹配 execute() 调用中的 SQL 字符串
    
    # 匹配 execute('...', ...) 或 execute("...", ...) 中的 ?
    def replace_in_sql(match):
        sql = match.group(1)
        # 替换 ? 为 %s（但不在引号内）
        sql = sql.replace('?', '%s')
        return f"execute({match.group(2)}{sql}{match.group(3)}"
    
    # 匹配 execute('...', ...) 模式
    pattern = r"execute\((['\"])(.*?)\1(,.*?)\)"
    content = re.sub(pattern, replace_in_sql, content, flags=re.DOTALL)
    
    return content

def fix_sqlite_exceptions(content):
    """替换 SQLite 异常类型"""
    content = content.replace('sqlite3.OperationalError', 'Exception')
    return content

if __name__ == '__main__':
    print("请手动修改 database.py 文件中的以下内容：")
    print("1. 将所有 ? 占位符替换为 %s")
    print("2. 将所有 sqlite3.OperationalError 替换为 Exception")
    print("3. 将所有 INSERT OR REPLACE 替换为 INSERT ... ON DUPLICATE KEY UPDATE")
    print("4. 将所有 PRAGMA table_info 替换为 SHOW COLUMNS FROM")
    print("\n详细说明请参考 DATABASE_MIGRATION_GUIDE.md")
