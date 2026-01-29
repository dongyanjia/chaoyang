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
from flask import Flask, jsonify, request, send_from_directory, send_file, g
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
import pymysql
try:
    from document_service import get_document_service
    from rag_service import get_rag_service
    DOCUMENT_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f'[WARN] 文档服务模块未安装: {e}')
    DOCUMENT_SERVICE_AVAILABLE = False

try:
    from tag_service import get_tag_service
    TAG_SERVICE_AVAILABLE = True
    print('[OK] 标签服务模块加载成功')
except ImportError as e:
    print(f'[WARN] 标签服务模块未安装: {e}')
    import traceback
    traceback.print_exc()
    TAG_SERVICE_AVAILABLE = False
except Exception as e:
    print(f'[ERROR] 标签服务模块加载失败: {e}')
    import traceback
    traceback.print_exc()
    TAG_SERVICE_AVAILABLE = False

# pandas导入（用于Excel/CSV文件解析）
PANDAS_AVAILABLE = False
pd = None
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
    print(f"[OK] pandas导入成功，版本: {pd.__version__}")
    try:
        import openpyxl
        openpyxl_available = True
    except:
        openpyxl_available = False
except ImportError as e:
    PANDAS_AVAILABLE = False
    pd = None
    print(f"[WARN] pandas未安装（Excel/CSV导入功能将不可用）: {e}")
    print("提示: 请运行 'pip install pandas==2.1.4' 安装pandas")
except Exception as e:
    PANDAS_AVAILABLE = False
    pd = None
    print(f"[WARN] pandas导入失败（Excel/CSV导入功能将不可用）: {e}")
    import traceback
    traceback.print_exc()

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
        
        print(f'[登录请求] 用户名: {username}, 密码长度: {len(password)}')
        
        if not username or not password:
            print(f'[登录失败] 用户名或密码为空')
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400
        
        # 检查用户是否存在
        user = USERS.get(username)
        if not user:
            print(f'[登录失败] 用户不存在: {username}')
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
        
        # 检查密码（实际项目中应该使用hash比较）
        if user['password'] != password:
            print(f'[登录失败] 密码错误 - 期望: {user["password"]}, 实际: {password}')
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
        
        print(f'[登录成功] 用户: {username}')
        
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
    # 使用 count 查询而不是获取所有数据，避免内存问题
    try:
        people_count = db.get_people_count()
        need_init = people_count == 0
        
        # 检查趋势数据是否存在（只检查数量，不获取全部数据）
        if not need_init:
            try:
                # 只查询一条数据来检查是否存在
                trend_data = db.get_trend_data(start_date='2000-01-01', end_date='2000-01-01', limit=1)
                if len(trend_data) == 0:
                    need_init = True
            except:
                # 如果查询失败，假设需要初始化
                need_init = True
    except Exception as e:
        # 如果查询失败，假设需要初始化
        print(f'检查数据库状态失败: {e}')
        need_init = True
    
    if need_init:
        # 暂时禁用自动初始化，避免内存问题
        # 用户需要手动运行 init_database.py 来初始化数据
        print('[WARN] 数据库为空，请手动运行 init_database.py 初始化数据')
        print('[WARN] 或者等待系统内存释放后再试')
        # from init_database import init_database
        # init_database(clear_existing=False, people_count=100, movements_count=200)
        # print('假数据初始化完成！')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计数据"""
    try:
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
        try:
            stats = db.get_stats()
        except Exception as e:
            print(f'获取统计数据失败: {e}')
            # 如果查询失败，返回默认值
            stats = {
                'totalPeople': 0,
                'confirmedCases': 0,
                'activeRegions': 0,
                'todayMovements': 0
            }
        
        # 获取最近10条流动记录作为动态
        try:
            movements = db.get_movements(limit=10)
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
        except Exception as e:
            print(f'获取流动记录失败: {e}')
            recent_activities = []
        
        # 从数据库获取地图数据（已同步）
        try:
            map_data = db.get_map_data()
        except Exception as e:
            print(f'获取地图数据失败: {e}')
            map_data = []
        
        # 如果地图数据为空，生成默认数据
        if not map_data:
            try:
                from init_database import PROVINCES
                map_data = []
                for province, (min_val, max_val) in PROVINCES.items():
                    value = random.randint(min_val, max_val)
                    map_data.append({'name': province, 'value': value})
                    try:
                        db.update_map_data(province, value)
                    except:
                        pass  # 如果更新失败，继续
            except Exception as e:
                print(f'生成默认地图数据失败: {e}')
                map_data = []
        
        # 获取各省确诊人数排名
        try:
            province_ranking = db.get_province_confirmed_ranking()
        except Exception as e:
            print(f'获取省份排名失败: {e}')
            province_ranking = []
        
        return jsonify({
            'stats': stats,
            'recentActivities': recent_activities,
            'mapData': map_data,
            'provinceRanking': province_ranking
        })
    except Exception as e:
        print(f'获取统计数据异常: {e}')
        import traceback
        traceback.print_exc()
        # 返回默认数据，确保前端不会崩溃
        return jsonify({
            'stats': {
                'totalPeople': 0,
                'confirmedCases': 0,
                'activeRegions': 0,
                'todayMovements': 0
            },
            'recentActivities': [],
            'mapData': [],
            'provinceRanking': []
        }), 200

