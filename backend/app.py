"""
Flask应用主文件
提供RESTful API接口，用于全国流感人群流动监测系统

主要功能：
- 人员信息管理（CRUD操作）
- 统计数据查询
- 态势感知数据获取
- 重点人员管理
- 地图数据同步
- 静态资源服务（头像图片）

作者：系统开发团队
版本：1.0.0
"""
from flask import Flask, jsonify, request, send_from_directory, g
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
import json
from datetime import datetime, timedelta
import random
import hashlib
import secrets
from database import Database
from map_sync import sync_map_data_from_people, sync_people_from_map_data, get_province_from_region

# pandas导入（用于Excel/CSV文件解析）
PANDAS_AVAILABLE = False
pd = None
# #region agent log
import json
import os
import sys
log_path = r'f:\all\projects\chaoyangV1.0.1\.cursor\debug.log'
try:
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps({
            'id': f'log_{int(__import__("time").time() * 1000)}',
            'timestamp': int(__import__("time").time() * 1000),
            'location': 'app.py:29',
            'message': '开始导入pandas',
            'data': {'python_executable': sys.executable, 'python_version': sys.version},
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'A'
        }, ensure_ascii=False) + '\n')
except: pass
# #endregion
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
    print(f"[OK] pandas导入成功，版本: {pd.__version__}")
    # #region agent log
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'id': f'log_{int(__import__("time").time() * 1000)}',
                'timestamp': int(__import__("time").time() * 1000),
                'location': 'app.py:35',
                'message': 'pandas导入成功',
                'data': {'version': pd.__version__, 'PANDAS_AVAILABLE': True},
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'A'
            }, ensure_ascii=False) + '\n')
    except: pass
    # #endregion
    # #region agent log
    try:
        import openpyxl
        openpyxl_available = True
    except:
        openpyxl_available = False
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'id': f'log_{int(__import__("time").time() * 1000)}',
                'timestamp': int(__import__("time").time() * 1000),
                'location': 'app.py:48',
                'message': '检查openpyxl',
                'data': {'openpyxl_available': openpyxl_available},
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'B'
            }, ensure_ascii=False) + '\n')
    except: pass
    # #endregion
except ImportError as e:
    PANDAS_AVAILABLE = False
    pd = None
    print(f"[WARN] pandas未安装（Excel/CSV导入功能将不可用）: {e}")
    print("提示: 请运行 'pip install pandas==2.1.4' 安装pandas")
    # #region agent log
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'id': f'log_{int(__import__("time").time() * 1000)}',
                'timestamp': int(__import__("time").time() * 1000),
                'location': 'app.py:58',
                'message': 'pandas ImportError',
                'data': {'error': str(e), 'PANDAS_AVAILABLE': False},
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'A'
            }, ensure_ascii=False) + '\n')
    except: pass
    # #endregion
except Exception as e:
    PANDAS_AVAILABLE = False
    pd = None
    print(f"[WARN] pandas导入失败（Excel/CSV导入功能将不可用）: {e}")
    import traceback
    traceback.print_exc()
    # #region agent log
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'id': f'log_{int(__import__("time").time() * 1000)}',
                'timestamp': int(__import__("time").time() * 1000),
                'location': 'app.py:70',
                'message': 'pandas其他异常',
                'data': {'error': str(e), 'error_type': type(e).__name__, 'PANDAS_AVAILABLE': False},
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'C'
            }, ensure_ascii=False) + '\n')
    except: pass
    # #endregion

# 创建Flask应用实例
app = Flask(__name__)
# 启用CORS跨域支持，允许前端访问API
CORS(app)

# 获取数据库连接（线程安全）
def get_db():
    """获取当前线程的数据库连接"""
    if 'db' not in g:
        g.db = Database()
        g.db.connect()
    return g.db

# 关闭数据库连接
@app.teardown_appcontext
def close_db(error):
    """请求结束时关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.disconnect()

# 根路由 - 显示API信息
@app.route('/', methods=['GET'])
def index():
    """根路由，显示API信息"""
    return jsonify({
        'message': '全国流感人群流动监测系统 API',
        'version': '1.0.0',
        'endpoints': {
            'stats': '/api/stats',
            'people': '/api/people',
            'situation': '/api/situation',
            'avatars': '/api/avatars/<filename>'
        }
    })

# 静态文件服务 - 提供头像图片
@app.route('/api/avatars/<filename>')
def serve_avatar(filename):
    """提供头像图片"""
    avatars_dir = os.path.join(os.path.dirname(__file__), 'avatars')
    return send_from_directory(avatars_dir, filename)

# 简单的用户数据库（实际项目中应该使用数据库）
# 默认用户：admin/admin123
USERS = {
    'admin': {
        'password': 'admin123',  # 实际项目中应该使用hash
        'username': 'admin',
        'key': 'ADMIN-2024-001',  # 用户key号
        'role': 'admin'
    }
}

# 生成token的简单函数（实际项目中应该使用JWT）
def generate_token(username):
    """生成简单的token"""
    timestamp = str(int(datetime.now().timestamp()))
    token_string = f"{username}:{timestamp}:{secrets.token_hex(16)}"
    return hashlib.sha256(token_string.encode()).hexdigest()

# 登录接口
@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400
        
        # 检查用户是否存在
        user = USERS.get(username)
        if not user:
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
        
        # 检查密码（实际项目中应该使用hash比较）
        if user['password'] != password:
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
        
        # 生成token
        token = generate_token(username)
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'username': user['username'],
                'key': user.get('key', f'USER-{secrets.token_hex(4).upper()}'),
                'role': user.get('role', 'user')
            },
            'message': '登录成功'
        })
    except Exception as e:
        print(f'登录错误: {e}')
        return jsonify({
            'success': False,
            'message': '登录失败，请稍后重试'
        }), 500

# 登出接口
@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """用户登出"""
    return jsonify({
        'success': True,
        'message': '登出成功'
    })

# 获取当前用户信息
@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """获取当前登录用户信息"""
    # 从请求头获取token
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({
            'success': False,
            'message': '未授权'
        }), 401
    
    # 简单验证（实际项目中应该验证token的有效性）
    token = auth_header.replace('Bearer ', '')
    if not token:
        return jsonify({
            'success': False,
            'message': '未授权'
        }), 401
    
    # 返回默认用户信息（实际项目中应该从token解析用户信息）
    return jsonify({
        'success': True,
        'user': {
            'username': 'admin',
            'key': 'ADMIN-2024-001',
            'role': 'admin'
        }
    })

# 初始化数据库（如果为空则生成假数据）
def init_database_if_empty():
    """如果数据库为空，则初始化假数据"""
    db = get_db()
    people = db.get_people()
    
    # 检查是否需要初始化
    need_init = len(people) == 0
    
    # 检查趋势数据是否存在
    if not need_init:
        trend_data = db.get_trend_data()
        if len(trend_data) == 0:
            need_init = True
    
    if need_init:
        print('数据库为空或缺少数据，正在初始化假数据...')
        # 导入初始化脚本
        from init_database import init_database
        init_database(clear_existing=False, people_count=8000, movements_count=16000)
        print('假数据初始化完成！')


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计数据"""
    db = get_db()
    init_database_if_empty()
    
    # 先同步地图数据（根据实际人员数据更新地图）
    try:
        sync_map_data_from_people(db)
        # 根据地图数据补充人员（如果地图人数大于实际人数）
        sync_people_from_map_data(db)
    except Exception as e:
        print(f'同步地图数据失败: {e}')
    
    # 从数据库获取统计数据
    stats = db.get_stats()
    
    # 获取最近10条流动记录作为动态
    movements = db.get_movements()
    recent_activities = []
    for movement in movements[:10]:
        activity = {
            'id': movement['id'],
            'name': movement['name'],
            'avatar': movement['avatar'],
            'action': f"从{movement['from']}流动到{movement['to']}",
            'time': movement['time']
        }
        recent_activities.append(activity)
    
    # 从数据库获取地图数据（已同步）
    map_data = db.get_map_data()
    
    # 如果地图数据为空，生成默认数据
    if not map_data:
        from init_database import PROVINCES
        map_data = []
        for province, (min_val, max_val) in PROVINCES.items():
            value = random.randint(min_val, max_val)
            map_data.append({'name': province, 'value': value})
            db.update_map_data(province, value)
    
    # 获取各省确诊人数排名
    try:
        province_ranking = db.get_province_confirmed_ranking()
    except Exception as e:
        print(f'获取省份排名失败: {e}')
        import traceback
        traceback.print_exc()
        province_ranking = []
    
    return jsonify({
        'stats': stats,
        'recentActivities': recent_activities,
        'mapData': map_data,
        'provinceRanking': province_ranking
    })

