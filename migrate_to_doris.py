"""
SQLite 到 Doris 4.0 完整迁移脚本

功能：
1. 创建 Doris 数据库和表结构
2. 从 SQLite 导出数据
3. 导入数据到 Doris
4. 验证迁移结果

使用方法：
    python migrate_to_doris.py
"""
import sqlite3
import pymysql
import json
import os
import sys
from datetime import datetime

# 设置输出编码为 UTF-8（Windows 兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# SQLite 数据库路径
SQLITE_DB_PATH = os.path.join('backend', 'data', 'flu_monitoring.db')

# Doris 数据库配置
# 注意：根据 docker-compose.yaml，FE 节点的 MySQL 查询端口映射为 9031, 9032, 9033
# 使用 FE-02 (端口 9032)，因为 FE-01 可能未启动
DORIS_CONFIG = {
    'host': os.getenv('DORIS_HOST', 'localhost'),
    'port': int(os.getenv('DORIS_PORT', 9032)),
    'user': os.getenv('DORIS_USER', 'root'),
    'password': os.getenv('DORIS_PASSWORD', ''),
    'database': os.getenv('DORIS_DATABASE', 'flu_monitoring'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def create_doris_tables():
    """在 Doris 中创建表结构"""
    print('=' * 60)
    print('步骤 1: 创建 Doris 表结构')
    print('=' * 60)
    
    # 先创建数据库（如果不存在）
    temp_config = DORIS_CONFIG.copy()
    database = temp_config.pop('database')
    temp_config.pop('cursorclass', None)
    
    try:
        temp_conn = pymysql.connect(**temp_config)
        cursor = temp_conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        cursor.close()
        temp_conn.close()
    except Exception as e:
        print(f'[WARN] 创建数据库失败（可能已存在）: {e}')
    
    # 连接到指定数据库并创建表结构
    sys.path.insert(0, 'backend')
    from database import Database
    
    # 使用与迁移脚本相同的配置
    db_config = DORIS_CONFIG.copy()
    db_config.pop('cursorclass', None)  # Database 类会自己设置
    
    db = Database(db_config)
    try:
        db.connect()
        print('[OK] Doris 连接成功')
        print('[OK] 表结构创建完成（如果表已存在则跳过）')
        return db.connection
    except Exception as e:
        print(f'[ERROR] 创建表结构失败: {e}')
        print('\n请检查:')
        print('1. Doris 服务是否运行: docker-compose ps')
        print('2. 端口是否正确（当前使用 9032）')
        print('3. 等待 Doris FE 完全启动（约1-2分钟）')
        raise

def get_table_info(sqlite_conn, table_name):
    """获取 SQLite 表的列信息"""
    cursor = sqlite_conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    cursor.close()
    return columns

def convert_value(value, column_type):
    """转换数据值以适配 Doris"""
    if value is None:
        return None
    
    # 处理日期时间
    if isinstance(value, str):
        # 尝试解析为日期时间
        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S.%f']:
            try:
                dt = datetime.strptime(value, fmt)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                continue
    
    # JSON 字段保持为字符串
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    
    return value

def migrate_table_data(sqlite_conn, doris_conn, table_name):
    """迁移单个表的数据"""
    print(f'\n正在迁移表: {table_name}')
    print('-' * 60)
    
    # 检查 SQLite 表是否存在
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute(f'''
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='{table_name}'
    ''')
    if not sqlite_cursor.fetchone():
        print(f'  [WARN] SQLite 中不存在表 {table_name}，跳过')
        sqlite_cursor.close()
        return 0
    
    # 从 SQLite 读取数据
    sqlite_cursor.execute(f'SELECT * FROM {table_name}')
    rows = sqlite_cursor.fetchall()
    sqlite_cursor.close()
    
    if not rows:
        print(f'  [WARN] 表 {table_name} 无数据，跳过')
        return 0
    
    # 获取列名
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute(f'SELECT * FROM {table_name} LIMIT 1')
    columns = [description[0] for description in sqlite_cursor.description]
    sqlite_cursor.close()
    
    print(f'  📊 找到 {len(rows)} 条记录')
    
    # 插入到 Doris（批量插入以提高性能）
    doris_cursor = doris_conn.cursor()
    
    # 构建插入语句
    columns_str = ','.join([f'`{col}`' for col in columns])
    placeholders = ','.join(['%s'] * len(columns))
    insert_sql = f'INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})'
    
    batch_size = 50  # 减小批量大小以避免内存问题
    total_inserted = 0
    errors = []
    
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        batch_values = []
        
        for row_idx, row in enumerate(batch):
            try:
                # 转换数据格式
                values = []
                for j, col_name in enumerate(columns):
                    value = row[j] if isinstance(row, tuple) else row[col_name]
                    converted_value = convert_value(value, None)
                    values.append(converted_value)
                batch_values.append(values)
            except Exception as e:
                errors.append(f'行 {i + row_idx + 1}: {str(e)}')
                continue
        
        if not batch_values:
            continue
        
        # 批量插入
        try:
            doris_cursor.executemany(insert_sql, batch_values)
            doris_conn.commit()
            total_inserted += len(batch_values)
            print(f'  ✓ 已插入 {total_inserted}/{len(rows)} 条记录', end='\r')
        except Exception as e:
            error_msg = str(e)
            # 如果是内存错误，减小批量大小并逐条插入
            if 'MEM_ALLOC_FAILED' in error_msg or 'memory' in error_msg.lower():
                print(f'\n  [WARN] 内存不足，改为小批量插入（每批10条）')
                # 小批量插入（每批10条）
                small_batch_size = 10
                for small_i in range(0, len(batch_values), small_batch_size):
                    small_batch = batch_values[small_i:small_i + small_batch_size]
                    try:
                        doris_cursor.executemany(insert_sql, small_batch)
                        doris_conn.commit()
                        total_inserted += len(small_batch)
                        print(f'  ✓ 已插入 {total_inserted}/{len(rows)} 条记录', end='\r')
                    except Exception as e3:
                        # 如果小批量也失败，逐条插入
                        for values in small_batch:
                            try:
                                doris_cursor.execute(insert_sql, values)
                                doris_conn.commit()
                                total_inserted += 1
                                print(f'  ✓ 已插入 {total_inserted}/{len(rows)} 条记录', end='\r')
                            except Exception as e4:
                                errors.append(f'插入失败: {str(e4)[:100]}')
                                continue
            else:
                # 其他错误，尝试逐条插入
                print(f'\n  [WARN] 批量插入失败，改为逐条插入: {error_msg[:100]}')
                for values in batch_values:
                    try:
                        doris_cursor.execute(insert_sql, values)
                        doris_conn.commit()
                        total_inserted += 1
                        print(f'  ✓ 已插入 {total_inserted}/{len(rows)} 条记录', end='\r')
                    except Exception as e2:
                        error_str = str(e2)
                        if error_str and error_str != "(0, '')":
                            errors.append(f'插入失败: {error_str[:100]}')
                        continue
    
    doris_cursor.close()
    print(f'\n  ✅ 表 {table_name} 迁移完成: {total_inserted}/{len(rows)} 条记录')
    
    if errors:
        print(f'  [WARN] 有 {len(errors)} 条记录插入失败')
        if len(errors) <= 10:
            for error in errors:
                print(f'    - {error}')
    
    return total_inserted

def verify_migration(sqlite_conn, doris_conn):
    """验证迁移结果"""
    print('\n' + '=' * 60)
    print('步骤 3: 验证迁移结果')
    print('=' * 60)
    
    tables = ['people', 'key_persons', 'movements', 'map_data', 'trend_data', 
              'flow_statistics', 'local_people']
    
    doris_cursor = doris_conn.cursor()
    sqlite_cursor = sqlite_conn.cursor()
    
    for table in tables:
        # 检查 SQLite 表是否存在
        sqlite_cursor.execute(f'''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='{table}'
        ''')
        if not sqlite_cursor.fetchone():
            continue
        
        # 统计 SQLite 记录数
        sqlite_cursor.execute(f'SELECT COUNT(*) as count FROM {table}')
        sqlite_count = sqlite_cursor.fetchone()[0]
        
        # 统计 Doris 记录数
        try:
            doris_cursor.execute(f'SELECT COUNT(*) as count FROM {table}')
            doris_count = doris_cursor.fetchone()['count']
        except:
            doris_count = 0
        
        status = '[OK]' if sqlite_count == doris_count else '[WARN]'
        print(f'{status} {table}: SQLite={sqlite_count}, Doris={doris_count}')
    
    sqlite_cursor.close()
    doris_cursor.close()

def main():
    """主函数"""
    print('=' * 60)
    print('SQLite 到 Doris 4.0 数据迁移')
    print('=' * 60)
    print()
    
    # 步骤 1: 创建 Doris 表结构
    try:
        doris_conn = create_doris_tables()
    except Exception as e:
        print(f'\n[ERROR] 无法创建 Doris 表结构: {e}')
        print('\n请确保:')
        print('1. Doris 服务已启动: docker-compose ps')
        print('2. 数据库配置正确')
        return
    
    # 步骤 2: 检查 SQLite 数据库
    if not os.path.exists(SQLITE_DB_PATH):
        print(f'\n[WARN] SQLite 数据库文件不存在: {SQLITE_DB_PATH}')
        print('将只创建 Doris 表结构，不迁移数据')
        return
    
    # 连接 SQLite
    print('\n' + '=' * 60)
    print('步骤 2: 迁移数据')
    print('=' * 60)
    print('连接 SQLite 数据库...')
    sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    print('[OK] SQLite 连接成功')
    
    # 迁移表
    tables = ['people', 'key_persons', 'movements', 'map_data', 'trend_data', 
              'flow_statistics', 'local_people']
    
    total_count = 0
    for table in tables:
        try:
            count = migrate_table_data(sqlite_conn, doris_conn, table)
            total_count += count
        except Exception as e:
            print(f'\n[ERROR] 迁移表 {table} 失败: {e}')
            import traceback
            traceback.print_exc()
    
    # 步骤 3: 验证迁移结果
    verify_migration(sqlite_conn, doris_conn)
    
    # 关闭连接
    sqlite_conn.close()
    doris_conn.close()
    
    print('\n' + '=' * 60)
    print('迁移完成！')
    print('=' * 60)
    print(f'共迁移 {total_count} 条记录')
    print('\n下一步:')
    print('1. 测试应用连接: python -c "from backend.database import Database; db = Database(); db.connect(); print(\'连接成功\')"')
    print('2. 启动应用: python backend/app.py')

if __name__ == '__main__':
    main()
