"""
SQLite 到 Doris 数据迁移脚本

使用方法：
    python migrate_sqlite_to_doris.py

功能：
    - 从 SQLite 数据库导出数据
    - 导入到 Doris 数据库
    - 保持表结构一致
"""
import sqlite3
import pymysql
import json
import os
from datetime import datetime

# SQLite 数据库路径
SQLITE_DB_PATH = os.path.join('backend', 'data', 'flu_monitoring.db')

# Doris 数据库配置
DORIS_CONFIG = {
    'host': os.getenv('DORIS_HOST', 'localhost'),
    'port': int(os.getenv('DORIS_PORT', 9030)),
    'user': os.getenv('DORIS_USER', 'root'),
    'password': os.getenv('DORIS_PASSWORD', ''),
    'database': os.getenv('DORIS_DATABASE', 'flu_monitoring'),
    'charset': 'utf8mb4'
}

def migrate_table(sqlite_conn, doris_conn, table_name):
    """迁移单个表的数据"""
    print(f'正在迁移表: {table_name}...')
    
    # 从 SQLite 读取数据
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute(f'SELECT * FROM {table_name}')
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        print(f'  表 {table_name} 无数据，跳过')
        return 0
    
    # 获取列名
    columns = [description[0] for description in sqlite_cursor.description]
    
    # 插入到 Doris
    doris_cursor = doris_conn.cursor()
    
    # 构建插入语句
    placeholders = ','.join(['%s'] * len(columns))
    columns_str = ','.join([f'`{col}`' for col in columns])
    insert_sql = f'INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})'
    
    count = 0
    for row in rows:
        try:
            # 转换数据格式
            values = []
            for i, value in enumerate(row):
                if isinstance(value, str):
                    # 处理日期时间字符串
                    if 'created_at' in columns[i] or 'updated_at' in columns[i] or 'last_update' in columns[i]:
                        try:
                            datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                            values.append(value)
                        except:
                            values.append(None)
                    else:
                        values.append(value)
                elif value is None:
                    values.append(None)
                else:
                    values.append(value)
            
            doris_cursor.execute(insert_sql, values)
            count += 1
        except Exception as e:
            print(f'  插入失败: {e}')
            continue
    
    doris_conn.commit()
    doris_cursor.close()
    print(f'  ✓ 已迁移 {count} 条记录')
    return count

def main():
    """主函数"""
    print('=' * 50)
    print('SQLite 到 Doris 数据迁移')
    print('=' * 50)
    
    # 检查 SQLite 数据库是否存在
    if not os.path.exists(SQLITE_DB_PATH):
        print(f'错误: SQLite 数据库文件不存在: {SQLITE_DB_PATH}')
        return
    
    # 连接 SQLite
    print('连接 SQLite 数据库...')
    sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    print('✓ SQLite 连接成功')
    
    # 连接 Doris
    print('连接 Doris 数据库...')
    try:
        doris_conn = pymysql.connect(**DORIS_CONFIG)
        print('✓ Doris 连接成功')
    except Exception as e:
        print(f'错误: 无法连接 Doris: {e}')
        print('请确保:')
        print('1. Doris 服务已启动: docker-compose up -d')
        print('2. 数据库配置正确')
        sqlite_conn.close()
        return
    
    # 迁移表
    tables = ['people', 'key_persons', 'movements', 'map_data', 'trend_data', 
              'flow_statistics', 'local_people']
    
    total_count = 0
    for table in tables:
        try:
            count = migrate_table(sqlite_conn, doris_conn, table)
            total_count += count
        except Exception as e:
            print(f'  迁移表 {table} 失败: {e}')
    
    # 关闭连接
    sqlite_conn.close()
    doris_conn.close()
    
    print('=' * 50)
    print(f'迁移完成！共迁移 {total_count} 条记录')
    print('=' * 50)

if __name__ == '__main__':
    main()