@app.route('/api/people', methods=['GET'])
def get_people():
    """获取人员列表，支持分页"""
    db = get_db()
    init_database_if_empty()
    
    # 获取分页参数
    page = request.args.get('page', type=int)
    page_size = request.args.get('page_size', type=int)
    
    # 如果提供了分页参数，使用分页查询
    if page is not None and page_size is not None:
        people = db.get_people(page=page, page_size=page_size)
        total_count = db.get_people_count()
        return jsonify({
            'data': people,
            'pagination': {
            'page': page,
            'page_size': page_size,
                'total': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        })
    else:
        # 兼容旧接口，返回所有数据
        people = db.get_people()
        return jsonify(people)

@app.route('/api/people', methods=['POST'])
def create_person():
    """创建人员"""
    db = get_db()
    init_database_if_empty()
    data = request.json
    
    # 如果没有提供头像，随机分配一个
    if not data.get('avatar'):
        data['avatar'] = f'/api/avatars/avatar_{random.randint(1, 20)}.jpg'
    
    new_person = db.create_person(data)
    
    # 同步地图数据
    try:
        sync_map_data_from_people(db)
    except Exception as e:
        print(f'同步地图数据失败: {e}')
    
    return jsonify(new_person), 201

@app.route('/api/test-connection', methods=['GET', 'POST'])
def test_connection():
    """测试连接路由"""
    print('=' * 50)
    print('=== 测试连接请求 ===')
    print('请求方法:', request.method)
    print('请求内容类型:', request.content_type)
    print('请求头:', dict(request.headers))
    print('=' * 50)
    return jsonify({'message': '后端连接正常', 'method': request.method})

@app.route('/api/local-people/import-file', methods=['POST', 'OPTIONS', 'GET'])
def import_local_people_file():
    """导入人员数据到本地人员库（支持JSON/Excel/CSV文件）"""
    # #region agent log
    import json
    import os
    log_path = r'f:\all\projects\chaoyangV1.0.1\.cursor\debug.log'
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'id': f'log_{int(__import__("time").time() * 1000)}',
                'timestamp': int(__import__("time").time() * 1000),
                'location': 'app.py:229',
                'message': '路由函数被调用',
                'data': {'method': request.method, 'path': request.path},
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'A'
            }, ensure_ascii=False) + '\n')
    except: pass
    # #endregion
    
    # 处理CORS预检请求
    if request.method == 'OPTIONS':
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'id': f'log_{int(__import__("time").time() * 1000)}',
                    'timestamp': int(__import__("time").time() * 1000),
                    'location': 'app.py:233',
                    'message': 'OPTIONS请求处理',
                    'data': {},
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A'
                }, ensure_ascii=False) + '\n')
        except: pass
        # #endregion
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    # 处理GET请求（用于测试或错误提示）
    if request.method == 'GET':
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'id': f'log_{int(__import__("time").time() * 1000)}',
                    'timestamp': int(__import__("time").time() * 1000),
                    'location': 'app.py:274',
                    'message': 'GET请求处理',
                    'data': {},
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A'
                }, ensure_ascii=False) + '\n')
        except: pass
        # #endregion
        return jsonify({
            'error': '此接口仅支持POST请求',
            'message': '请使用POST方法上传文件',
            'usage': '使用前端页面的"确认导入"按钮上传文件'
        }), 405
    
    try:
        import sys
        sys.stdout.flush()  # 强制刷新输出缓冲区
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'id': f'log_{int(__import__("time").time() * 1000)}',
                    'timestamp': int(__import__("time").time() * 1000),
                    'location': 'app.py:288',
                    'message': 'POST请求进入try块',
                    'data': {'method': request.method, 'content_type': request.content_type, 'has_files': bool(request.files)},
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'B'
                }, ensure_ascii=False) + '\n')
        except: pass
        # #endregion
        
        print('=' * 50, flush=True)
        print('=== 本地人员库文件导入请求开始 ===', flush=True)
        print('请求方法:', request.method, flush=True)
        print('请求内容类型:', request.content_type, flush=True)
        print('请求头:', dict(request.headers), flush=True)
        print('=' * 50, flush=True)
        print('请求文件:', request.files, flush=True)
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'id': f'log_{int(__import__("time").time() * 1000)}',
                    'timestamp': int(__import__("time").time() * 1000),
                    'location': 'app.py:323',
                    'message': '检查request.files',
                    'data': {'has_files': bool(request.files), 'files_keys': list(request.files.keys()) if request.files else []},
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'C'
                }, ensure_ascii=False) + '\n')
        except: pass
        # #endregion
        
        db = get_db()

        if 'file' not in request.files:
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'id': f'log_{int(__import__("time").time() * 1000)}',
                        'timestamp': int(__import__("time").time() * 1000),
                        'location': 'app.py:327',
                        'message': '错误：请求中没有file字段',
                        'data': {'available_files': list(request.files.keys())},
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'C'
                    }, ensure_ascii=False) + '\n')
            except: pass
            # #endregion
            print('错误：请求中没有file字段', flush=True)
            print('可用的文件字段:', list(request.files.keys()), flush=True)
            print('请求表单数据:', request.form, flush=True)
            return jsonify({'error': '未选择文件', 'available_files': list(request.files.keys())}), 400

        file = request.files['file']
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'id': f'log_{int(__import__("time").time() * 1000)}',
                    'timestamp': int(__import__("time").time() * 1000),
                    'location': 'app.py:333',
                    'message': '文件对象获取成功',
                    'data': {'filename': file.filename if file else None},
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'D'
                }, ensure_ascii=False) + '\n')
        except: pass
        # #endregion
        print('文件对象:', file, flush=True)
        print('文件名:', file.filename, flush=True)
        print('文件大小:', file.content_length if hasattr(file, 'content_length') else '未知', flush=True)
        
        if file.filename == '' or file.filename is None:
            print('错误：文件名为空', flush=True)
            return jsonify({'error': '未选择文件'}), 400
        
        # 检查文件内容是否为空
        file.seek(0, 2)  # 移动到文件末尾
        file_size = file.tell()
        file.seek(0)  # 重置到文件开头
        print('文件实际大小:', file_size, 'bytes', flush=True)
        
        if file_size == 0:
            print('错误：文件内容为空', flush=True)
            return jsonify({'error': '文件内容为空'}), 400

        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        print('文件扩展名:', file_ext, flush=True)
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'id': f'log_{int(__import__("time").time() * 1000)}',
                    'timestamp': int(__import__("time").time() * 1000),
                    'location': 'app.py:432',
                    'message': '文件扩展名检测',
                    'data': {'filename': filename, 'file_ext': file_ext, 'is_excel': file_ext in ['.xlsx', '.xls']},
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'D'
                }, ensure_ascii=False) + '\n')
        except: pass
        # #endregion

        people_list = []

        # 根据文件类型解析数据
        if file_ext == '.json':
            # JSON文件
            try:
                file_content = file.read()
                if isinstance(file_content, bytes):
                    file_content = file_content.decode('utf-8')
                data = json.loads(file_content)
                if isinstance(data, dict):
                    people_list = [data]
                elif isinstance(data, list):
                    people_list = data
                else:
                    return jsonify({'error': 'JSON格式错误，应为对象或数组'}), 400
            except json.JSONDecodeError as e:
                return jsonify({'error': f'JSON解析错误：{str(e)}'}), 400
            except UnicodeDecodeError as e:
                return jsonify({'error': f'文件编码错误：{str(e)}'}), 400

        elif file_ext in ['.xlsx', '.xls']:
            # Excel文件
            # 动态检查pandas是否可用（因为可能在启动后安装）
            pandas_available_now = PANDAS_AVAILABLE
            pd_module = pd
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'id': f'log_{int(__import__("time").time() * 1000)}',
                        'timestamp': int(__import__("time").time() * 1000),
                        'location': 'app.py:524',
                        'message': '检查pandas初始状态',
                        'data': {'PANDAS_AVAILABLE': PANDAS_AVAILABLE, 'pd_is_none': pd is None},
                        'sessionId': 'debug-session',
                        'runId': 'post-fix-v2',
                        'hypothesisId': 'A'
                    }, ensure_ascii=False) + '\n')
            except: pass
            # #endregion
            if not pandas_available_now or pd_module is None:
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'id': f'log_{int(__import__("time").time() * 1000)}',
                            'timestamp': int(__import__("time").time() * 1000),
                            'location': 'app.py:540',
                            'message': '尝试动态导入pandas',
                            'data': {},
                            'sessionId': 'debug-session',
                            'runId': 'post-fix-v2',
                            'hypothesisId': 'A'
                        }, ensure_ascii=False) + '\n')
                except: pass
                # #endregion
                try:
                    import sys
                    import pandas as pd_module
                    pandas_available_now = True
                    # #region agent log
                    try:
                        with open(log_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({
                                'id': f'log_{int(__import__("time").time() * 1000)}',
                                'timestamp': int(__import__("time").time() * 1000),
                                'location': 'app.py:555',
                                'message': '运行时动态导入pandas成功',
                                'data': {'version': pd_module.__version__, 'pd_module_type': str(type(pd_module)), 'python_executable': sys.executable},
                                'sessionId': 'debug-session',
                                'runId': 'post-fix-v2',
                                'hypothesisId': 'A'
                            }, ensure_ascii=False) + '\n')
                    except: pass
                    # #endregion
                except ImportError as e:
                    pandas_available_now = False
                    # #region agent log
                    try:
                        import sys
                        with open(log_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({
                                'id': f'log_{int(__import__("time").time() * 1000)}',
                                'timestamp': int(__import__("time").time() * 1000),
                                'location': 'app.py:570',
                                'message': '运行时动态导入pandas失败 - ImportError',
                                'data': {'error': str(e), 'error_type': type(e).__name__, 'python_executable': sys.executable, 'sys_path': sys.path[:3]},
                                'sessionId': 'debug-session',
                                'runId': 'post-fix-v2',
                                'hypothesisId': 'A'
                            }, ensure_ascii=False) + '\n')
                    except: pass
                    # #endregion
                except Exception as e:
                    pandas_available_now = False
                    # #region agent log
                    try:
                        with open(log_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({
                                'id': f'log_{int(__import__("time").time() * 1000)}',
                                'timestamp': int(__import__("time").time() * 1000),
                                'location': 'app.py:585',
                                'message': '运行时动态导入pandas失败 - 其他异常',
                                'data': {'error': str(e), 'error_type': type(e).__name__},
                                'sessionId': 'debug-session',
                                'runId': 'post-fix-v2',
                                'hypothesisId': 'A'
                            }, ensure_ascii=False) + '\n')
                    except: pass
                    # #endregion
            
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'id': f'log_{int(__import__("time").time() * 1000)}',
                        'timestamp': int(__import__("time").time() * 1000),
                        'location': 'app.py:456',
                        'message': 'Excel文件处理开始',
                        'data': {'file_ext': file_ext, 'PANDAS_AVAILABLE_startup': PANDAS_AVAILABLE, 'pandas_available_now': pandas_available_now, 'pd_is_none': pd_module is None},
                        'sessionId': 'debug-session',
                        'runId': 'post-fix',
                        'hypothesisId': 'A'
                    }, ensure_ascii=False) + '\n')
            except: pass
            # #endregion
            
            if not pandas_available_now or pd_module is None:
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'id': f'log_{int(__import__("time").time() * 1000)}',
                            'timestamp': int(__import__("time").time() * 1000),
                            'location': 'app.py:470',
                            'message': 'pandas不可用，返回错误',
                            'data': {'pandas_available_now': pandas_available_now},
                            'sessionId': 'debug-session',
                            'runId': 'post-fix',
                            'hypothesisId': 'A'
                        }, ensure_ascii=False) + '\n')
                except: pass
                # #endregion
                return jsonify({'error': 'Excel文件解析需要pandas库，请安装：pip install pandas openpyxl'}), 400
            try:
                import io
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'id': f'log_{int(__import__("time").time() * 1000)}',
                            'timestamp': int(__import__("time").time() * 1000),
                            'location': 'app.py:490',
                            'message': '准备读取Excel文件',
                            'data': {'pd_module_available': pd_module is not None},
                            'sessionId': 'debug-session',
                            'runId': 'post-fix',
                            'hypothesisId': 'B'
                        }, ensure_ascii=False) + '\n')
                except: pass
                # #endregion
                file_content = file.read()
                file_stream = io.BytesIO(file_content)
                # #region agent log
                try:
                    import openpyxl
                    openpyxl_check = True
                except ImportError:
                    openpyxl_check = False
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'id': f'log_{int(__import__("time").time() * 1000)}',
                            'timestamp': int(__import__("time").time() * 1000),
                            'location': 'app.py:503',
                            'message': '调用pd.read_excel前检查openpyxl',
                            'data': {'openpyxl_available': openpyxl_check},
                            'sessionId': 'debug-session',
                            'runId': 'post-fix',
                            'hypothesisId': 'B'
                        }, ensure_ascii=False) + '\n')
                except: pass
                # #endregion
                df = pd_module.read_excel(file_stream)
                print(f'[DEBUG] Excel文件读取成功，共 {len(df)} 行，列名: {list(df.columns)}')
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'id': f'log_{int(__import__("time").time() * 1000)}',
                            'timestamp': int(__import__("time").time() * 1000),
                            'location': 'app.py:516',
                            'message': 'Excel文件读取成功',
                            'data': {'row_count': len(df), 'columns': list(df.columns)},
                            'sessionId': 'debug-session',
                            'runId': 'post-fix',
                            'hypothesisId': 'B'
                        }, ensure_ascii=False) + '\n')
                except: pass
                # #endregion
                
                # 处理idCard列，防止Excel将其读取为科学计数法
                def convert_idcard(value):
                    """转换idCard字段，处理科学计数法和数字格式"""
                    if pd_module.isna(value):
                        return ''
                    if isinstance(value, (int, float)):
                        # 如果是数字，转换为字符串（避免科学计数法）
                        return str(int(value))
                    if isinstance(value, str):
                        # 处理科学计数法格式
                        if 'E+' in value.upper() or 'e+' in value.lower():
                            try:
                                return str(int(float(value)))
                            except:
                                return value
                        # 处理空值
                        if value.strip() == '' or value.lower() == 'nan':
                            return ''
                        return value
                    return str(value) if value else ''
                
                if 'idCard' in df.columns:
                    df['idCard'] = df['idCard'].apply(convert_idcard)
                elif 'id_card' in df.columns:
                    df['id_card'] = df['id_card'].apply(convert_idcard)
                
                # 删除所有列都为空的行
                df = df.dropna(how='all')
                print(f'[DEBUG] 删除空行后，剩余 {len(df)} 行')
                
                people_list = df.to_dict('records')
                print(f'[DEBUG] 转换后的第一条数据: {people_list[0] if people_list else "无数据"}', flush=True)
                if len(people_list) > 0:
                    print(f'[DEBUG] 第一条数据的name字段值: {people_list[0].get("name")}, 类型: {type(people_list[0].get("name"))}', flush=True)
                    print(f'[DEBUG] 第一条数据的所有字段: {list(people_list[0].keys())}', flush=True)
                    print(f'[DEBUG] 第一条数据完整内容: {people_list[0]}', flush=True)
                
                # 标准化字段名：处理中英文、大小写变体
                for idx, person in enumerate(people_list):
                    print(f'[DEBUG] 处理第 {idx+1} 条数据，标准化前name字段: {person.get("name")}', flush=True)
                    # 处理姓名字段（确保name字段存在且有效）
                    name_found = False
                    for name_key in ['name', 'Name', 'NAME', '姓名', '名字']:
                        if name_key in person:
                            name_val = person[name_key]
                            # 检查值是否有效（不是NaN、空字符串等）
                            if name_val is not None and not pd_module.isna(name_val):
                                name_str = str(name_val).strip()
                                if name_str and name_str.lower() not in ['nan', 'none', '']:
                                    if name_key != 'name':
                                        person['name'] = name_val
                                    name_found = True
                                    break
                    
                    # 如果name字段存在但值为NaN，清理它
                    if 'name' in person and (person['name'] is None or pd_module.isna(person['name'])):
                        del person['name']
                    
                    # 处理身份证字段（确保是字符串格式）
                    id_card_value = None
                    for id_key in ['idCard', 'id_card', '身份证', '身份证号', 'IdCard', 'ID_CARD']:
                        if id_key in person:
                            id_card_value = person[id_key]
                            # 处理科学计数法或数字格式
                            if isinstance(id_card_value, (int, float)) and not pd_module.isna(id_card_value):
                                id_card_value = str(int(id_card_value))
                            elif isinstance(id_card_value, str) and 'E+' in id_card_value.upper():
                                try:
                                    id_card_value = str(int(float(id_card_value)))
                                except:
                                    pass
                            if id_key != 'idCard':
                                person['idCard'] = id_card_value
                                if id_key in person:
                                    del person[id_key]
                            break
                    
                    # 处理字段名映射（Excel列名可能是下划线或驼峰）
                    if 'id_card' in person and 'idCard' not in person:
                        person['idCard'] = person.pop('id_card')
                    if 'last_update' in person and 'lastUpdate' not in person:
                        person['lastUpdate'] = person.pop('last_update')
                    if 'education_history' in person and 'educationHistory' not in person:
                        person['educationHistory'] = person.pop('education_history')
                    if 'work_history' in person and 'workHistory' not in person:
                        person['workHistory'] = person.pop('work_history')
                    if 'social_media' in person and 'socialMedia' not in person:
                        person['socialMedia'] = person.pop('social_media')
                    if 'visit_records' in person and 'visitRecords' not in person:
                        person['visitRecords'] = person.pop('visit_records')
                    if 'flight_records' in person and 'flightRecords' not in person:
                        person['flightRecords'] = person.pop('flight_records')
                    if 'train_records' in person and 'trainRecords' not in person:
                        person['trainRecords'] = person.pop('train_records')
                    if 'visa_type' in person and 'visaType' not in person:
                        person['visaType'] = person.pop('visa_type')
                print(f'[DEBUG] Excel数据转换完成，第一条数据示例: {people_list[0] if people_list else "无数据"}')
            except Exception as e:
                import traceback
                traceback.print_exc()
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'id': f'log_{int(__import__("time").time() * 1000)}',
                            'timestamp': int(__import__("time").time() * 1000),
                            'location': 'app.py:607',
                            'message': 'Excel文件解析异常',
                            'data': {'error': str(e), 'error_type': type(e).__name__, 'traceback': traceback.format_exc()},
                            'sessionId': 'debug-session',
                            'runId': 'post-fix',
                            'hypothesisId': 'B'
                        }, ensure_ascii=False) + '\n')
                except: pass
                # #endregion
                return jsonify({'error': f'Excel文件解析错误：{str(e)}'}), 400

        elif file_ext == '.csv':
            # CSV文件
            # 动态检查pandas是否可用（因为可能在启动后安装）
            pandas_available_csv = PANDAS_AVAILABLE
            pd_module_csv = pd
            if not pandas_available_csv or pd_module_csv is None:
                try:
                    import pandas as pd_module_csv
                    pandas_available_csv = True
                except ImportError:
                    pandas_available_csv = False
            
            if not pandas_available_csv or pd_module_csv is None:
                return jsonify({'error': 'CSV文件解析需要pandas库，请安装：pip install pandas'}), 400
            try:
                import io
                file_content = file.read()
                encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
                df = None
                for encoding in encodings:
                    try:
                        file_stream = io.BytesIO(file_content)
                        df = pd_module_csv.read_csv(file_stream, encoding=encoding)
                        print(f'CSV文件读取成功（编码：{encoding}），共{len(df)}行')
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is None:
                    return jsonify({'error': 'CSV文件编码不支持，请使用UTF-8或GBK编码'}), 400
                
                print(f'[DEBUG] CSV文件读取成功，共 {len(df)} 行，列名: {list(df.columns)}')
                # 删除所有列都为空的行
                df = df.dropna(how='all')
                print(f'[DEBUG] 删除空行后，剩余 {len(df)} 行')
                
                people_list = df.to_dict('records')
                
                # 标准化字段名：处理中英文、大小写变体
                for person in people_list:
                    # 处理姓名字段（确保name字段存在且有效）
                    name_found = False
                    for name_key in ['name', 'Name', 'NAME', '姓名', '名字']:
                        if name_key in person:
                            name_val = person[name_key]
                            # 检查值是否有效（不是NaN、空字符串等）
                            if name_val is not None and not pd_module_csv.isna(name_val):
                                name_str = str(name_val).strip()
                                if name_str and name_str.lower() not in ['nan', 'none', '']:
                                    if name_key != 'name':
                                        person['name'] = name_val
                                    name_found = True
                                    break
                    
                    # 如果name字段存在但值为NaN，清理它
                    if 'name' in person and (person['name'] is None or pd_module_csv.isna(person['name'])):
                        del person['name']
                    
                    # 处理身份证字段
                    for id_key in ['身份证', '身份证号', 'IdCard', 'ID_CARD']:
                        if id_key in person:
                            if 'idCard' not in person and 'id_card' not in person:
                                person['idCard'] = person.pop(id_key)
                            break
                    
                    # 处理字段名映射（CSV列名可能是下划线或驼峰）
                    if 'id_card' in person and 'idCard' not in person:
                        person['idCard'] = person.pop('id_card')
                    if 'last_update' in person and 'lastUpdate' not in person:
                        person['lastUpdate'] = person.pop('last_update')
                    if 'education_history' in person and 'educationHistory' not in person:
                        person['educationHistory'] = person.pop('education_history')
                    if 'work_history' in person and 'workHistory' not in person:
                        person['workHistory'] = person.pop('work_history')
                    if 'social_media' in person and 'socialMedia' not in person:
                        person['socialMedia'] = person.pop('social_media')
                    if 'visit_records' in person and 'visitRecords' not in person:
                        person['visitRecords'] = person.pop('visit_records')
                    if 'flight_records' in person and 'flightRecords' not in person:
                        person['flightRecords'] = person.pop('flight_records')
                    if 'train_records' in person and 'trainRecords' not in person:
                        person['trainRecords'] = person.pop('train_records')
                    if 'visa_type' in person and 'visaType' not in person:
                        person['visaType'] = person.pop('visa_type')
                print(f'[DEBUG] CSV数据转换完成，第一条数据示例: {people_list[0] if people_list else "无数据"}')
            except Exception as e:
                import traceback
                traceback.print_exc()
                return jsonify({'error': f'CSV文件解析错误：{str(e)}'}), 400

        else:
            return jsonify({'error': f'不支持的文件格式：{file_ext}'}), 400

        if not people_list:
            return jsonify({'error': '文件中没有数据'}), 400

        print(f'[DEBUG] 解析到 {len(people_list)} 条数据', flush=True)
        print(f'[DEBUG] 前3条数据示例: {people_list[:3] if len(people_list) >= 3 else people_list}', flush=True)

        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'id': f'log_{int(__import__("time").time() * 1000)}',
                    'timestamp': int(__import__("time").time() * 1000),
                    'location': 'app.py:579',
                    'message': '准备调用batch_create_local_people',
                    'data': {'people_count': len(people_list)},
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'D'
                }, ensure_ascii=False) + '\n')
        except: pass
        # #endregion
        
        # 批量导入到本地人员库
        count = db.batch_create_local_people(people_list)
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'id': f'log_{int(__import__("time").time() * 1000)}',
                    'timestamp': int(__import__("time").time() * 1000),
                    'location': 'app.py:580',
                    'message': 'batch_create_local_people返回',
                    'data': {'count': count},
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'D'
                }, ensure_ascii=False) + '\n')
        except: pass
        # #endregion
        
        print(f'[DEBUG] 导入完成，返回count: {count}', flush=True)
        print('=' * 50, flush=True)
        print('=== 本地人员库文件导入请求结束 ===', flush=True)
        print('=' * 50, flush=True)

        return jsonify({
            'message': f'成功导入 {count} 条数据到本地人员库',
            'count': count
        })
    except Exception as e:
        import traceback
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'id': f'log_{int(__import__("time").time() * 1000)}',
                    'timestamp': int(__import__("time").time() * 1000),
                    'location': 'app.py:591',
                    'message': '异常捕获',
                    'data': {'error': str(e), 'error_type': type(e).__name__},
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'E'
                }, ensure_ascii=False) + '\n')
        except: pass
        # #endregion
        traceback.print_exc()
        return jsonify({
            'error': '导入失败',
            'message': str(e)
        }), 500

