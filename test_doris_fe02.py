"""
测试 doris-fe-02 连接（端口 9032）
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
    
    # 使用 FE-02 端口
    config = {
        'host': os.getenv('DORIS_HOST', 'localhost'),
        'port': 9032,  # FE-02 端口
        'user': os.getenv('DORIS_USER', 'root'),
        'password': os.getenv('DORIS_PASSWORD', ''),
        'charset': 'utf8mb4'
    }
    
    print('正在测试 doris-fe-02 连接...')
    print(f'连接信息: {config["user"]}@{config["host"]}:{config["port"]}')
    
    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    
    cursor.execute('SELECT VERSION()')
    version = cursor.fetchone()
    print(f'[OK] 连接成功！Doris 版本: {version[0]}')
    
    cursor.execute('SHOW DATABASES')
    databases = cursor.fetchall()
    print(f'\n可用数据库:')
    for db in databases:
        print(f'  - {db[0]}')
    
    cursor.close()
    conn.close()
    
except ImportError:
    print('[ERROR] pymysql 未安装，请运行: pip install pymysql')
except Exception as e:
    print(f'[ERROR] 连接失败: {e}')
