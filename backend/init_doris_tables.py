"""
执行 doris_schema.sql 文件，初始化 Doris 数据库表结构
"""
import os
import pymysql
import sys

# Doris 数据库连接配置
DORIS_HOST = os.getenv('DORIS_HOST', 'localhost')
DORIS_PORT = int(os.getenv('DORIS_PORT', 9030))
DORIS_USER = os.getenv('DORIS_USER', 'root')
DORIS_PASSWORD = os.getenv('DORIS_PASSWORD', '')

def execute_sql_file(sql_file_path):
    """执行 SQL 文件"""
    print(f'正在读取 SQL 文件: {sql_file_path}')
    
    # 读取 SQL 文件
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 连接数据库
    print(f'正在连接 Doris 数据库: {DORIS_HOST}:{DORIS_PORT}')
    try:
        connection = pymysql.connect(
            host=DORIS_HOST,
            port=DORIS_PORT,
            user=DORIS_USER,
            password=DORIS_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print('[OK] 数据库连接成功')
    except Exception as e:
        print(f'[ERROR] 连接数据库失败: {e}')
        return False
    
    cursor = connection.cursor()
    
    # 分割 SQL 语句（按分号分割，但要注意字符串中的分号和注释）
    statements = []
    lines = sql_content.split('\n')
    current_statement = ''
    in_string = False
    string_char = None
    
    for line in lines:
        # 移除行注释
        if '--' in line:
            comment_pos = line.find('--')
            # 检查 -- 是否在字符串中
            before_comment = line[:comment_pos]
            in_string_before = False
            quote_count = 0
            for char in before_comment:
                if char in ("'", '"', '`'):
                    quote_count += 1
            if quote_count % 2 == 1:
                # -- 在字符串中，保留
                current_statement += line + '\n'
            else:
                # -- 不在字符串中，移除注释部分
                current_statement += before_comment + '\n'
        else:
            current_statement += line + '\n'
        
        # 检查是否有完整的语句（以分号结尾且不在字符串中）
        if ';' in line:
            # 简单处理：找到最后一个分号
            parts = current_statement.rsplit(';', 1)
            if len(parts) == 2:
                statement = parts[0].strip()
                if statement and not statement.startswith('--'):
                    statements.append(statement)
                current_statement = parts[1]
    
    # 处理最后一个语句（如果没有分号结尾）
    remaining = current_statement.strip()
    if remaining and not remaining.startswith('--'):
        statements.append(remaining)
    
    print(f'共找到 {len(statements)} 条 SQL 语句')
    
    # 执行每条 SQL 语句
    success_count = 0
    error_count = 0
    database_created = False
    
    for i, statement in enumerate(statements, 1):
        statement = statement.strip()
        if not statement or statement.startswith('--'):
            continue
        
        # 显示当前执行的语句（截取前100个字符）
        preview = statement[:100].replace('\n', ' ')
        if len(statement) > 100:
            preview += '...'
        print(f'\n[{i}/{len(statements)}] 执行: {preview}')
        
        try:
            cursor.execute(statement)
            connection.commit()
            success_count += 1
            print(f'  [OK] 执行成功')
            
            # 检查是否是 USE 语句成功
            if statement.upper().startswith('USE '):
                database_created = True
                
        except Exception as e:
            error_msg = str(e)
            
            # 如果是数据库不存在的错误，先创建数据库
            if 'Unknown database' in error_msg:
                db_name = 'flu_monitoring'
                print(f'  [WARN] 数据库不存在，尝试创建数据库: {db_name}')
                try:
                    cursor.execute(f'CREATE DATABASE IF NOT EXISTS {db_name}')
                    connection.commit()
                    print(f'  [OK] 数据库创建成功')
                    database_created = True
                    # 重新执行原语句
                    cursor.execute(statement)
                    connection.commit()
                    success_count += 1
                    print(f'  [OK] 执行成功')
                    continue
                except Exception as create_error:
                    print(f'  [ERROR] 创建数据库失败: {str(create_error)[:200]}')
                    error_count += 1
                    continue
            
            # 如果是表或索引已存在的错误，可以忽略
            if 'already exists' in error_msg.lower() or 'Duplicate' in error_msg or 'duplicate key' in error_msg.lower():
                print(f'  [SKIP] 表或索引已存在，跳过')
                success_count += 1
            # 如果是没有选择数据库的错误，尝试选择数据库
            elif 'No database selected' in error_msg:
                if database_created:
                    print(f'  [WARN] 未选择数据库，尝试选择数据库')
                    try:
                        cursor.execute('USE flu_monitoring')
                        # 重新执行原语句
                        cursor.execute(statement)
                        connection.commit()
                        success_count += 1
                        print(f'  [OK] 执行成功')
                        continue
                    except Exception as retry_error:
                        print(f'  [ERROR] 重试失败: {str(retry_error)[:200]}')
                        error_count += 1
                else:
                    print(f'  [ERROR] 执行失败: {error_msg[:200]}')
                    error_count += 1
            else:
                print(f'  [ERROR] 执行失败: {error_msg[:200]}')
                error_count += 1
    
    cursor.close()
    connection.close()
    
    print(f'\n' + '=' * 50)
    print(f'执行完成！')
    print(f'成功: {success_count} 条')
    print(f'失败: {error_count} 条')
    print(f'总计: {len(statements)} 条')
    print('=' * 50)
    
    return error_count == 0

if __name__ == '__main__':
    sql_file = os.path.join(os.path.dirname(__file__), 'doris_schema.sql')
    
    if not os.path.exists(sql_file):
        print(f'[ERROR] SQL 文件不存在: {sql_file}')
        sys.exit(1)
    
    success = execute_sql_file(sql_file)
    sys.exit(0 if success else 1)