@app.route('/api/local-people', methods=['GET'])
def get_local_people():
    """获取所有本地人员数据"""
    db = get_db()
    local_people = db.get_local_people()
    return jsonify(local_people)

@app.route('/api/local-people/<int:person_id>', methods=['GET'])
def get_local_person_detail(person_id):
    """获取单个本地人员详情"""
    db = get_db()
    person = db.get_local_person(person_id)
    if not person:
        return jsonify({'error': '人员不存在'}), 404
    return jsonify(person)

@app.route('/api/local-people/batch-delete', methods=['POST'])
def batch_delete_local_people():
    """批量删除本地人员"""
    try:
        data = request.json
        person_ids = data.get('ids', [])
        
        if not person_ids:
            return jsonify({'error': '请选择要删除的人员'}), 400
        
        if not isinstance(person_ids, list):
            return jsonify({'error': 'ids参数必须是数组'}), 400
        
        db = get_db()
        count = db.batch_delete_local_people(person_ids)
        
        return jsonify({
            'message': f'成功删除 {count} 条数据',
            'count': count
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': '删除失败',
            'message': str(e)
        }), 500

@app.route('/api/local-people/clear', methods=['POST'])
def clear_all_local_people():
    """清空所有本地人员"""
    try:
        db = get_db()
        count = db.clear_all_local_people()
        
        return jsonify({
            'message': f'成功清空 {count} 条数据',
            'count': count
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': '清空失败',
            'message': str(e)
        }), 500