@app.route('/api/people', methods=['GET'])
def get_people():
    """获取人员列表，支持分页和标签筛选"""
    try:
        db = get_db()
        init_database_if_empty()
        
        # 获取分页参数
        page = request.args.get('page', type=int)
        page_size = request.args.get('page_size', type=int)
        
        # 获取搜索和标签筛选参数
        search_query = request.args.get('search', type=str)
        tags_json = request.args.get('tags', type=str)  # JSON 字符串格式的标签列表
        
        # 解析标签
        tags = []
        if tags_json:
            try:
                tags = json.loads(tags_json)
            except:
                pass
        
        # 如果提供了标签筛选，使用标签服务
        if tags and TAG_SERVICE_AVAILABLE:
            try:
                tag_service = get_tag_service(db)
                result = tag_service.filter_people_by_tags(
                    tags=tags,
                    search_query=search_query,
                    page=page or 1,
                    page_size=page_size or 30
                )
                return jsonify({
                    'data': result['data'],
                    'pagination': {
                        'page': result['page'],
                        'page_size': result['page_size'],
                        'total': result['total'],
                        'total_pages': result['total_pages']
                    }
                })
            except Exception as e:
                print(f'标签筛选失败: {e}')
                import traceback
                traceback.print_exc()
                # 降级到普通查询
        
        # 普通查询（无标签筛选或标签服务不可用）
        # 如果提供了分页参数，使用分页查询
        if page is not None and page_size is not None:
            try:
                # 如果有搜索条件，需要先过滤
                if search_query:
                    # 简单搜索：获取所有数据后过滤（性能较差，但兼容现有逻辑）
                    all_people = db.get_people(limit=10000)
                    filtered = [
                        p for p in all_people
                        if search_query.lower() in (p.get('name', '') or '').lower() or
                           search_query in (p.get('id_card', '') or '')
                    ]
                    total_count = len(filtered)
                    start = (page - 1) * page_size
                    end = start + page_size
                    people = filtered[start:end]
                else:
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
            except Exception as e:
                print(f'获取人员列表失败: {e}')
                return jsonify({
                    'data': [],
                    'pagination': {
                        'page': page,
                        'page_size': page_size,
                        'total': 0,
                        'total_pages': 0
                    }
                }), 200
        else:
            # 兼容旧接口，但限制返回数量避免内存问题
            try:
                people = db.get_people(limit=1000)
                return jsonify(people)
            except Exception as e:
                print(f'获取人员列表失败: {e}')
                return jsonify([]), 200
    except Exception as e:
        print(f'获取人员列表异常: {e}')
        import traceback
        traceback.print_exc()
        return jsonify([]), 200

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
    
    
    # 处理CORS预检请求
    if request.method == 'OPTIONS':
        
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    # 处理GET请求（用于测试或错误提示）
    if request.method == 'GET':
        
        return jsonify({
            'error': '此接口仅支持POST请求',
            'message': '请使用POST方法上传文件',
            'usage': '使用前端页面的"确认导入"按钮上传文件'
        }), 405
    
    try:
        import sys
        sys.stdout.flush()  # 强制刷新输出缓冲区
        
        
        
        print('=' * 50, flush=True)
        print('=== 本地人员库文件导入请求开始 ===', flush=True)
        print('请求方法:', request.method, flush=True)
        print('请求内容类型:', request.content_type, flush=True)
        print('请求头:', dict(request.headers), flush=True)
        print('=' * 50, flush=True)
        print('请求文件:', request.files, flush=True)
        
        
        
        db = get_db()

        if 'file' not in request.files:
            
            print('错误：请求中没有file字段', flush=True)
            print('可用的文件字段:', list(request.files.keys()), flush=True)
            print('请求表单数据:', request.form, flush=True)
            return jsonify({'error': '未选择文件', 'available_files': list(request.files.keys())}), 400

        file = request.files['file']
        
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
            
            if not pandas_available_now or pd_module is None:
                
                try:
                    import sys
                    import pandas as pd_module
                    pandas_available_now = True
                    
                except ImportError as e:
                    pandas_available_now = False
                    
                except Exception as e:
                    pandas_available_now = False
                    
            
            
            
            if not pandas_available_now or pd_module is None:
                
                return jsonify({'error': 'Excel文件解析需要pandas库，请安装：pip install pandas openpyxl'}), 400
            try:
                import io
                
                file_content = file.read()
                file_stream = io.BytesIO(file_content)
                
                df = pd_module.read_excel(file_stream)
                print(f'[DEBUG] Excel文件读取成功，共 {len(df)} 行，列名: {list(df.columns)}')
                
                
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

        
        
        # 批量导入到本地人员库
        count = db.batch_create_local_people(people_list)
        
        
        
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
        
        traceback.print_exc()
        return jsonify({
            'error': '导入失败',
            'message': str(e)
        }), 500

