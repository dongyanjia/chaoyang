"""
检查 Doris 表是否创建成功

使用方法:
    python check_doris_tables.py
"""
import sys
import os

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    import pymysql
    
    # Doris 数据库配置
    config = {
        'host': os.getenv('DORIS_HOST', 'localhost'),
        'port': int(os.getenv('DORIS_PORT', 9031)),
        'user': os.getenv('DORIS_USER', 'root'),
        'password': os.getenv('DORIS_PASSWORD', ''),
        'database': os.getenv('DORIS_DATABASE', 'flu_monitoring'),
        'charset': 'utf8mb4'
    }
    
    print('正在检查 Doris 表...')
    
    # 连接数据库
    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    
    # 列出所有表
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    
    print(f'\n数据库 {config["database"]} 中的表:')
    if tables:
        for table in tables:
            table_name = table[0]
            # 统计记录数
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                count = cursor.fetchone()[0]
                print(f'  - {table_name}: {count} 条记录')
            except Exception as e:
                print(f'  - {table_name}: [错误] {e}')
    else:
        print('  (无表)')
    
    cursor.close()
    conn.close()
    
except ImportError:
    print('[ERROR] pymysql 未安装，请运行: pip install pymysql')
except Exception as e:
    print(f'[ERROR] 检查失败: {e}')
    import traceback
    traceback.print_exc()