@app.route('/api/people/<int:person_id>', methods=['PUT'])
def update_person(person_id):
    """更新人员"""
    db = get_db()
    init_database_if_empty()
    data = request.json
    
    person = db.get_person(person_id)
    if not person:
            return jsonify({'error': '人员不存在'}), 404
    
    updated_person = db.update_person(person_id, data)
    
    # 同步地图数据
    try:
        sync_map_data_from_people(db)
    except Exception as e:
        print(f'同步地图数据失败: {e}')
    
    return jsonify(updated_person)

@app.route('/api/people/<int:person_id>', methods=['GET'])
def get_person_detail(person_id):
    """获取人员详情"""
    db = get_db()
    init_database_if_empty()
    person = db.get_person(person_id)
    if not person:
        return jsonify({'error': '人员不存在'}), 404
    return jsonify(person)

@app.route('/api/people/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    """删除人员"""
    db = get_db()
    init_database_if_empty()
    success = db.delete_person(person_id)
    if not success:
        return jsonify({'error': '人员不存在'}), 404
    
    # 同步地图数据
    try:
        sync_map_data_from_people(db)
    except Exception as e:
        print(f'同步地图数据失败: {e}')

    return jsonify({'message': '删除成功'}), 200

# ========== 重点人员相关接口 ==========

@app.route('/api/key-persons', methods=['GET'])
def get_key_persons():
    """获取重点人员列表"""
    db = get_db()
    init_database_if_empty()
    category = request.args.get('category')
    if category and category != '全部':
        key_persons = db.get_key_persons(category=category)
    else:
        key_persons = db.get_key_persons()
    return jsonify(key_persons)

@app.route('/api/key-persons/categories', methods=['GET'])
def get_key_person_categories():
    """获取所有重点人员类别"""
    db = get_db()
    init_database_if_empty()
    categories = db.get_key_person_categories()
    return jsonify(categories)

@app.route('/api/key-persons', methods=['POST'])
def add_key_person():
    """添加重点人员"""
    # #region agent log
    import json
    try:
        with open(r'f:\all\projects\chaoyangV1.0.1\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'id': f'log_{int(__import__("time").time() * 1000)}',
                'timestamp': int(__import__("time").time() * 1000),
                'location': 'app.py:826',
                'message': 'add_key_person函数被调用',
                'data': {'method': request.method if request else 'N/A'},
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'A'
            }, ensure_ascii=False) + '\n')
    except:
        pass
    # #endregion
    
    db = get_db()
    init_database_if_empty()
    data = request.json
    
    # #region agent log
    try:
        with open(r'f:\all\projects\chaoyangV1.0.1\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'id': f'log_{int(__import__("time").time() * 1000)}',
                'timestamp': int(__import__("time").time() * 1000),
                'location': 'app.py:830',
                'message': '解析请求数据',
                'data': {'has_data': bool(data), 'person_id': data.get('personId') if data else None, 'category': data.get('category') if data else None},
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'B'
            }, ensure_ascii=False) + '\n')
    except:
        pass
    # #endregion
    
    person_id = data.get('personId')
    category = data.get('category')
    priority_level = data.get('priorityLevel', 1)
    reason = data.get('reason', '')
    
    if not person_id or not category:
        return jsonify({'error': '缺少必要参数'}), 400
    
    # #region agent log
    try:
        with open(r'f:\all\projects\chaoyangV1.0.1\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'id': f'log_{int(__import__("time").time() * 1000)}',
                'timestamp': int(__import__("time").time() * 1000),
                'location': 'app.py:839',
                'message': '调用add_key_person前',
                'data': {'person_id': person_id, 'category': category, 'priority_level': priority_level},
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'C'
            }, ensure_ascii=False) + '\n')
    except:
        pass
    # #endregion
    
    key_person = db.add_key_person(person_id, category, priority_level, reason)
    return jsonify(key_person), 201