@app.route('/api/local-people', methods=['GET'])
def get_local_people():
    """获取所有本地人员数据（已合并到 people 表）"""
    try:
        db = get_db()
        local_people = db.get_local_people()
        return jsonify(local_people)
    except Exception as e:
        print(f'获取本地人员列表失败: {e}')
        import traceback
        traceback.print_exc()
        return jsonify([]), 200

@app.route('/api/local-people/<int:person_id>', methods=['GET'])
def get_local_person_detail(person_id):
    """获取单个本地人员详情（已合并到 people 表）"""
    db = get_db()
    person = db.get_local_person(person_id)
    if not person:
        return jsonify({'error': '人员不存在'}), 404
    return jsonify(person)

@app.route('/api/local-people/batch-delete', methods=['POST'])
def batch_delete_local_people():
    """批量删除本地人员（已合并到 people 表）"""
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
    """清空所有本地人员（已合并到 people 表，此操作会清空所有人员数据，请谨慎使用）"""
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
    try:
        db = get_db()
        init_database_if_empty()
        category = request.args.get('category')
        if category and category != '全部':
            key_persons = db.get_key_persons(category=category)
        else:
            key_persons = db.get_key_persons()
        return jsonify(key_persons)
    except Exception as e:
        print(f'获取重点人员列表失败: {e}')
        import traceback
        traceback.print_exc()
        return jsonify([]), 200

@app.route('/api/key-persons/categories', methods=['GET'])
def get_key_person_categories():
    """获取所有重点人员类别"""
    try:
        db = get_db()
        init_database_if_empty()
        categories = db.get_key_person_categories()
        return jsonify(categories)
    except Exception as e:
        print(f'获取重点人员类别失败: {e}')
        import traceback
        traceback.print_exc()
        return jsonify([]), 200

