"""
测试后端是否已切换到 Doris 数据库

使用方法:
    python test_backend_doris.py
"""
import sys
import os

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print('=' * 60)
print('检查后端是否已切换到 Doris 数据库')
print('=' * 60)

# 1. 检查 database.py 文件
print('\n[1] 检查 database.py 配置...')
try:
    sys.path.insert(0, 'backend')
    from database import Database, DB_CONFIG
    
    print(f'✓ 数据库模块导入成功')
    print(f'  数据库类型: Doris (使用 pymysql)')
    print(f'  连接配置:')
    print(f'    - Host: {DB_CONFIG["host"]}')
    print(f'    - Port: {DB_CONFIG["port"]}')
    print(f'    - Database: {DB_CONFIG["database"]}')
    print(f'    - User: {DB_CONFIG["user"]}')
    
    # 检查是否使用 pymysql
    import database
    if 'pymysql' in str(database.__file__):
        print(f'  ✓ 使用 pymysql 连接器')
    else:
        # 检查导入
        import inspect
        source = inspect.getsource(database)
        if 'import pymysql' in source or 'import pymysql' in source:
            print(f'  ✓ 使用 pymysql 连接器')
        else:
            print(f'  ✗ 未找到 pymysql 导入')
    
except Exception as e:
    print(f'✗ 导入失败: {e}')
    import traceback
    traceback.print_exc()

# 2. 测试数据库连接
print('\n[2] 测试数据库连接...')
try:
    db = Database()
    db.connect()
    print('✓ 数据库连接成功')
    
    # 测试查询
    cursor = db.connection.cursor()
    cursor.execute('SELECT DATABASE()')
    current_db = cursor.fetchone()
    print(f'  当前数据库: {current_db[0] if current_db else "未知"}')
    
    cursor.execute('SELECT VERSION()')
    version = cursor.fetchone()
    print(f'  Doris 版本: {version[0] if version else "未知"}')
    
    cursor.close()
    db.disconnect()
    
except Exception as e:
    print(f'✗ 数据库连接失败: {e}')
    import traceback
    traceback.print_exc()

# 3. 检查表是否存在
print('\n[3] 检查表结构...')
try:
    db = Database()
    db.connect()
    cursor = db.connection.cursor()
    
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    
    expected_tables = ['people', 'key_persons', 'movements', 'map_data', 'trend_data', 'flow_statistics', 'local_people']
    table_names = [t[0] for t in tables]
    
    print(f'  找到 {len(tables)} 个表')
    for table in expected_tables:
        if table in table_names:
            print(f'  ✓ {table}')
        else:
            print(f'  ✗ {table} (缺失)')
    
    cursor.close()
    db.disconnect()
    
except Exception as e:
    print(f'✗ 检查表失败: {e}')

# 4. 检查后端 API 是否使用正确的数据库
print('\n[4] 检查后端 API 配置...')
try:
    import app
    print('✓ Flask 应用导入成功')
    
    # 检查 app.py 是否导入 Database
    import inspect
    source = inspect.getsource(app)
    if 'from database import Database' in source:
        print('  ✓ app.py 从 database 模块导入 Database')
    else:
        print('  ✗ app.py 未从 database 模块导入 Database')
    
    # 检查 get_db 函数
    if hasattr(app, 'get_db'):
        print('  ✓ get_db 函数存在')
    else:
        print('  ✗ get_db 函数不存在')
    
except Exception as e:
    print(f'✗ 检查 API 配置失败: {e}')

# 5. 测试 API 端点（如果后端正在运行）
print('\n[5] 测试后端 API...')
try:
    import requests
    base_url = 'http://localhost:8000'
    
    # 测试健康检查或简单端点
    endpoints = ['/api/people', '/api/stats', '/api/situation?period=week']
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=2)
            if response.status_code == 200:
                print(f'  ✓ {endpoint} - 200 OK')
            elif response.status_code == 404:
                print(f'  ✗ {endpoint} - 404 Not Found')
            else:
                print(f'  ⚠ {endpoint} - {response.status_code}')
        except requests.exceptions.ConnectionError:
            print(f'  ✗ {endpoint} - 连接失败（后端可能未运行）')
            break
        except Exception as e:
            print(f'  ✗ {endpoint} - 错误: {e}')
            
except ImportError:
    print('  ⚠ requests 库未安装，跳过 API 测试')
except Exception as e:
    print(f'  ✗ API 测试失败: {e}')

print('\n' + '=' * 60)
print('检查完成')
print('=' * 60)