@app.route('/api/key-persons/<int:person_id>', methods=['DELETE'])
def remove_key_person(person_id):
    """移除重点人员"""
    db = get_db()
    init_database_if_empty()
    category = request.args.get('category')
    if not category:
        return jsonify({'error': '缺少类别参数'}), 400
    
    success = db.remove_key_person(person_id, category)
    if success:
        return jsonify({'message': '移除成功'}), 200
    else:
        return jsonify({'error': '移除失败'}), 404

@app.route('/api/key-persons/<int:person_id>', methods=['PUT'])
def update_key_person(person_id):
    """更新重点人员信息"""
    db = get_db()
    init_database_if_empty()
    data = request.json
    category = data.get('category')
    priority_level = data.get('priorityLevel')
    reason = data.get('reason')
    
    if not category:
        return jsonify({'error': '缺少类别参数'}), 400
    
    key_person = db.update_key_person(person_id, category, priority_level, reason)
    if key_person:
        return jsonify(key_person), 200
    else:
        return jsonify({'error': '更新失败'}), 404

@app.route('/api/situation', methods=['GET'])
def get_situation():
    """获取态势感知数据"""
    try:
        db = get_db()
        init_database_if_empty()
        period = request.args.get('period', 'week')
        
        # 计算日期范围
        now = datetime.now()
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0)
        elif period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        else:
            start_date = datetime(2020, 1, 1)
        
        # 从数据库获取流动记录
        # 对于"全部"数据，限制查询数量以提高性能（最多查询1000条）
        movement_limit = 1000 if period == 'all' else None
        movements = db.get_movements({
            'from_date': start_date.strftime('%Y-%m-%d %H:%M:%S')
        }, limit=movement_limit)
        
        # 使用SQL聚合查询获取地区分布数据，而不是获取所有人员数据
        # 这样更高效，特别是当数据量很大时
        cursor = db.connection.cursor()
        cursor.execute('SELECT region, COUNT(*) as count FROM people GROUP BY region')
        region_rows = cursor.fetchall()
        region_data = [{'name': row[0] or '未知', 'value': row[1]} for row in region_rows]
        
        # 从数据库获取趋势数据
        end_date = now.strftime('%Y-%m-%d')
        start_date_str = start_date.strftime('%Y-%m-%d')
        trend_data_list = db.get_trend_data(start_date=start_date_str, end_date=end_date)
        
        # 如果数据库中没有趋势数据，生成最近7天的默认数据
        if not trend_data_list:
            dates = []
            confirmed_trend = []
            suspected_trend = []
            recovered_trend = []
            
            for i in range(7):
                date = (now - timedelta(days=6-i)).strftime('%Y-%m-%d')
                dates.append(date)
                confirmed_val = random.randint(5, 20)
                suspected_val = random.randint(10, 30)
                recovered_val = random.randint(3, 15)
                confirmed_trend.append(confirmed_val)
                suspected_trend.append(suspected_val)
                recovered_trend.append(recovered_val)
                # 保存到数据库
                db.create_trend_data(date, confirmed_val, suspected_val, recovered_val)
        else:
            # 从数据库读取趋势数据，确保按日期排序
            trend_data_list.sort(key=lambda x: x['date'])
            dates = [item['date'] for item in trend_data_list]
            confirmed_trend = [item['confirmedCount'] for item in trend_data_list]
            suspected_trend = [item['suspectedCount'] for item in trend_data_list]
            recovered_trend = [item['recoveredCount'] for item in trend_data_list]
        
        # 状态分布
        status_dist = db.count_people_by_status()
        status_distribution = [
            {'value': status_dist.get('正常', 0), 'name': '正常'},
            {'value': status_dist.get('疑似', 0), 'name': '疑似'},
            {'value': status_dist.get('确诊', 0), 'name': '确诊'},
            {'value': status_dist.get('康复', 0), 'name': '康复'}
        ]
        
        # 从数据库获取流动统计
        flow_statistics = db.get_flow_statistics(period=period)
        
        # 如果数据库中没有流动统计，从流动记录计算并保存
        if not flow_statistics:
            # 统计各地区的流动数量
            region_flows = {}
            for movement in movements:
                from_region = movement.get('from', '未知')
                to_region = movement.get('to', '未知')
                
                # 统计出发地
                if from_region not in region_flows:
                    region_flows[from_region] = 0
                region_flows[from_region] += 1
                
                # 统计目的地
                if to_region not in region_flows:
                    region_flows[to_region] = 0
                region_flows[to_region] += 1
            
            # 如果没有流动记录，从人员数据生成
            if not region_flows:
                flow_regions = list(set(p.get('region', '未知') for p in people))
                for region in flow_regions:
                    region_flows[region] = random.randint(10, 50)
            
            # 保存到数据库
            flow_regions = []
            flow_counts = []
            for region, flow_count in region_flows.items():
                flow_regions.append(region)
                flow_counts.append(flow_count)
                db.create_flow_statistics(region, flow_count, period=period)
        else:
            flow_regions = [item['region'] for item in flow_statistics]
            flow_counts = [item['flowCount'] for item in flow_statistics]
        
        # 处理movements数据，确保time字段存在
        sorted_movements = []
        for movement in movements:
            # 统一time字段名称
            if 'time' not in movement:
                movement['time'] = movement.get('movementTime') or movement.get('movement_time', '')
            if movement.get('time'):
                sorted_movements.append(movement)
        
        # 按时间排序，最多返回50条
        sorted_movements = sorted(sorted_movements, key=lambda x: x.get('time', ''), reverse=True)[:50]
        
        return jsonify({
            'regionData': region_data,
            'trendDates': dates,
            'confirmedTrend': confirmed_trend,
            'suspectedTrend': suspected_trend,
            'recoveredTrend': recovered_trend,
            'statusDistribution': status_distribution,
            'flowRegions': flow_regions,
            'flowCounts': flow_counts,
            'movements': sorted_movements
        })
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        return jsonify({
            'error': '获取态势数据失败',
            'message': error_msg,
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/news', methods=['GET'])
def get_news():
    """获取新闻热点数据"""
    try:
        db = get_db()
        init_database_if_empty()
        limit = int(request.args.get('limit', 20))
        
        # 从人员数据中提取相关信息生成新闻热点
        people = db.get_people()
        
        # 生成新闻热点数据
        news_items = []
        
        # 基于人员状态和地区生成新闻
        status_counts = {}
        region_counts = {}
        for person in people:
            status = person.get('status', '正常')
            region = person.get('region', '未知')
            status_counts[status] = status_counts.get(status, 0) + 1
            region_counts[region] = region_counts.get(region, 0) + 1
        
        # 生成新闻标题和内容
        news_templates = [
            {
                'title': f'{max(region_counts.items(), key=lambda x: x[1])[0]}地区监测人数达{max(region_counts.values())}人',
                'summary': f'根据最新监测数据，{max(region_counts.items(), key=lambda x: x[1])[0]}地区监测人数持续增长，相关部门已加强防控措施。',
                'source': '监测系统',
            },
            {
                'title': f'全国疑似病例{status_counts.get("疑似", 0)}例，确诊病例{status_counts.get("确诊", 0)}例',
                'summary': f'截至今日，全国疑似病例{status_counts.get("疑似", 0)}例，确诊病例{status_counts.get("确诊", 0)}例，康复病例{status_counts.get("康复", 0)}例。',
                'source': '疾控中心',
            },
            {
                'title': '多地加强人员流动监测，确保防控措施落实到位',
                'summary': '各地监测系统持续运行，对人员流动进行实时追踪，确保及时发现和处置异常情况。',
                'source': '新闻媒体',
            },
            {
                'title': '专家提醒：注意个人防护，减少不必要的外出',
                'summary': '专家建议公众注意个人防护，勤洗手、戴口罩，减少不必要的外出和聚集活动。',
                'source': '健康时报',
            },
            {
                'title': '监测系统升级，提升数据处理能力',
                'summary': '全国流感人群流动监测系统完成升级，数据处理能力提升，能够更快速、准确地分析人员流动情况。',
                'source': '科技日报',
            },
        ]
        
        # 如果数据库中有流动记录，基于流动记录生成新闻
        movements = db.get_movements({})
        if movements:
            recent_movements = sorted(movements, key=lambda x: x.get('time', ''), reverse=True)[:5]
            for movement in recent_movements:
                from_region = movement.get('from', '未知')
                to_region = movement.get('to', '未知')
                news_items.append({
                    'title': f'{from_region}至{to_region}人员流动增加',
                    'summary': f'监测数据显示，{from_region}至{to_region}的人员流动有所增加，相关部门已加强监测。',
                    'source': '监测系统',
                    'publishTime': movement.get('time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                })
        
        # 添加模板新闻
        for i, template in enumerate(news_templates[:limit - len(news_items)]):
            days_ago = random.randint(0, 7)
            publish_time = (datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))).strftime('%Y-%m-%d %H:%M:%S')
            news_items.append({
                'title': template['title'],
                'summary': template['summary'],
                'source': template['source'],
                'publishTime': publish_time
            })
        
        # 按时间排序
        news_items.sort(key=lambda x: x.get('publishTime', ''), reverse=True)
        
        return jsonify(news_items[:limit])
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': '获取新闻热点失败',
            'message': str(e)
        }), 500

@app.route('/api/social-posts', methods=['GET'])
def get_social_posts():
    """获取社交动态数据"""
    try:
        db = get_db()
        init_database_if_empty()
        limit = int(request.args.get('limit', 50))
        
        # 从人员数据中提取社交动态
        people = db.get_people()
        
        social_posts = []
        
        # 遍历所有人员，提取他们的社交动态
        for person in people:
            social_media = person.get('socialMedia', [])
            if not social_media:
                # 如果没有socialMedia字段，尝试从social_media字段获取
                social_media = person.get('social_media', [])
            
            # 如果social_media是字符串，尝试解析JSON
            if isinstance(social_media, str):
                try:
                    social_media = json.loads(social_media) if social_media else []
                except:
                    social_media = []
            
            # 提取社交动态
            if isinstance(social_media, list):
                for post in social_media:
                    if isinstance(post, dict):
                        social_posts.append({
                            'personName': person.get('name', '未知'),
                            'avatar': person.get('avatar', '/api/avatars/avatar_1.jpg'),
                            'platform': post.get('platform', '未知平台'),
                            'content': post.get('content', ''),
                            'postTime': post.get('time', post.get('postTime', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                        })
        
        # 按时间排序
        social_posts.sort(key=lambda x: x.get('postTime', ''), reverse=True)
        
        return jsonify(social_posts[:limit])
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': '获取社交动态失败',
            'message': str(e)
        }), 500

@app.route('/api/realtime-movements', methods=['GET'])
def get_realtime_movements():
    """获取实时流动数据"""
    try:
        db = get_db()
        init_database_if_empty()
        limit = int(request.args.get('limit', 50))
        
        # 从数据库获取最近的流动记录
        movements = db.get_movements({})
        
        # 按时间排序，获取最新的流动记录
        sorted_movements = sorted(movements, key=lambda x: x.get('time', x.get('movementTime', '')), reverse=True)[:limit]
        
        # 格式化数据
        realtime_movements = []
        for movement in sorted_movements:
            realtime_movements.append({
                'id': movement.get('id'),
                'personName': movement.get('personName', movement.get('name', '未知')),
                'avatar': movement.get('avatar', '/api/avatars/avatar_1.jpg'),
                'from': movement.get('from', movement.get('fromRegion', '未知')),
                'to': movement.get('to', movement.get('toRegion', '未知')),
                'time': movement.get('time', movement.get('movementTime', '')),
                'status': movement.get('status', '正常')
            })
        
        return jsonify(realtime_movements)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': '获取实时流动数据失败',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # 初始化数据库（如果为空）- 使用临时连接
    with Database() as temp_db:
        people = temp_db.get_people()
        if len(people) == 0:
            print('数据库为空，正在初始化假数据...')
            from init_database import init_database
            init_database(clear_existing=False, people_count=8000, movements_count=16000)
            print('假数据初始化完成！')
    
    app.run(debug=True, port=8000, threaded=True)