@app.route('/api/key-persons', methods=['POST'])
def add_key_person():
    """添加重点人员"""
    
    
    db = get_db()
    init_database_if_empty()
    data = request.json
    
    
    
    person_id = data.get('personId')
    category = data.get('category')
    priority_level = data.get('priorityLevel', 1)
    reason = data.get('reason', '')
    
    if not person_id or not category:
        return jsonify({'error': '缺少必要参数'}), 400
    
    
    
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
        try:
            movement_limit = 1000 if period == 'all' else None
            movements = db.get_movements({
                'from_date': start_date.strftime('%Y-%m-%d %H:%M:%S')
            }, limit=movement_limit)
        except Exception as e:
            print(f'获取流动记录失败: {e}')
            movements = []
        
        # 使用SQL聚合查询获取地区分布数据，而不是获取所有人员数据
        # 这样更高效，特别是当数据量很大时
        try:
            cursor = db.connection.cursor()
            cursor.execute('SELECT region, COUNT(*) as count FROM people GROUP BY region')
            region_rows = cursor.fetchall()
            region_data = [{'name': row[0] or '未知', 'value': row[1]} for row in region_rows]
        except Exception as e:
            print(f'获取地区分布数据失败: {e}')
            region_data = []
        
        # 从数据库获取趋势数据
        try:
            end_date = now.strftime('%Y-%m-%d')
            start_date_str = start_date.strftime('%Y-%m-%d')
            trend_data_list = db.get_trend_data(start_date=start_date_str, end_date=end_date, limit=100)
        except Exception as e:
            print(f'获取趋势数据失败: {e}')
            trend_data_list = []
        
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
        try:
            status_dist = db.count_people_by_status()
            status_distribution = [
                {'value': status_dist.get('正常', 0), 'name': '正常'},
                {'value': status_dist.get('疑似', 0), 'name': '疑似'},
                {'value': status_dist.get('确诊', 0), 'name': '确诊'},
                {'value': status_dist.get('康复', 0), 'name': '康复'}
            ]
        except Exception as e:
            print(f'获取状态分布失败: {e}')
            status_distribution = [
                {'value': 0, 'name': '正常'},
                {'value': 0, 'name': '疑似'},
                {'value': 0, 'name': '确诊'},
                {'value': 0, 'name': '康复'}
            ]
        
        # 从数据库获取流动统计
        try:
            flow_statistics = db.get_flow_statistics(period=period)
        except Exception as e:
            print(f'获取流动统计失败: {e}')
            flow_statistics = []
        
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
            
            # 如果没有流动记录，生成默认数据
            if not region_flows:
                # 不查询所有人员数据，直接生成默认数据
                default_regions = ['北京', '上海', '广东', '浙江', '江苏']
                for region in default_regions:
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
            'flowRegions': flow_regions if 'flow_regions' in locals() else [],
            'flowCounts': flow_counts if 'flow_counts' in locals() else [],
            'movements': sorted_movements if 'sorted_movements' in locals() else []
        })
    except Exception as e:
        print(f'获取态势感知数据异常: {e}')
        import traceback
        traceback.print_exc()
        # 返回默认数据，确保前端不会崩溃
        return jsonify({
            'regionData': [],
            'trendDates': [],
            'confirmedTrend': [],
            'suspectedTrend': [],
            'recoveredTrend': [],
            'statusDistribution': [
                {'value': 0, 'name': '正常'},
                {'value': 0, 'name': '疑似'},
                {'value': 0, 'name': '确诊'},
                {'value': 0, 'name': '康复'}
            ],
            'flowRegions': [],
            'flowCounts': [],
            'movements': []
        }), 200

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
            init_database(clear_existing=False, people_count=100, movements_count=200)
            print('假数据初始化完成！')
    
    # 文档工作区相关接口
    if DOCUMENT_SERVICE_AVAILABLE:
        @app.route('/api/documents', methods=['GET'])
        def get_documents():
            """获取文档列表"""
            try:
                area = request.args.get('area', 'public')
                user = request.headers.get('X-User', None)
                
                db = get_db()
                doc_service = get_document_service(db)
                documents = doc_service.get_documents(area, user)
                
                return jsonify(documents)
            except Exception as e:
                print(f'获取文档列表失败: {e}')
                import traceback
                traceback.print_exc()
                return jsonify({'error': str(e)}), 500

        @app.route('/api/documents/upload', methods=['POST'])
        def upload_document():
            """上传文档"""
            try:
                if 'file' not in request.files:
                    return jsonify({'error': '没有文件'}), 400
                
                file = request.files['file']
                area = request.form.get('area', 'public')
                user = request.headers.get('X-User', 'anonymous')
                
                if file.filename == '':
                    return jsonify({'error': '文件名为空'}), 400
                
                db = get_db()
                if not db:
                    return jsonify({'error': '数据库连接失败'}), 500
                
                doc_service = get_document_service(db)
                if not doc_service:
                    return jsonify({'error': '文档服务初始化失败'}), 500
                
                result = doc_service.save_document(file, area, user)
                
                if not result:
                    return jsonify({'error': '文档保存失败'}), 500
                
                return jsonify(result), 201
            except Exception as e:
                error_msg = str(e)
                print(f'上传文档失败: {error_msg}')
                import traceback
                traceback.print_exc()
                return jsonify({'error': error_msg}), 500

        @app.route('/api/documents/<int:document_id>/preview', methods=['GET'])
        def get_document_preview(document_id):
            """获取文档预览"""
            try:
                db = get_db()
                cursor = db.connection.cursor(pymysql.cursors.DictCursor)
                cursor.execute('SELECT file_path, file_type, name FROM documents WHERE id = %s', (document_id,))
                doc = cursor.fetchone()
                
                if not doc:
                    return jsonify({'error': '文档不存在'}), 404
                
                # OnlyOffice 配置
                onlyoffice_url = os.getenv('ONLYOFFICE_URL', 'http://localhost:8081')
                
                # 生成文档访问URL（需要可以从 OnlyOffice 访问）
                document_url = request.url_root.rstrip('/') + f'/api/documents/{document_id}/file'
                
                # 生成 OnlyOffice 预览配置
                file_type_lower = doc['file_type'].lower()
                
                # 确定文档类型
                if file_type_lower in ['doc', 'docx', 'txt', 'rtf', 'odt']:
                    doc_type = 'text'
                elif file_type_lower in ['xls', 'xlsx', 'ods']:
                    doc_type = 'spreadsheet'
                elif file_type_lower in ['ppt', 'pptx', 'odp']:
                    doc_type = 'presentation'
                else:
                    doc_type = 'text'
                
                # 生成文档密钥（用于缓存）
                doc_key = hashlib.md5(f"{document_id}_{doc['name']}_{doc['file_path']}".encode()).hexdigest()
                
                preview_config = {
                    'document': {
                        'fileType': file_type_lower,
                        'key': doc_key,
                        'title': doc['name'],
                        'url': document_url
                    },
                    'documentType': doc_type,
                    'editorConfig': {
                        'mode': 'view',  # 预览模式，不允许编辑
                        'lang': 'zh-CN'
                    }
                }
                
                download_url = f'/api/documents/{document_id}/download'
                
                # 支持 OnlyOffice 的文件类型
                onlyoffice_supported = ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf', 'txt', 'rtf', 'odt', 'ods', 'odp']
                file_type_lower = doc['file_type'].lower()
                
                result = {
                    'preview_url': document_url,
                    'download_url': download_url,
                    'file_type': doc['file_type'],
                    'file_name': doc['name']
                }
                
                # 如果文件类型支持 OnlyOffice，添加配置
                if file_type_lower in onlyoffice_supported:
                    result['onlyoffice_url'] = onlyoffice_url
                    result['onlyoffice_config'] = preview_config
                
                return jsonify(result)
            except Exception as e:
                print(f'获取文档预览失败: {e}')
                import traceback
                traceback.print_exc()
                return jsonify({'error': str(e)}), 500

        @app.route('/api/documents/<int:document_id>/file', methods=['GET'])
        def get_document_file(document_id):
            """获取文档文件（用于预览）"""
            try:
                db = get_db()
                cursor = db.connection.cursor(pymysql.cursors.DictCursor)
                cursor.execute('SELECT file_path, file_type FROM documents WHERE id = %s', (document_id,))
                doc = cursor.fetchone()
                
                if not doc or not os.path.exists(doc['file_path']):
                    return jsonify({'error': '文档不存在'}), 404
                
                return send_file(doc['file_path'], as_attachment=False)
            except Exception as e:
                print(f'获取文档文件失败: {e}')
                return jsonify({'error': str(e)}), 500

        @app.route('/api/documents/<int:document_id>/download', methods=['GET'])
        def download_document(document_id):
            """下载文档"""
            try:
                db = get_db()
                cursor = db.connection.cursor(pymysql.cursors.DictCursor)
                cursor.execute('SELECT file_path, name FROM documents WHERE id = %s', (document_id,))
                doc = cursor.fetchone()
                
                if not doc:
                    return jsonify({'error': '文档不存在'}), 404
                
                if not os.path.exists(doc['file_path']):
                    return jsonify({'error': '文档文件不存在'}), 404
                
                # 使用 send_file 发送文件，设置正确的下载名称
                return send_file(
                    doc['file_path'],
                    as_attachment=True,
                    download_name=doc['name'],
                    mimetype='application/octet-stream'
                )
            except Exception as e:
                print(f'下载文档失败: {e}')
                import traceback
                traceback.print_exc()
                return jsonify({'error': str(e)}), 500

        @app.route('/api/documents/<int:document_id>', methods=['DELETE'])
        def delete_document(document_id):
            """删除文档"""
            try:
                db = get_db()
                doc_service = get_document_service(db)
                
                if doc_service.delete_document(document_id):
                    return jsonify({'message': '删除成功'}), 200
                else:
                    return jsonify({'error': '删除失败'}), 500
            except Exception as e:
                print(f'删除文档失败: {e}')
                return jsonify({'error': str(e)}), 500

        @app.route('/api/documents/ask', methods=['POST'])
        def ask_question():
            """智能问答"""
            try:
                data = request.json
                question = data.get('question', '')
                area = data.get('area', None)
                
                if not question:
                    return jsonify({'error': '问题不能为空'}), 400
                
                db = get_db()
                doc_service = get_document_service(db)
                rag_service = get_rag_service(doc_service)
                
                result = rag_service.ask_question(question, area)
                
                return jsonify(result)
            except Exception as e:
                print(f'问答失败: {e}')
                import traceback
                traceback.print_exc()
                return jsonify({'error': str(e)}), 500

    # 标签相关接口
    # 确保 TAG_SERVICE_AVAILABLE 已定义
    try:
        _tag_service_available = TAG_SERVICE_AVAILABLE
    except NameError:
        _tag_service_available = False
        print('[WARN] TAG_SERVICE_AVAILABLE 未定义，设置为 False')
    
    if _tag_service_available:
        print('[OK] 注册标签相关API路由')
        @app.route('/api/tags', methods=['GET'])
        def get_tags():
            """获取所有标签"""
            try:
                db = get_db()
                if not db:
                    print('[ERROR] /api/tags: 数据库连接失败')
                    return jsonify({
                        'error': '数据库连接失败',
                        'message': '无法连接到数据库，请检查数据库配置'
                    }), 500
                
                tag_service = get_tag_service(db)
                if not tag_service:
                    print('[ERROR] /api/tags: 标签服务初始化失败')
                    return jsonify({
                        'error': '标签服务初始化失败',
                        'message': '无法初始化标签服务'
                    }), 500
                
                tags = tag_service.get_all_tags()
                # 确保返回的是列表格式
                if tags is None:
                    tags = []
                
                # 如果数据库中没有标签，自动初始化默认标签
                if len(tags) == 0:
                    print('[INFO] /api/tags: 数据库中没有标签，自动初始化默认标签...')
                    DEFAULT_TAG_CATEGORIES = [
                        {
                            'id': 1,
                            'name': '基本信息',
                            'children': [
                                {
                                    'id': 1,
                                    'name': '年龄',
                                    'tags': ['18-25岁', '26-35岁', '36-45岁', '46-55岁', '56-65岁', '65岁以上']
                                },
                                {
                                    'id': 2,
                                    'name': '性别',
                                    'tags': ['男', '女']
                                },
                                {
                                    'id': 3,
                                    'name': '职业',
                                    'tags': ['外交官', '翻译', '导游', '外贸', '空乘', '飞行员', '船员', '记者', '商务', '学生',
                                             '教授', '医生', '工程师', '艺术家', '音乐家', '运动员', '国际咨询', '跨国公司高管', '国际律师', '国际组织工作人员']
                                },
                                {
                                    'id': 4,
                                    'name': '籍贯',
                                    'tags': ['北京市', '上海市', '天津市', '重庆市', '广东省', '浙江省', '江苏省', '山东省', '四川省', '湖北省', '河南省', '湖南省', '安徽省', '福建省', '陕西省', '辽宁省', '河北省', '江西省', '云南省', '广西壮族自治区', '贵州省', '山西省', '内蒙古自治区', '吉林省', '黑龙江省', '新疆维吾尔自治区', '甘肃省', '海南省', '宁夏回族自治区', '青海省', '西藏自治区', '香港特别行政区', '澳门特别行政区', '台湾省']
                                },
                                {
                                    'id': 5,
                                    'name': '状态',
                                    'tags': ['正常', '疑似', '确诊', '康复']
                                },
                                {
                                    'id': 6,
                                    'name': '签证类型',
                                    'tags': ['旅游签证', '工作签证', '学生签证', '商务签证', '探亲签证', '访问签证', 
                                             '过境签证', '居留签证', '投资签证', '技术签证', '文化交流签证', '医疗签证',
                                             '实习签证', '记者签证', '外交签证', '公务签证', '其他签证']
                                },
                                {
                                    'id': 7,
                                    'name': '机构',
                                    'tags': ['美国疾病控制与预防中心', '英国国家医疗服务体系', '法国公共卫生署', '德国罗伯特·科赫研究所', '日本国立感染症研究所', '韩国疾病管理本部', '俄罗斯联邦消费者权益保护局', '印度国家疾病控制中心', '澳大利亚卫生部', '加拿大公共卫生署', '意大利国家卫生研究所', '西班牙卫生部', '巴西卫生部', '墨西哥卫生部', '世界卫生组织']
                                }
                            ]
                        },
                        {
                            'id': 2,
                            'name': '到访信息',
                            'children': [
                                {
                                    'id': 1,
                                    'name': '到访省份',
                                    'tags': ['北京市', '上海市', '天津市', '重庆市', '广东省', '浙江省', '江苏省', '山东省', '四川省', '湖北省', '河南省', '湖南省', '安徽省', '福建省', '陕西省', '辽宁省', '河北省', '江西省', '云南省', '广西壮族自治区', '贵州省', '山西省', '内蒙古自治区', '吉林省', '黑龙江省', '新疆维吾尔自治区', '甘肃省', '海南省', '宁夏回族自治区', '青海省', '西藏自治区', '香港特别行政区', '澳门特别行政区', '台湾省']
                                }
                            ]
                        },
                        {
                            'id': 3,
                            'name': '民航铁路动态',
                            'children': [
                                {
                                    'id': 1,
                                    'name': '航班',
                                    'tags': ['中国国际航空', '中国东方航空', '中国南方航空', '海南航空', '深圳航空']
                                },
                                {
                                    'id': 2,
                                    'name': '铁路',
                                    'tags': ['高铁', '动车', '普通列车']
                                }
                            ]
                        },
                        {
                            'id': 4,
                            'name': '社交媒体动态',
                            'children': [
                                {
                                    'id': 1,
                                    'name': '平台类型',
                                    'tags': ['微信', '微博', '抖音', 'QQ', '小红书', '知乎']
                                }
                            ]
                        }
                    ]
                    
                    try:
                        count = tag_service.extract_and_save_tags(DEFAULT_TAG_CATEGORIES, clear_existing=False)
                        print(f'[OK] /api/tags: 自动初始化完成，成功导入 {count} 个标签')
                        # 重新获取标签
                        tags = tag_service.get_all_tags()
                        if tags is None:
                            tags = []
                    except Exception as init_error:
                        print(f'[ERROR] /api/tags: 自动初始化失败: {init_error}')
                        import traceback
                        traceback.print_exc()
                        # 即使初始化失败，也返回空数组，不抛出错误
                
                print(f'[INFO] /api/tags: 返回 {len(tags)} 个分类')
                if len(tags) > 0:
                    print(f'[INFO] /api/tags: 第一个分类: {tags[0].get("name", "N/A")}, 子分类数: {len(tags[0].get("children", []))}')
                
                return jsonify(tags)
            except Exception as e:
                print(f'[ERROR] 获取标签列表失败: {e}')
                import traceback
                traceback.print_exc()
                return jsonify({
                    'error': '获取标签列表失败',
                    'message': str(e),
                    'details': '请检查后端日志获取更多信息'
                }), 500

        @app.route('/api/tags/extract', methods=['POST'])
        def extract_tags():
            """从配置中提取标签并保存到数据库"""
            try:
                data = request.json
                categories = data.get('categories', [])
                
                if not categories:
                    return jsonify({'error': '标签数据为空'}), 400
                
                db = get_db()
                tag_service = get_tag_service(db)
                clear_existing = data.get('clear_existing', False)
                count = tag_service.extract_and_save_tags(categories, clear_existing=clear_existing)
                
                return jsonify({
                    'success': True,
                    'message': f'成功提取并保存 {count} 个标签',
                    'count': count
                })
            except Exception as e:
                print(f'提取标签失败: {e}')
                import traceback
                traceback.print_exc()
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/tags/sync', methods=['POST'])
        def sync_tags():
            """从前端同步标签到数据库（会清空旧标签）"""
            try:
                data = request.json
                categories = data.get('categories', [])
                
                if not categories:
                    return jsonify({'success': False, 'error': '标签数据为空'}), 400
                
                db = get_db()
                tag_service = get_tag_service(db)
                result = tag_service.save_tags_from_frontend(categories)
                
                if result['success']:
                    return jsonify(result)
                else:
                    return jsonify(result), 500
            except Exception as e:
                print(f'同步标签失败: {e}')
                import traceback
                traceback.print_exc()
                return jsonify({'success': False, 'error': str(e)}), 500

        @app.route('/api/tags/counts', methods=['GET'])
        def get_tag_counts():
            """获取标签计数"""
            try:
                area = request.args.get('area', type=str)
                db = get_db()
                tag_service = get_tag_service(db)
                counts = tag_service.get_tag_counts(area)
                return jsonify(counts)
            except Exception as e:
                print(f'获取标签计数失败: {e}')
                import traceback
                traceback.print_exc()
                return jsonify({'error': str(e)}), 500
    else:
        print('[WARN] 标签服务不可用，注册标签API错误处理路由')
        # 添加诊断路由和错误处理路由
        @app.route('/api/tags/status', methods=['GET'])
        def tag_service_status():
            """检查标签服务状态"""
            return jsonify({
                'available': False,
                'message': '标签服务模块未加载，请检查后端日志',
                'error': 'TAG_SERVICE_AVAILABLE = False'
            }), 503
        
        # 如果标签服务不可用，为/api/tags提供友好的错误响应
        @app.route('/api/tags', methods=['GET'])
        def get_tags_unavailable():
            """获取所有标签（标签服务不可用时的处理）"""
            return jsonify({
                'error': '标签服务不可用',
                'message': '标签服务模块未加载，请检查后端日志并确保tag_service.py文件存在且无错误',
                'available': False
            }), 503
    
    # 确保 /api/tags 路由已注册（诊断信息）
    print(f'[DEBUG] TAG_SERVICE_AVAILABLE = {_tag_service_available}')
    print(f'[DEBUG] /api/tags 路由已注册')

    app.run(debug=True, port=8000, threaded=True)

