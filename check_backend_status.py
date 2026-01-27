"""
检查后端服务状态和数据库连接

使用方法:
    python check_backend_status.py
"""
import sys
import os
import socket
import requests

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_port(host='localhost', port=8000):
    """检查端口是否被占用"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def check_backend_api():
    """检查后端 API 是否响应"""
    try:
        response = requests.get('http://localhost:8000/api/people', timeout=5)
        return response.status_code == 200, response.status_code
    except requests.exceptions.ConnectionError:
        return False, "连接被拒绝"
    except requests.exceptions.Timeout:
        return False, "超时"
    except Exception as e:
        return False, str(e)

def check_database_connection():
    """检查数据库连接"""
    try:
        sys.path.insert(0, 'backend')
        from database import Database
        
        db = Database()
        db.connect()
        
        # 尝试查询
        count = db.get_people_count()
        db.disconnect()
        
        return True, f"连接成功，人员总数: {count}"
    except Exception as e:
        return False, str(e)

print('=' * 60)
print('后端服务状态检查')
print('=' * 60)

# 1. 检查端口
print('\n[1] 检查后端服务端口 (8000)...')
if check_port('localhost', 8000):
    print('  ✓ 端口 8000 正在监听')
else:
    print('  ✗ 端口 8000 未被占用（后端服务未运行）')
    print('  请运行: python backend/run.py')

# 2. 检查 API
print('\n[2] 检查后端 API...')
try:
    api_ok, status = check_backend_api()
    if api_ok:
        print(f'  ✓ API 响应正常 (状态码: {status})')
    else:
        print(f'  ✗ API 无响应: {status}')
except ImportError:
    print('  ⚠ requests 未安装，跳过 API 检查')
    print('  安装: pip install requests')

# 3. 检查数据库连接
print('\n[3] 检查数据库连接...')
db_ok, db_msg = check_database_connection()
if db_ok:
    print(f'  ✓ {db_msg}')
else:
    print(f'  ✗ 数据库连接失败: {db_msg}')
    print('\n可能的原因:')
    print('  1. Doris FE 服务未启动')
    print('  2. BE 节点状态异常')
    print('  3. 数据库配置错误')

print('\n' + '=' * 60)
print('检查完成')
print('=' * 60)
