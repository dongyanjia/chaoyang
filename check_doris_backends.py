"""
检查 Doris Backend 节点状态

使用方法:
    python check_doris_backends.py
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
    
    print('正在检查 Doris Backend 节点状态...')
    
    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    
    # 查询 Backend 节点状态
    cursor.execute("SHOW BACKENDS")
    backends = cursor.fetchall()
    
    print(f'\n找到 {len(backends)} 个 Backend 节点:')
    print('-' * 100)
    
    if backends:
        # 获取列名
        columns = [desc[0] for desc in cursor.description]
        # 查找关键列
        key_cols = ['BackendId', 'Host', 'Alive', 'SystemDecommissioned', 'LastHeartbeat']
        col_indices = [columns.index(col) if col in columns else None for col in key_cols]
        
        # 显示表头
        header = ' | '.join([col for col in key_cols if columns.index(col) < len(columns)])
        print(header)
        print('-' * 100)
        
        for backend in backends:
            # 显示关键信息
            values = []
            for col in key_cols:
                if col in columns:
                    idx = columns.index(col)
                    if idx < len(backend):
                        values.append(str(backend[idx]))
            print(' | '.join(values))
    else:
        print('没有找到 Backend 节点！')
        print('\n请检查:')
        print('1. BE 容器是否运行: docker ps | findstr doris-be')
        print('2. BE 节点是否已注册到 FE')
        print('3. 网络连接是否正常')
    
    cursor.close()
    conn.close()
    
except ImportError:
    print('[ERROR] pymysql 未安装，请运行: pip install pymysql')
except Exception as e:
    print(f'[ERROR] 检查失败: {e}')
    import traceback
    traceback.print_exc()
