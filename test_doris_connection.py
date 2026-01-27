"""
测试 Doris 连接脚本

使用方法:
    python test_doris_connection.py
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
    # 注意：根据 docker-compose.yaml，FE 节点的 MySQL 查询端口映射为 9031, 9032, 9033
    config = {
        'host': os.getenv('DORIS_HOST', 'localhost'),
        'port': int(os.getenv('DORIS_PORT', 9031)),
        'user': os.getenv('DORIS_USER', 'root'),
        'password': os.getenv('DORIS_PASSWORD', ''),
        'charset': 'utf8mb4'
    }
    
    print('正在测试 Doris 连接...')
    print(f'连接信息: {config["user"]}@{config["host"]}:{config["port"]}')
    
    # 尝试连接（不指定数据库）
    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    
    # 测试查询
    cursor.execute('SELECT VERSION()')
    version = cursor.fetchone()
    print(f'[OK] 连接成功！Doris 版本: {version[0]}')
    
    # 列出数据库
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
    print('\n请确保:')
    print('1. Docker Desktop 已启动')
    print('2. Doris 服务已运行: docker-compose ps')
    print('3. 等待 Doris FE 完全启动（约1-2分钟）')
