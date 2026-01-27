"""
数据库接口模块 - Doris 版本
使用 Apache Doris 数据库存储人员、流动记录和地图数据

主要功能：
- 人员信息管理（增删改查）
- 重点人员管理
- 流动记录管理
- 地图数据管理
- 趋势数据管理
- 流动统计管理

数据库表结构：
- people: 人员基本信息表
- key_persons: 重点人员表（支持多类别）
- movements: 人员流动记录表
- map_data: 地图数据表（各省份监测人数）
- trend_data: 趋势数据表（每日统计数据）
- flow_statistics: 流动统计表（各地区流动数量）

作者：系统开发团队
版本：2.0.0 - Doris 版本
"""
import os
import json
import random
import pymysql
from typing import List, Dict, Optional
from datetime import datetime

# Doris 数据库连接配置
# 注意：根据 docker-compose.yaml，FE 节点的 MySQL 查询端口映射为 9031, 9032, 9033
# 当前使用 FE-02 (端口 9032)，因为 FE-01 可能未启动
DB_CONFIG = {
    'host': os.getenv('DORIS_HOST', 'localhost'),
    'port': int(os.getenv('DORIS_PORT', 9032)),
    'user': os.getenv('DORIS_USER', 'root'),
    'password': os.getenv('DORIS_PASSWORD', ''),
    'database': os.getenv('DORIS_DATABASE', 'flu_monitoring'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}


class Database:
    """
    Doris数据库操作类
    
    提供对数据库的所有操作接口，包括：
    - 数据库连接管理
    - 数据表的创建和维护
    - CRUD操作（增删改查）
    - 数据统计和查询
    
    使用方式：
        db = Database()
        db.connect()
        # 执行操作
        db.disconnect()
    
    或者使用上下文管理器：
        with Database() as db:
            # 执行操作
    """
    
    def __init__(self, db_config: Dict = None):
        """
        初始化数据库对象
        
        Args:
            db_config: 数据库配置字典，如果为None则使用默认配置
        """
        self.db_config = db_config or DB_CONFIG.copy()
        self.connection = None
    
    def connect(self):
        """
        连接数据库
        
        功能：
        - 建立Doris数据库连接（通过MySQL协议）
        - 自动创建数据库（如果不存在）
        - 自动创建数据表（如果不存在）
        
        Returns:
            pymysql.Connection: 数据库连接对象
        """
        # 先连接不指定数据库，创建数据库
        temp_config = self.db_config.copy()
        database = temp_config.pop('database')
        
        try:
            temp_conn = pymysql.connect(**temp_config)
            cursor = temp_conn.cursor()
            # Doris 使用简化的 CREATE DATABASE 语法，不支持 CHARACTER SET 和 COLLATE
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            cursor.close()
            temp_conn.close()
        except Exception as e:
            print(f'[WARN] 创建数据库失败（可能已存在）: {e}', flush=True)
        
        # 连接到指定数据库
        self.connection = pymysql.connect(**self.db_config)
        self._create_tables()  # 确保所有表都存在
        return self.connection
    
    def disconnect(self):
        """
        断开数据库连接
        释放数据库资源
        """
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def _create_tables(self):
        """
        创建数据表
        
        如果表已存在则跳过，如果不存在则创建
        同时处理表结构的升级（添加新字段）
        
        创建的表包括：
        - people: 人员基本信息表
        - key_persons: 重点人员表
        - movements: 流动记录表
        - map_data: 地图数据表
        - trend_data: 趋势数据表
        - flow_statistics: 流动统计表
        """
        cursor = self.connection.cursor()
        
        # 人员表 - 使用 Doris 的数据类型和表属性
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS people (
                id BIGINT NOT NULL AUTO_INCREMENT,
                id_card VARCHAR(50) NOT NULL,
                name VARCHAR(255) NOT NULL,
                region VARCHAR(100) NOT NULL,
                age INT NOT NULL,
                phone VARCHAR(20) NOT NULL,
                status VARCHAR(20) NOT NULL,
                avatar VARCHAR(500),
                last_update DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                gender VARCHAR(10),
                occupation VARCHAR(100),
                tags TEXT,
                education_history TEXT,
                work_history TEXT,
                social_media TEXT,
                visit_records TEXT,
                flight_records TEXT,
                train_records TEXT,
                hometown VARCHAR(100),
                nationality VARCHAR(50),
                visa_type VARCHAR(50),
                institution VARCHAR(200)
            ) ENGINE=OLAP
            UNIQUE KEY(id, id_card)
            DISTRIBUTED BY HASH(id) BUCKETS 10
            PROPERTIES (
                "replication_num" = "1",
                "storage_format" = "V2"
            )
        ''')
        
        # 添加新字段（如果表已存在，使用ALTER TABLE）
        columns_to_add = [
            ('gender', 'VARCHAR(10)'),
            ('occupation', 'VARCHAR(100)'),
            ('tags', 'TEXT'),
            ('education_history', 'TEXT'),
            ('work_history', 'TEXT'),
            ('social_media', 'TEXT'),
            ('visit_records', 'TEXT'),
            ('flight_records', 'TEXT'),
            ('train_records', 'TEXT'),
            ('hometown', 'VARCHAR(100)'),
            ('nationality', 'VARCHAR(50)'),
            ('visa_type', 'VARCHAR(50)'),
            ('institution', 'VARCHAR(200)')
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                cursor.execute(f'ALTER TABLE people ADD COLUMN {col_name} {col_type}')
            except Exception:
                pass  # 字段已存在
        
        # 重点人员表（支持多个类别）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS key_persons (
                id BIGINT NOT NULL AUTO_INCREMENT,
                person_id BIGINT NOT NULL,
                category VARCHAR(50) NOT NULL,
                priority_level INT DEFAULT 1,
                reason TEXT,
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=OLAP
            UNIQUE KEY(id, person_id, category)
            DISTRIBUTED BY HASH(id) BUCKETS 10
            PROPERTIES (
                "replication_num" = "1",
                "storage_format" = "V2"
            )
        ''')
        
        # 创建重点人员索引
        try:
            cursor.execute('CREATE INDEX idx_key_persons_category ON key_persons(category)')
        except Exception:
            pass
        try:
            cursor.execute('CREATE INDEX idx_key_persons_person ON key_persons(person_id)')
        except Exception:
            pass
        
        # 流动记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movements (
                id BIGINT NOT NULL AUTO_INCREMENT,
                person_id BIGINT NOT NULL,
                person_name VARCHAR(255),
                avatar VARCHAR(500),
                from_region VARCHAR(100) NOT NULL,
                to_region VARCHAR(100) NOT NULL,
                movement_time DATETIME NOT NULL,
                status VARCHAR(20) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=OLAP
            DUPLICATE KEY(id)
            DISTRIBUTED BY HASH(id) BUCKETS 10
            PROPERTIES (
                "replication_num" = "1",
                "storage_format" = "V2"
            )
        ''')
        
        # 地图数据表（存储各省份的监测人数）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS map_data (
                id BIGINT NOT NULL AUTO_INCREMENT,
                province_name VARCHAR(100) NOT NULL,
                value INT NOT NULL DEFAULT 0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=OLAP
            UNIQUE KEY(id, province_name)
            DISTRIBUTED BY HASH(id) BUCKETS 10
            PROPERTIES (
                "replication_num" = "1",
                "storage_format" = "V2"
            )
        ''')
        
        # 趋势数据表（存储每日的趋势数据）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trend_data (
                id BIGINT NOT NULL AUTO_INCREMENT,
                date DATE NOT NULL,
                confirmed_count INT NOT NULL DEFAULT 0,
                suspected_count INT NOT NULL DEFAULT 0,
                recovered_count INT NOT NULL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=OLAP
            UNIQUE KEY(id, date)
            DISTRIBUTED BY HASH(id) BUCKETS 10
            PROPERTIES (
                "replication_num" = "1",
                "storage_format" = "V2"
            )
        ''')
        
        # 流动统计表（存储各地区的流动数量）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flow_statistics (
                id BIGINT NOT NULL AUTO_INCREMENT,
                region VARCHAR(100) NOT NULL,
                period VARCHAR(20) NOT NULL,
                flow_count INT NOT NULL DEFAULT 0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=OLAP
            UNIQUE KEY(id, region, period)
            DISTRIBUTED BY HASH(id) BUCKETS 10
            PROPERTIES (
                "replication_num" = "1",
                "storage_format" = "V2"
            )
        ''')
        
        # 本地人员表（用户导入的数据）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS local_people (
                id BIGINT NOT NULL AUTO_INCREMENT,
                name VARCHAR(255) NOT NULL,
                id_card VARCHAR(50),
                region VARCHAR(100),
                age INT,
                phone VARCHAR(20),
                status VARCHAR(20),
                avatar VARCHAR(500),
                last_update DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                gender VARCHAR(10),
                occupation VARCHAR(100),
                tags TEXT,
                education_history TEXT,
                work_history TEXT,
                social_media TEXT,
                visit_records TEXT,
                flight_records TEXT,
                train_records TEXT,
                hometown VARCHAR(100),
                nationality VARCHAR(50),
                visa_type VARCHAR(50),
                institution VARCHAR(200)
            ) ENGINE=OLAP
            DUPLICATE KEY(id)
            DISTRIBUTED BY HASH(id) BUCKETS 10
            PROPERTIES (
                "replication_num" = "1",
                "storage_format" = "V2"
            )
        ''')
        
        # 创建索引
        indexes = [
            ('idx_people_region', 'people', 'region'),
            ('idx_people_status', 'people', 'status'),
            ('idx_movements_person', 'movements', 'person_id'),
            ('idx_movements_time', 'movements', 'movement_time'),
            ('idx_trend_data_date', 'trend_data', 'date'),
            ('idx_flow_statistics_region', 'flow_statistics', 'region'),
            ('idx_local_people_id_card', 'local_people', 'id_card'),
            ('idx_local_people_phone', 'local_people', 'phone')
        ]
        
        for idx_name, table_name, column_name in indexes:
            try:
                cursor.execute(f'CREATE INDEX {idx_name} ON {table_name}({column_name})')
            except Exception:
                pass  # 索引已存在
        
        self.connection.commit()
        cursor.close()
    
    # ========== 人员相关操作 ==========
    
    def get_people(self, page: int = None, page_size: int = None) -> List[Dict]:
        """获取人员列表，支持分页"""
        cursor = self.connection.cursor()
        try:
            if page is not None and page_size is not None:
                offset = (page - 1) * page_size
                cursor.execute('SELECT * FROM people ORDER BY id DESC LIMIT %s OFFSET %s', (page_size, offset))
                rows = cursor.fetchall()
                return [self._row_to_dict(row) for row in rows]
            else:
                cursor.execute('SELECT * FROM people ORDER BY id DESC')
                rows = cursor.fetchall()
                return [self._row_to_dict(row) for row in rows]
        finally:
            cursor.close()
    
    def get_people_count(self) -> int:
        """获取人员总数"""
        cursor = self.connection.cursor()
        try:
            cursor.execute('SELECT COUNT(*) as count FROM people')
            row = cursor.fetchone()
            return row['count'] if row else 0
        finally:
            cursor.close()
    
    def get_person(self, person_id: int) -> Optional[Dict]:
        """获取单个人员"""
        cursor = self.connection.cursor()
        try:
            cursor.execute('SELECT * FROM people WHERE id = %s', (person_id,))
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None
        finally:
            cursor.close()
    
    def create_person(self, data: Dict) -> Dict:
        """创建人员"""
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                INSERT INTO people (name, id_card, region, age, phone, status, avatar, last_update, 
                                  gender, occupation, tags, education_history, work_history, social_media,
                                  visit_records, flight_records, train_records, hometown, nationality, visa_type, institution)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                data['name'],
                data['idCard'],
                data.get('region', ''),  # 保留region字段用于兼容，但主要使用hometown
                int(data['age']),
                data['phone'],
                data['status'],
                data.get('avatar', ''),
                data.get('lastUpdate', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                data.get('gender', ''),
                data.get('occupation', ''),
                json.dumps(data.get('tags', []), ensure_ascii=False) if isinstance(data.get('tags'), list) else data.get('tags', '[]'),
                json.dumps(data.get('educationHistory', []), ensure_ascii=False) if isinstance(data.get('educationHistory'), list) else data.get('educationHistory', '[]'),
                json.dumps(data.get('workHistory', []), ensure_ascii=False) if isinstance(data.get('workHistory'), list) else data.get('workHistory', '[]'),
                json.dumps(data.get('socialMedia', []), ensure_ascii=False) if isinstance(data.get('socialMedia'), list) else data.get('socialMedia', '[]'),
                json.dumps(data.get('visitRecords', []), ensure_ascii=False) if isinstance(data.get('visitRecords'), list) else data.get('visitRecords', '[]'),
                json.dumps(data.get('flightRecords', []), ensure_ascii=False) if isinstance(data.get('flightRecords'), list) else data.get('flightRecords', '[]'),
                json.dumps(data.get('trainRecords', []), ensure_ascii=False) if isinstance(data.get('trainRecords'), list) else data.get('trainRecords', '[]'),
                data.get('hometown', ''),
                data.get('nationality', ''),
                data.get('visaType', ''),
                data.get('institution', '')
            ))
            self.connection.commit()
            person_id = cursor.lastrowid
            return self.get_person(person_id)
        finally:
            cursor.close()
    
    def batch_create_people(self, people_list: List[Dict]) -> int:
        """批量创建人员"""
        count = 0
        errors = []
        for i, person in enumerate(people_list):
            try:
                # 验证必要字段
                if not person.get('name') or not person.get('idCard'):
                    errors.append(f'第{i+1}条数据缺少必要字段：name或idCard')
                    continue
                
                # 如果没有提供头像，随机分配一个
                if not person.get('avatar'):
                    person['avatar'] = f'/api/avatars/avatar_{random.randint(1, 20)}.jpg'
                
                result = self.create_person(person)
                if result:
                    count += 1
                else:
                    errors.append(f'第{i+1}条数据创建失败：{person.get("name", "未知")}')
            except Exception as e:
                import traceback
                error_msg = f'导入人员失败: {person.get("name", "未知")}, 错误: {str(e)}'
                print(error_msg)
                print(traceback.format_exc())
                errors.append(error_msg)
                continue
        
        if errors:
            print(f'导入完成，成功{count}条，失败{len(errors)}条')
            for error in errors[:5]:  # 只打印前5个错误
                print(f'  - {error}')
        
        return count
    
    # ========== 本地人员相关操作 ==========
    
    def batch_create_local_people(self, people_list: List[Dict]) -> int:
        """批量创建本地人员（用户导入的数据）"""
        count = 0
        errors = []
        cursor = self.connection.cursor()
        
        import sys
        import json
        import os
        log_path = r'f:\all\projects\chaoyangV1.0.1\.cursor\debug.log'
        sys.stdout.flush()
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'id': f'log_{int(__import__("time").time() * 1000)}',
                    'timestamp': int(__import__("time").time() * 1000),
                    'location': 'database.py:420',
                    'message': 'batch_create_local_people开始',
                    'data': {'people_count': len(people_list)},
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'D'
                }, ensure_ascii=False) + '\n')
        except: pass
        # #endregion
        print(f'[DEBUG] 开始导入本地人员，共 {len(people_list)} 条数据', flush=True)
        if len(people_list) > 0:
            print(f'[DEBUG] 第一条数据示例: {people_list[0]}', flush=True)
            print(f'[DEBUG] 第一条数据的键: {list(people_list[0].keys())}', flush=True)
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'id': f'log_{int(__import__("time").time() * 1000)}',
                        'timestamp': int(__import__("time").time() * 1000),
                        'location': 'database.py:427',
                        'message': '第一条数据详情',
                        'data': {'first_person': people_list[0], 'keys': list(people_list[0].keys())},
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'D'
                    }, ensure_ascii=False) + '\n')
            except: pass
            # #endregion
        
        for i, person in enumerate(people_list):
            try:
                # 打印当前处理的数据
                print(f'[DEBUG] 处理第 {i+1} 条数据，字段: {list(person.keys())}')
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'id': f'log_{int(__import__("time").time() * 1000)}',
                            'timestamp': int(__import__("time").time() * 1000),
                            'location': 'database.py:433',
                            'message': '处理数据',
                            'data': {'index': i+1, 'keys': list(person.keys()), 'person': person},
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'D'
                        }, ensure_ascii=False) + '\n')
                except: pass
                # #endregion
                
                # 处理可能的字段名变体（支持中英文、大小写）
                name_value = None
                for key in ['name', 'Name', 'NAME', '姓名', '名字']:
                    if key in person:
                        name_value = person[key]
                        # 检查值是否为空（处理NaN、空字符串等情况）
                        if name_value is not None:
                            name_str = str(name_value).strip()
                            if name_str and name_str.lower() not in ['nan', 'none', '']:
                                if key != 'name':
                                    person['name'] = name_value
                                break
                        name_value = None
                
                # 验证必要字段
                if not name_value:
                    error_msg = f'第{i+1}条数据缺少必要字段：name（姓名）'
                    # #region agent log
                    try:
                        with open(log_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({
                                'id': f'log_{int(__import__("time").time() * 1000)}',
                                'timestamp': int(__import__("time").time() * 1000),
                                'location': 'database.py:450',
                                'message': 'name字段验证失败',
                                'data': {'index': i+1, 'keys': list(person.keys()), 'person': person, 'name_in_person': 'name' in person, 'name_value': person.get('name') if 'name' in person else None},
                                'sessionId': 'debug-session',
                                'runId': 'run1',
                                'hypothesisId': 'D'
                            }, ensure_ascii=False) + '\n')
                    except: pass
                    # #endregion
                    print(f'[WARN] {error_msg}', flush=True)
                    print(f'[WARN] 可用字段: {list(person.keys())}', flush=True)
                    print(f'[WARN] 字段值: {person}', flush=True)
                    print(f'[WARN] name字段是否存在: {"name" in person}', flush=True)
                    if 'name' in person:
                        print(f'[WARN] name字段值: {person["name"]}, 类型: {type(person["name"])}', flush=True)
                    errors.append(error_msg)
                    continue
                
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'id': f'log_{int(__import__("time").time() * 1000)}',
                            'timestamp': int(__import__("time").time() * 1000),
                            'location': 'database.py:461',
                            'message': 'name字段验证通过',
                            'data': {'index': i+1, 'name_value': name_value},
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'D'
                        }, ensure_ascii=False) + '\n')
                except: pass
                # #endregion
                print(f'[DEBUG] 第 {i+1} 条数据验证通过，姓名: {name_value}')
                
                # 如果没有提供头像，随机分配一个
                if not person.get('avatar'):
                    person['avatar'] = f'/api/avatars/avatar_{random.randint(1, 20)}.jpg'
                
                # 处理age字段，确保是整数
                age_value = person.get('age')
                if age_value:
                    try:
                        age_value = int(float(str(age_value)))  # 支持字符串数字和浮点数
                    except (ValueError, TypeError):
                        age_value = 0
                else:
                    age_value = 0
                
                # 处理idCard字段，确保是字符串格式
                id_card_value = person.get('idCard') or person.get('id_card')
                if id_card_value is not None:
                    # 处理数字格式（Excel可能读取为数字）
                    if isinstance(id_card_value, (int, float)):
                        id_card_value = str(int(id_card_value))
                    elif isinstance(id_card_value, str):
                        # 处理科学计数法格式
                        if 'E+' in id_card_value.upper() or 'e+' in id_card_value:
                            try:
                                id_card_value = str(int(float(id_card_value)))
                            except:
                                id_card_value = str(id_card_value)
                        # 处理空字符串
                        if id_card_value.strip() == '' or id_card_value.lower() == 'nan':
                            id_card_value = None
                    else:
                        id_card_value = str(id_card_value) if id_card_value else None
                
                # 转换字段名（从驼峰到数据库字段）
                insert_params = (
                    person.get('name'),
                    id_card_value,
                    person.get('region') or '',
                    age_value,
                    person.get('phone') or '',
                    person.get('status') or '正常',
                    person.get('avatar'),
                    person.get('lastUpdate') or datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    person.get('gender') or '',
                    person.get('occupation') or '',
                    json.dumps(person.get('tags', []), ensure_ascii=False) if isinstance(person.get('tags'), list) else person.get('tags', '[]'),
                    json.dumps(person.get('educationHistory', []), ensure_ascii=False) if isinstance(person.get('educationHistory'), list) else person.get('educationHistory', '[]'),
                    json.dumps(person.get('workHistory', []), ensure_ascii=False) if isinstance(person.get('workHistory'), list) else person.get('workHistory', '[]'),
                    json.dumps(person.get('socialMedia', []), ensure_ascii=False) if isinstance(person.get('socialMedia'), list) else person.get('socialMedia', '[]'),
                    json.dumps(person.get('visitRecords', []), ensure_ascii=False) if isinstance(person.get('visitRecords'), list) else person.get('visitRecords', '[]'),
                    json.dumps(person.get('flightRecords', []), ensure_ascii=False) if isinstance(person.get('flightRecords'), list) else person.get('flightRecords', '[]'),
                    json.dumps(person.get('trainRecords', []), ensure_ascii=False) if isinstance(person.get('trainRecords'), list) else person.get('trainRecords', '[]'),
                    person.get('hometown') or '',
                    person.get('nationality') or '',
                    person.get('visaType') or person.get('visa_type') or '',
                    person.get('institution') or ''
                )
                
                cursor.execute('''
                    INSERT INTO local_people (
                        name, id_card, region, age, phone, status, avatar, last_update,
                        gender, occupation, tags, education_history, work_history, social_media,
                        visit_records, flight_records, train_records, hometown, nationality, visa_type, institution
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', insert_params)
                
                count += 1
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'id': f'log_{int(__import__("time").time() * 1000)}',
                            'timestamp': int(__import__("time").time() * 1000),
                            'location': 'database.py:530',
                            'message': '数据库插入成功',
                            'data': {'index': i+1, 'name': person.get("name")},
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'D'
                        }, ensure_ascii=False) + '\n')
                except: pass
                # #endregion
                print(f'[DEBUG] 成功导入第 {i+1} 条数据: {person.get("name")}')
            except Exception as e:
                import traceback
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'id': f'log_{int(__import__("time").time() * 1000)}',
                            'timestamp': int(__import__("time").time() * 1000),
                            'location': 'database.py:532',
                            'message': '数据库插入异常',
                            'data': {'index': i+1, 'error': str(e), 'error_type': type(e).__name__},
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'D'
                        }, ensure_ascii=False) + '\n')
                except: pass
                # #endregion
                error_msg = f'导入本地人员失败: 第{i+1}条数据 {person.get("name", "未知")}, 错误: {str(e)}'
                print(f'[ERROR] {error_msg}')
                print(traceback.format_exc())
                errors.append(error_msg)
                continue
        
        try:
            self.connection.commit()
            print(f'[DEBUG] 数据库提交成功')
        except Exception as e:
            print(f'[ERROR] 数据库提交失败: {str(e)}')
            import traceback
            traceback.print_exc()
            self.connection.rollback()
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'id': f'log_{int(__import__("time").time() * 1000)}',
                    'timestamp': int(__import__("time").time() * 1000),
                    'location': 'database.py:657',
                    'message': 'batch_create_local_people完成',
                    'data': {'count': count, 'errors_count': len(errors), 'errors': errors[:10]},
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'D'
                }, ensure_ascii=False) + '\n')
        except: pass
        # #endregion
        print(f'[DEBUG] 导入完成，成功 {count} 条，失败 {len(errors)} 条')
        if errors:
            for error in errors[:10]:  # 打印前10个错误
                print(f'  - {error}')
        
        return count
    
    def get_local_people(self) -> List[Dict]:
        """获取所有本地人员，同时查找匹配的系统库人员"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM local_people ORDER BY id DESC')
        rows = cursor.fetchall()
        result = []
        for row in rows:
            person = self._row_to_dict(row)
            # 注意：_row_to_dict已经将id_card转换为idCard，last_update转换为lastUpdate，created_at转换为createdAt
            # 但为了确保字段存在，我们检查一下
            if 'idCard' not in person:
                person['idCard'] = row['id_card'] if 'id_card' in row.keys() else None
            if 'lastUpdate' not in person:
                person['lastUpdate'] = row['last_update'] if 'last_update' in row.keys() else None
            if 'createdAt' not in person:
                person['createdAt'] = row['created_at'] if 'created_at' in row.keys() else None
            
            # 调试：打印"高敏"的匹配信息
            if person.get('name') == '高敏':
                print(f'[DEBUG] 高敏数据: idCard={person.get("idCard")}, phone={person.get("phone")}, name={person.get("name")}', flush=True)
            # 解析JSON字段
            for json_field in ['tags', 'education_history', 'work_history', 'social_media', 'visit_records', 'flight_records', 'train_records']:
                field_value = person.get(json_field)
                if field_value and isinstance(field_value, str):
                    try:
                        person[json_field] = json.loads(field_value)
                    except:
                        person[json_field] = []
            # 转换为前端需要的字段名
            if 'tags' in person:
                person['tags'] = person.get('tags', [])
            if 'education_history' in person:
                person['educationHistory'] = person.get('education_history', [])
            if 'work_history' in person:
                person['workHistory'] = person.get('work_history', [])
            if 'social_media' in person:
                person['socialMedia'] = person.get('social_media', [])
            if 'visit_records' in person:
                person['visitRecords'] = person.get('visit_records', [])
            if 'flight_records' in person:
                person['flightRecords'] = person.get('flight_records', [])
            if 'train_records' in person:
                person['trainRecords'] = person.get('train_records', [])
            if 'visa_type' in person:
                person['visaType'] = person.get('visa_type')
            
            # 查找匹配的系统库人员（名字+手机号 或 名字+身份证号）
            # 确保使用正确的字段名（idCard 或 id_card）
            id_card_for_match = person.get('idCard') or person.get('id_card')
            phone_for_match = person.get('phone')
            name_for_match = person.get('name')
            
            # 调试：特别关注"高敏"
            if name_for_match == '高敏':
                print(f'[DEBUG] 高敏准备匹配: name="{name_for_match}", idCard="{id_card_for_match}", phone="{phone_for_match}"', flush=True)
                print(f'[DEBUG] 高敏person字典中的字段: {list(person.keys())}', flush=True)
                print(f'[DEBUG] 高敏person.idCard值: {person.get("idCard")}', flush=True)
                print(f'[DEBUG] 高敏person.id_card值: {person.get("id_card")}', flush=True)
            else:
                print(f'[DEBUG] 准备匹配: name="{name_for_match}", idCard="{id_card_for_match}", phone="{phone_for_match}"', flush=True)
            
            matched_system_person = self._find_matched_system_person(
                name_for_match,
                id_card_for_match,
                phone_for_match
            )
            if matched_system_person:
                person['hasSystemMatch'] = True
                person['systemPerson'] = matched_system_person
                person['systemPersonId'] = matched_system_person.get('id')
                
                # 检查匹配的系统库人员是否在重点人员库中
                key_person_info = self._find_key_person_by_person_id(matched_system_person.get('id'))
                if key_person_info:
                    person['hasKeyPersonMatch'] = True
                    person['keyPerson'] = key_person_info
                    person['keyPersonId'] = key_person_info.get('keyPersonId')
                    person['keyPersonCategory'] = key_person_info.get('category')
                    if name_for_match == '袁浩' or name_for_match == '高敏':
                        try:
                            category = key_person_info.get("category", "")
                            print(f'[DEBUG] [OK] {name_for_match}匹配成功且为重点人员: 自建库人员 "{person.get("name")}" (ID: {person.get("id")}) 匹配到系统库人员 "{matched_system_person.get("name")}" (ID: {matched_system_person.get("id")}), 重点人员类别: {category}', flush=True)
                        except:
                            print(f'[DEBUG] [OK] {name_for_match}匹配成功且为重点人员', flush=True)
                else:
                    person['hasKeyPersonMatch'] = False
                    if name_for_match == '袁浩' or name_for_match == '高敏':
                        print(f'[DEBUG] [OK] {name_for_match}匹配成功但不是重点人员: 自建库人员 "{person.get("name")}" (ID: {person.get("id")}) 匹配到系统库人员 "{matched_system_person.get("name")}" (ID: {matched_system_person.get("id")})', flush=True)
                
                if name_for_match == '高敏':
                    print(f'[DEBUG] [OK] 高敏匹配成功: 自建库人员 "{person.get("name")}" (ID: {person.get("id")}) 匹配到系统库人员 "{matched_system_person.get("name")}" (ID: {matched_system_person.get("id")})', flush=True)
                    print(f'[DEBUG] 高敏hasSystemMatch设置为: {person.get("hasSystemMatch")}', flush=True)
                    print(f'[DEBUG] 高敏systemPersonId设置为: {person.get("systemPersonId")}', flush=True)
                elif name_for_match == '袁浩':
                    print(f'[DEBUG] [OK] 袁浩匹配成功: 自建库人员 "{person.get("name")}" (ID: {person.get("id")}) 匹配到系统库人员 "{matched_system_person.get("name")}" (ID: {matched_system_person.get("id")})', flush=True)
                    print(f'[DEBUG] 袁浩hasSystemMatch设置为: {person.get("hasSystemMatch")}', flush=True)
                    print(f'[DEBUG] 袁浩hasKeyPersonMatch设置为: {person.get("hasKeyPersonMatch")}', flush=True)
                    print(f'[DEBUG] 袁浩keyPersonCategory设置为: {person.get("keyPersonCategory")}', flush=True)
                else:
                    print(f'[DEBUG] 匹配成功: 自建库人员 "{person.get("name")}" (ID: {person.get("id")}) 匹配到系统库人员 "{matched_system_person.get("name")}" (ID: {matched_system_person.get("id")})', flush=True)
            else:
                person['hasSystemMatch'] = False
                person['hasKeyPersonMatch'] = False
                if name_for_match == '高敏':
                    print(f'[DEBUG] [FAIL] 高敏未匹配: 自建库人员 "{person.get("name")}" (ID: {person.get("id")}, 身份证: {person.get("idCard")}, 手机: {person.get("phone")}) 未找到匹配的系统库人员', flush=True)
                    print(f'[DEBUG] 高敏hasSystemMatch设置为: {person.get("hasSystemMatch")}', flush=True)
                elif name_for_match == '袁浩':
                    print(f'[DEBUG] [FAIL] 袁浩未匹配系统库: 自建库人员 "{person.get("name")}" (ID: {person.get("id")}, 身份证: {person.get("idCard")}, 手机: {person.get("phone")}) 未找到匹配的系统库人员', flush=True)
                    print(f'[DEBUG] 袁浩hasSystemMatch设置为: {person.get("hasSystemMatch")}', flush=True)
                else:
                    print(f'[DEBUG] 未匹配: 自建库人员 "{person.get("name")}" (ID: {person.get("id")}, 身份证: {person.get("idCard")}, 手机: {person.get("phone")}) 未找到匹配的系统库人员', flush=True)
            
            result.append(person)
        return result
    
    def _find_matched_system_person(self, name: str, id_card: str = None, phone: str = None) -> Dict:
        """
        查找匹配的系统库人员
        匹配条件：名字+手机号 或 名字+身份证号 相同
        
        Args:
            name: 姓名
            id_card: 身份证号
            phone: 手机号
            
        Returns:
            匹配的系统库人员信息，如果没有匹配则返回None
        """
        if not name:
            return None
        
        # 标准化输入数据
        name = str(name).strip() if name else None
        id_card = str(id_card).strip() if id_card else None
        phone = str(phone).strip() if phone else None
        
        # 处理空值
        if not name or name.lower() in ['nan', 'none', '']:
            return None
        
        # 处理身份证号：去除空格，统一格式
        if id_card:
            id_card = id_card.replace(' ', '').replace('-', '').replace('_', '')
            if id_card.lower() in ['nan', 'none', '']:
                id_card = None
        
        # 处理手机号：去除空格，统一格式，转换为字符串
        if phone:
            if isinstance(phone, (int, float)):
                phone = str(int(phone))
            else:
                phone = str(phone).replace(' ', '').replace('-', '').replace('_', '')
            if phone.lower() in ['nan', 'none', ''] or phone == '0':
                phone = None
        
        if not id_card and not phone:
            return None
        
        cursor = self.connection.cursor()
        
        # 辅助函数：转换系统库人员数据格式
        def _convert_system_person(row):
            person = self._row_to_dict(row)
            # 转换字段名
            person['idCard'] = person.get('id_card')
            person['lastUpdate'] = person.get('last_update')
            person['createdAt'] = person.get('created_at')
            # 解析JSON字段
            for json_field in ['tags', 'education_history', 'work_history', 'social_media', 'visit_records', 'flight_records', 'train_records']:
                field_value = person.get(json_field)
                if field_value and isinstance(field_value, str):
                    try:
                        person[json_field] = json.loads(field_value)
                    except:
                        person[json_field] = []
            # 转换为前端需要的字段名
            if 'tags' in person:
                person['tags'] = person.get('tags', [])
            if 'education_history' in person:
                person['educationHistory'] = person.get('education_history', [])
            if 'work_history' in person:
                person['workHistory'] = person.get('work_history', [])
            if 'social_media' in person:
                person['socialMedia'] = person.get('social_media', [])
            if 'visit_records' in person:
                person['visitRecords'] = person.get('visit_records', [])
            if 'flight_records' in person:
                person['flightRecords'] = person.get('flight_records', [])
            if 'train_records' in person:
                person['trainRecords'] = person.get('train_records', [])
            return person
        
        # 优先匹配：名字+身份证号
        if id_card:
            # 标准化身份证号：去除所有空格和特殊字符
            id_card_clean = str(id_card).replace(' ', '').replace('-', '').replace('_', '').strip()
            
            print(f'[DEBUG] 尝试匹配（身份证）: name="{name}", id_card原始="{id_card}", id_card清理后="{id_card_clean}"', flush=True)
            
            # 尝试精确匹配（清理后的身份证号，使用REPLACE函数清理数据库中的值）
            cursor.execute('''
                SELECT * FROM people 
                WHERE TRIM(name) = %s AND REPLACE(REPLACE(REPLACE(TRIM(id_card), ' ', ''), '-', ''), '_', '') = %s
                LIMIT 1
            ''', (name, id_card_clean))
            row = cursor.fetchone()
            if row:
                print(f'[DEBUG] [OK] 匹配成功（精确匹配-身份证）: name="{name}", id_card="{id_card_clean}"', flush=True)
                return _convert_system_person(row)
            
            # 尝试忽略大小写匹配
            cursor.execute('''
                SELECT * FROM people 
                WHERE LOWER(TRIM(name)) = LOWER(%s) AND REPLACE(REPLACE(REPLACE(TRIM(id_card), ' ', ''), '-', ''), '_', '') = %s
                LIMIT 1
            ''', (name, id_card_clean))
            row = cursor.fetchone()
            if row:
                print(f'[DEBUG] [OK] 匹配成功（忽略大小写-身份证）: name="{name}", id_card="{id_card_clean}"', flush=True)
                return _convert_system_person(row)
            
            # 尝试直接匹配（不清理，以防数据库中也包含特殊字符）
            cursor.execute('''
                SELECT * FROM people 
                WHERE TRIM(name) = %s AND TRIM(id_card) = %s
                LIMIT 1
            ''', (name, id_card))
            row = cursor.fetchone()
            if row:
                print(f'[DEBUG] [OK] 匹配成功（直接匹配-身份证）: name="{name}", id_card="{id_card}"', flush=True)
                return _convert_system_person(row)
            
            print(f'[DEBUG] [FAIL] 匹配失败（身份证）: name="{name}", id_card原始="{id_card}", id_card清理后="{id_card_clean}"', flush=True)
            
            # 调试：查询系统库中是否有相同姓名的人员
            cursor.execute('''
                SELECT id, name, id_card, phone FROM people 
                WHERE TRIM(name) = %s OR LOWER(TRIM(name)) = LOWER(%s)
                LIMIT 10
            ''', (name, name))
            debug_rows = cursor.fetchall()
            if debug_rows:
                print(f'[DEBUG] 系统库中找到相同姓名的人员:', flush=True)
                for debug_row in debug_rows:
                    print(f'  - ID: {debug_row["id"]}, 姓名: "{debug_row["name"]}", 身份证: "{debug_row["id_card"]}", 手机: "{debug_row["phone"]}"', flush=True)
            
            # 调试：查询系统库中是否有相同身份证号的人员
            if id_card_clean:
                cursor.execute('''
                    SELECT id, name, id_card, phone FROM people 
                    WHERE REPLACE(REPLACE(REPLACE(TRIM(id_card), ' ', ''), '-', ''), '_', '') = %s
                    LIMIT 10
                ''', (id_card_clean,))
                debug_rows = cursor.fetchall()
                if debug_rows:
                    print(f'[DEBUG] 系统库中找到相同身份证号的人员:', flush=True)
                    for debug_row in debug_rows:
                        print(f'  - ID: {debug_row["id"]}, 姓名: "{debug_row["name"]}", 身份证: "{debug_row["id_card"]}", 手机: "{debug_row["phone"]}"', flush=True)
        
        # 次优匹配：名字+手机号
        if phone:
            # 尝试精确匹配
            cursor.execute('''
                SELECT * FROM people 
                WHERE TRIM(name) = %s AND TRIM(phone) = %s
                LIMIT 1
            ''', (name, phone))
            row = cursor.fetchone()
            if row:
                print(f'[DEBUG] 匹配成功（精确匹配-手机）: name="{name}", phone="{phone}"', flush=True)
                return _convert_system_person(row)
            
            # 尝试忽略大小写匹配
            cursor.execute('''
                SELECT * FROM people 
                WHERE LOWER(TRIM(name)) = LOWER(%s) AND TRIM(phone) = %s
                LIMIT 1
            ''', (name, phone))
            row = cursor.fetchone()
            if row:
                print(f'[DEBUG] 匹配成功（忽略大小写-手机）: name="{name}", phone="{phone}"', flush=True)
                return _convert_system_person(row)
            
            # 尝试数字格式匹配（处理phone可能是数字的情况）
            try:
                phone_num = int(float(phone))
                phone_str = str(phone_num)
                # 尝试多种格式：原始字符串、数字字符串、数字
                cursor.execute('''
                    SELECT * FROM people 
                    WHERE LOWER(TRIM(name)) = LOWER(%s) 
                    AND (TRIM(phone) = %s OR TRIM(phone) = %s OR phone = %s)
                    LIMIT 1
                ''', (name, phone, phone_str, phone_num))
                row = cursor.fetchone()
                if row:
                    print(f'[DEBUG] 匹配成功（数字格式-手机）: name="{name}", phone="{phone}", phone_num={phone_num}', flush=True)
                    return _convert_system_person(row)
            except Exception as e:
                print(f'[DEBUG] 数字格式匹配失败: {e}', flush=True)
            
            print(f'[DEBUG] 匹配失败（手机）: name="{name}", phone="{phone}"', flush=True)
        
        return None
    
    def _find_matched_local_person(self, name: str, id_card: str = None, phone: str = None) -> Dict:
        """
        查找匹配的本地库人员
        匹配条件：名字+手机号 或 名字+身份证号 相同
        
        Args:
            name: 姓名
            id_card: 身份证号
            phone: 手机号
            
        Returns:
            匹配的本地库人员信息，如果没有匹配则返回None
        """
        if not name:
            return None
        
        # 标准化输入数据
        name = str(name).strip() if name else None
        id_card = str(id_card).strip() if id_card else None
        phone = str(phone).strip() if phone else None
        
        # 处理空值
        if not name or name.lower() in ['nan', 'none', '']:
            return None
        
        # 处理身份证号：去除空格，统一格式
        if id_card:
            id_card = id_card.replace(' ', '').replace('-', '').replace('_', '')
            if id_card.lower() in ['nan', 'none', '']:
                id_card = None
        
        # 处理手机号：去除空格，统一格式，转换为字符串
        if phone:
            if isinstance(phone, (int, float)):
                phone = str(int(phone))
            else:
                phone = str(phone).replace(' ', '').replace('-', '').replace('_', '')
            if phone.lower() in ['nan', 'none', ''] or phone == '0':
                phone = None
        
        if not id_card and not phone:
            return None
        
        cursor = self.connection.cursor()
        
        # 辅助函数：转换本地库人员数据格式
        def _convert_local_person(row):
            person = self._row_to_dict(row)
            # 注意：_row_to_dict已经将id_card转换为idCard，last_update转换为lastUpdate，created_at转换为createdAt
            # 但为了确保字段存在，我们检查一下
            if 'idCard' not in person:
                person['idCard'] = row['id_card'] if 'id_card' in row.keys() else None
            if 'lastUpdate' not in person:
                person['lastUpdate'] = row['last_update'] if 'last_update' in row.keys() else None
            if 'createdAt' not in person:
                person['createdAt'] = row['created_at'] if 'created_at' in row.keys() else None
            # 解析JSON字段
            for json_field in ['tags', 'education_history', 'work_history', 'social_media', 'visit_records', 'flight_records', 'train_records']:
                field_value = person.get(json_field)
                if field_value and isinstance(field_value, str):
                    try:
                        person[json_field] = json.loads(field_value)
                    except:
                        person[json_field] = []
            # 转换为前端需要的字段名
            if 'tags' in person:
                person['tags'] = person.get('tags', [])
            if 'education_history' in person:
                person['educationHistory'] = person.get('education_history', [])
            if 'work_history' in person:
                person['workHistory'] = person.get('work_history', [])
            if 'social_media' in person:
                person['socialMedia'] = person.get('social_media', [])
            if 'visit_records' in person:
                person['visitRecords'] = person.get('visit_records', [])
            if 'flight_records' in person:
                person['flightRecords'] = person.get('flight_records', [])
            if 'train_records' in person:
                person['trainRecords'] = person.get('train_records', [])
            if 'visa_type' in person:
                person['visaType'] = person.get('visa_type')
            return person
        
        # 优先匹配：名字+身份证号
        if id_card:
            # 标准化身份证号：去除所有空格和特殊字符
            id_card_clean = str(id_card).replace(' ', '').replace('-', '').replace('_', '').strip()
            
            # 尝试精确匹配（清理后的身份证号，使用REPLACE函数清理数据库中的值）
            cursor.execute('''
                SELECT * FROM local_people 
                WHERE TRIM(name) = %s AND REPLACE(REPLACE(REPLACE(TRIM(id_card), ' ', ''), '-', ''), '_', '') = %s
                LIMIT 1
            ''', (name, id_card_clean))
            row = cursor.fetchone()
            if row:
                return _convert_local_person(row)
            
            # 尝试忽略大小写匹配
            cursor.execute('''
                SELECT * FROM local_people 
                WHERE LOWER(TRIM(name)) = LOWER(%s) AND REPLACE(REPLACE(REPLACE(TRIM(id_card), ' ', ''), '-', ''), '_', '') = %s
                LIMIT 1
            ''', (name, id_card_clean))
            row = cursor.fetchone()
            if row:
                return _convert_local_person(row)
            
            # 尝试直接匹配（不清理，以防数据库中也包含特殊字符）
            cursor.execute('''
                SELECT * FROM local_people 
                WHERE TRIM(name) = %s AND TRIM(id_card) = %s
                LIMIT 1
            ''', (name, id_card))
            row = cursor.fetchone()
            if row:
                return _convert_local_person(row)
        
        # 次优匹配：名字+手机号
        if phone:
            # 尝试精确匹配
            cursor.execute('''
                SELECT * FROM local_people 
                WHERE TRIM(name) = %s AND TRIM(phone) = %s
                LIMIT 1
            ''', (name, phone))
            row = cursor.fetchone()
            if row:
                return _convert_local_person(row)
            
            # 尝试忽略大小写匹配
            cursor.execute('''
                SELECT * FROM local_people 
                WHERE LOWER(TRIM(name)) = LOWER(%s) AND TRIM(phone) = %s
                LIMIT 1
            ''', (name, phone))
            row = cursor.fetchone()
            if row:
                return _convert_local_person(row)
            
            # 尝试数字格式匹配（处理Excel读取为数字的情况）
            try:
                phone_numeric = str(int(float(phone)))
                cursor.execute('''
                    SELECT * FROM local_people 
                    WHERE TRIM(name) = %s AND (TRIM(phone) = %s OR TRIM(phone) = %s)
                    LIMIT 1
                ''', (name, phone, phone_numeric))
                row = cursor.fetchone()
                if row:
                    return _convert_local_person(row)
            except:
                pass
        
        return None
    
    def get_local_person(self, person_id: int) -> Optional[Dict]:
        """获取单个本地人员，同时查找匹配的系统库人员"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM local_people WHERE id = %s', (person_id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        person = self._row_to_dict(row)
        # 注意：_row_to_dict已经将id_card转换为idCard，last_update转换为lastUpdate，created_at转换为createdAt
        # 所以person字典中应该已经有这些字段了，不需要再次转换
        # 但为了确保字段存在，我们检查一下（以防_row_to_dict的逻辑发生变化）
        if 'idCard' not in person:
            # 如果_row_to_dict没有转换，尝试从原始字段获取
            person['idCard'] = row['id_card'] if 'id_card' in row.keys() else None
            print(f'[DEBUG] get_local_person: idCard字段不存在，从row获取: {person.get("idCard")}', flush=True)
        else:
            print(f'[DEBUG] get_local_person: idCard字段已存在: {person.get("idCard")}', flush=True)
        if 'lastUpdate' not in person:
            person['lastUpdate'] = row['last_update'] if 'last_update' in row.keys() else None
        if 'createdAt' not in person:
            person['createdAt'] = row['created_at'] if 'created_at' in row.keys() else None
        
        # 调试：打印person字典中的所有字段
        print(f'[DEBUG] get_local_person: person字段列表: {list(person.keys())}', flush=True)
        print(f'[DEBUG] get_local_person: person.idCard值: {person.get("idCard")}', flush=True)
        # 解析JSON字段
        for json_field in ['tags', 'education_history', 'work_history', 'social_media', 'visit_records', 'flight_records', 'train_records']:
            field_value = person.get(json_field)
            if field_value and isinstance(field_value, str):
                try:
                    person[json_field] = json.loads(field_value)
                except:
                    person[json_field] = []
        # 转换为前端需要的字段名
        if 'tags' in person:
            person['tags'] = person.get('tags', [])
        if 'education_history' in person:
            person['educationHistory'] = person.get('education_history', [])
        if 'work_history' in person:
            person['workHistory'] = person.get('work_history', [])
        if 'social_media' in person:
            person['socialMedia'] = person.get('social_media', [])
        if 'visit_records' in person:
            person['visitRecords'] = person.get('visit_records', [])
        if 'flight_records' in person:
            person['flightRecords'] = person.get('flight_records', [])
        if 'train_records' in person:
            person['trainRecords'] = person.get('train_records', [])
        if 'visa_type' in person:
            person['visaType'] = person.get('visa_type')
        
        # 查找匹配的系统库人员（名字+手机号 或 名字+身份证号）
        matched_system_person = self._find_matched_system_person(
            person.get('name'),
            person.get('idCard'),
            person.get('phone')
        )
        if matched_system_person:
            person['hasSystemMatch'] = True
            person['systemPerson'] = matched_system_person
            person['systemPersonId'] = matched_system_person.get('id')
            
            # 检查匹配的系统库人员是否在重点人员库中
            key_person_info = self._find_key_person_by_person_id(matched_system_person.get('id'))
            if key_person_info:
                person['hasKeyPersonMatch'] = True
                person['keyPerson'] = key_person_info
                person['keyPersonId'] = key_person_info.get('keyPersonId')
                person['keyPersonCategory'] = key_person_info.get('category')
                if person.get('name') == '袁浩':
                    try:
                        category = key_person_info.get("category", "")
                        print(f'[DEBUG] 袁浩(单个)匹配成功且为重点人员: 类别={category}', flush=True)
                    except:
                        print(f'[DEBUG] 袁浩(单个)匹配成功且为重点人员', flush=True)
            else:
                person['hasKeyPersonMatch'] = False
                if person.get('name') == '袁浩':
                    print(f'[DEBUG] 袁浩(单个)匹配成功但不是重点人员', flush=True)
        else:
            person['hasSystemMatch'] = False
            person['hasKeyPersonMatch'] = False
        
        return person
    
    def batch_delete_local_people(self, person_ids: List[int]) -> int:
        """批量删除本地人员"""
        if not person_ids:
            return 0
        
        cursor = self.connection.cursor()
        placeholders = ','.join(['%s'] * len(person_ids))
        cursor.execute(f'DELETE FROM local_people WHERE id IN ({placeholders})', person_ids)
        self.connection.commit()
        return cursor.rowcount
    
    def clear_all_local_people(self) -> int:
        """清空所有本地人员"""
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM local_people')
        count = cursor.rowcount
        self.connection.commit()
        return count
    
    def update_person(self, person_id: int, data: Dict) -> Dict:
        """更新人员"""
        cursor = self.connection.cursor()
        cursor.execute('''
            UPDATE people 
            SET name = %s, id_card = %s, region = %s, age = %s, phone = %s, status = %s, last_update = %s,
                gender = %s, occupation = %s, tags = %s, education_history = %s, work_history = %s, social_media = %s,
                visit_records = %s, flight_records = %s, train_records = %s, hometown = %s, nationality = %s, visa_type = %s, institution = %s
            WHERE id = %s
        ''', (
            data.get('name'),
            data.get('idCard'),
            data.get('region', ''),  # 保留region字段用于兼容
            int(data.get('age', 0)),
            data.get('phone'),
            data.get('status'),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            data.get('gender', ''),
            data.get('occupation', ''),
            json.dumps(data.get('tags', []), ensure_ascii=False) if isinstance(data.get('tags'), list) else data.get('tags', '[]'),
            json.dumps(data.get('educationHistory', []), ensure_ascii=False) if isinstance(data.get('educationHistory'), list) else data.get('educationHistory', '[]'),
            json.dumps(data.get('workHistory', []), ensure_ascii=False) if isinstance(data.get('workHistory'), list) else data.get('workHistory', '[]'),
            json.dumps(data.get('socialMedia', []), ensure_ascii=False) if isinstance(data.get('socialMedia'), list) else data.get('socialMedia', '[]'),
            json.dumps(data.get('visitRecords', []), ensure_ascii=False) if isinstance(data.get('visitRecords'), list) else data.get('visitRecords', '[]'),
            json.dumps(data.get('flightRecords', []), ensure_ascii=False) if isinstance(data.get('flightRecords'), list) else data.get('flightRecords', '[]'),
            json.dumps(data.get('trainRecords', []), ensure_ascii=False) if isinstance(data.get('trainRecords'), list) else data.get('trainRecords', '[]'),
            data.get('hometown', ''),
            data.get('nationality', ''),
            data.get('visaType', ''),
            data.get('institution', ''),
            person_id
        ))
        self.connection.commit()
        return self.get_person(person_id)
    
    def delete_person(self, person_id: int) -> bool:
        """删除人员"""
        cursor = self.connection.cursor()
        try:
            cursor.execute('DELETE FROM people WHERE id = %s', (person_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
    
    def count_people_by_status(self) -> Dict[str, int]:
        """按状态统计人员数量"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT status, COUNT(*) as count FROM people GROUP BY status')
        result = {}
        for row in cursor.fetchall():
            result[row['status']] = row['count']
        return result
    
    # ========== 流动记录相关操作 ==========
    
    def get_movements(self, filters: Optional[Dict] = None, limit: Optional[int] = None) -> List[Dict]:
        """获取流动记录"""
        cursor = self.connection.cursor()
        query = 'SELECT * FROM movements'
        params = []
        
        if filters:
            conditions = []
            if 'person_id' in filters:
                conditions.append('person_id = %s')
                params.append(filters['person_id'])
            if 'from_date' in filters:
                conditions.append('movement_time >= %s')
                params.append(filters['from_date'])
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY movement_time DESC'
        
        # 如果指定了limit，添加LIMIT子句以提高性能
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [self._row_to_dict(row) for row in rows]
    
    def create_movement(self, data: Dict) -> Dict:
        """创建流动记录"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO movements (person_id, person_name, avatar, from_region, to_region, movement_time, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            data.get('personId'),
            data.get('name', ''),
            data.get('avatar', ''),
            data.get('from'),
            data.get('to'),
            data.get('time'),
            data.get('status')
        ))
        self.connection.commit()
        cursor.execute('SELECT * FROM movements WHERE id = %s', (cursor.lastrowid,))
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else {}
    
    # ========== 地图数据相关操作 ==========
    
    def get_map_data(self) -> List[Dict]:
        """获取地图数据（各省份监测人数）"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT province_name, value FROM map_data ORDER BY value DESC')
        rows = cursor.fetchall()
        return [{'name': row['province_name'], 'value': row['value']} for row in rows]
    
    def update_map_data(self, province_name: str, value: int):
        """更新地图数据"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO map_data (province_name, value, updated_at)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE value = VALUES(value), updated_at = VALUES(updated_at)
        ''', (province_name, value, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.connection.commit()
        cursor.close()
    
    def batch_update_map_data(self, data: List[Dict]):
        """批量更新地图数据"""
        cursor = self.connection.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.executemany('''
            INSERT INTO map_data (province_name, value, updated_at)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE value = VALUES(value), updated_at = VALUES(updated_at)
        ''', [(item['name'], item['value'], now) for item in data])
        self.connection.commit()
        cursor.close()
    
    # ========== 趋势数据相关操作 ==========
    
    def get_trend_data(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """获取趋势数据"""
        cursor = self.connection.cursor()
        query = 'SELECT date, confirmed_count, suspected_count, recovered_count FROM trend_data'
        params = []
        
        if start_date or end_date:
            conditions = []
            if start_date:
                conditions.append('date >= %s')
                params.append(start_date)
            if end_date:
                conditions.append('date <= %s')
                params.append(end_date)
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY date ASC'
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [
            {
                'date': row['date'],
                'confirmedCount': row['confirmed_count'],
                'suspectedCount': row['suspected_count'],
                'recoveredCount': row['recovered_count']
            }
            for row in rows
        ]
    
    def create_trend_data(self, date: str, confirmed_count: int, suspected_count: int, recovered_count: int):
        """创建或更新趋势数据"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO trend_data (date, confirmed_count, suspected_count, recovered_count, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE confirmed_count = VALUES(confirmed_count), suspected_count = VALUES(suspected_count), recovered_count = VALUES(recovered_count)
        ''', (date, confirmed_count, suspected_count, recovered_count, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.connection.commit()
        cursor.close()
    
    def batch_create_trend_data(self, data: List[Dict]):
        """批量创建趋势数据"""
        cursor = self.connection.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.executemany('''
            INSERT INTO trend_data (date, confirmed_count, suspected_count, recovered_count, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE confirmed_count = VALUES(confirmed_count), suspected_count = VALUES(suspected_count), recovered_count = VALUES(recovered_count)
        ''', [
            (
                item['date'],
                item.get('confirmedCount', 0),
                item.get('suspectedCount', 0),
                item.get('recoveredCount', 0),
                now
            )
            for item in data
        ])
        self.connection.commit()
        cursor.close()
    
    # ========== 流动统计相关操作 ==========
    
    def get_flow_statistics(self, period: str = 'week') -> List[Dict]:
        """获取流动统计"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT region, flow_count FROM flow_statistics 
            WHERE period = %s 
            ORDER BY flow_count DESC
        ''', (period,))
        rows = cursor.fetchall()
        return [
            {
                'region': row['region'],
                'flowCount': row['flow_count']
            }
            for row in rows
        ]
    
    def create_flow_statistics(self, region: str, flow_count: int, period: str = 'week'):
        """创建或更新流动统计"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO flow_statistics (region, flow_count, period, updated_at)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE flow_count = VALUES(flow_count), updated_at = VALUES(updated_at)
        ''', (region, flow_count, period, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.connection.commit()
        cursor.close()
    
    def batch_create_flow_statistics(self, data: List[Dict], period: str = 'week'):
        """批量创建流动统计"""
        cursor = self.connection.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.executemany('''
            INSERT INTO flow_statistics (region, flow_count, period, updated_at)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE flow_count = VALUES(flow_count), updated_at = VALUES(updated_at)
        ''', [
            (
                item['region'],
                item.get('flowCount', 0),
                period,
                now
            )
            for item in data
        ])
        self.connection.commit()
        cursor.close()
    
    # ========== 重点人员相关操作 ==========
    
    def get_key_persons(self, category: str = None) -> List[Dict]:
        """获取重点人员列表，同时查找匹配的本地库人员"""
        cursor = self.connection.cursor()
        if category:
            cursor.execute('''
                SELECT kp.*, p.name, p.id_card, p.region, p.age, p.phone, p.status, 
                       p.avatar, p.gender, p.occupation, p.hometown
                FROM key_persons kp
                JOIN people p ON kp.person_id = p.id
                WHERE kp.category = %s
                ORDER BY kp.priority_level DESC, kp.added_at DESC
            ''', (category,))
        else:
            cursor.execute('''
                SELECT kp.*, p.name, p.id_card, p.region, p.age, p.phone, p.status, 
                       p.avatar, p.gender, p.occupation, p.hometown
                FROM key_persons kp
                JOIN people p ON kp.person_id = p.id
                ORDER BY kp.category, kp.priority_level DESC, kp.added_at DESC
            ''')
        rows = cursor.fetchall()
        result = []
        for row in rows:
            person_data = {
                'id': row['person_id'],
                'keyPersonId': row['id'],
                'name': row['name'],
                'idCard': row['id_card'],
                'region': row['region'],
                'age': row['age'],
                'phone': row['phone'],
                'status': row['status'],
                'avatar': row['avatar'],
                'gender': row['gender'],
                'occupation': row['occupation'],
                'hometown': row['hometown'],
                'category': row['category'],
                'priorityLevel': row['priority_level'],
                'reason': row['reason'],
                'addedAt': row['added_at'],
                'updatedAt': row['updated_at']
            }
            
            # 查找匹配的本地库人员（名字+手机号 或 名字+身份证号）
            matched_local_person = self._find_matched_local_person(
                person_data.get('name'),
                person_data.get('idCard'),
                person_data.get('phone')
            )
            if matched_local_person:
                person_data['hasLocalMatch'] = True
                person_data['localPerson'] = matched_local_person
                person_data['localPersonId'] = matched_local_person.get('id')
                print(f'[DEBUG] 重点人员匹配本地库成功: 重点人员 "{person_data.get("name")}" (ID: {person_data.get("id")}) 匹配到本地库人员 "{matched_local_person.get("name")}" (ID: {matched_local_person.get("id")})', flush=True)
            else:
                person_data['hasLocalMatch'] = False
                print(f'[DEBUG] 重点人员未匹配本地库: 重点人员 "{person_data.get("name")}" (ID: {person_data.get("id")}, 身份证: {person_data.get("idCard")}, 手机: {person_data.get("phone")}) 未找到匹配的本地库人员', flush=True)
            
            result.append(person_data)
        return result
    
    def _find_key_person_by_person_id(self, person_id: int) -> Optional[Dict]:
        """
        根据系统库人员ID查找重点人员信息
        
        Args:
            person_id: 系统库人员ID
            
        Returns:
            重点人员信息，如果没有则返回None
        """
        if not person_id:
            return None
        
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT kp.*, p.name, p.id_card, p.phone
            FROM key_persons kp
            JOIN people p ON kp.person_id = p.id
            WHERE kp.person_id = %s
            LIMIT 1
        ''', (person_id,))
        row = cursor.fetchone()
        if row:
            return {
                'keyPersonId': row['id'],
                'personId': row['person_id'],
                'category': row['category'],
                'priorityLevel': row['priority_level'],
                'reason': row['reason'],
                'addedAt': row['added_at'],
                'updatedAt': row['updated_at'],
                'name': row['name'],
                'idCard': row['id_card'],
                'phone': row['phone']
            }
        return None
    
    def get_key_person_categories(self) -> List[str]:
        """获取所有重点人员类别"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT DISTINCT category FROM key_persons ORDER BY category')
        rows = cursor.fetchall()
        return [row['category'] for row in rows]
    
    def add_key_person(self, person_id: int, category: str, priority_level: int = 1, reason: str = '') -> Dict:
        """添加重点人员"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO key_persons (person_id, category, priority_level, reason, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE priority_level = VALUES(priority_level), reason = VALUES(reason), updated_at = VALUES(updated_at)
        ''', (person_id, category, priority_level, reason, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.connection.commit()
        cursor.close()
        return self.get_key_persons(category)[0] if self.get_key_persons(category) else {}
    
    def remove_key_person(self, person_id: int, category: str) -> bool:
        """移除重点人员"""
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM key_persons WHERE person_id = %s AND category = %s', (person_id, category))
        self.connection.commit()
        return cursor.rowcount > 0
    
    def update_key_person(self, person_id: int, category: str, priority_level: int = None, reason: str = None) -> Dict:
        """更新重点人员信息"""
        cursor = self.connection.cursor()
        updates = []
        params = []
        
        if priority_level is not None:
            updates.append('priority_level = %s')
            params.append(priority_level)
        
        if reason is not None:
            updates.append('reason = %s')
            params.append(reason)
        
        if updates:
            updates.append('updated_at = %s')
            params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            params.extend([person_id, category])
            
            cursor.execute(f'''
                UPDATE key_persons 
                SET {', '.join(updates)}
                WHERE person_id = %s AND category = %s
            ''', params)
            self.connection.commit()
        
        result = self.get_key_persons(category)
        for item in result:
            if item['id'] == person_id:
                return item
        return {}
    
    # ========== 统计相关操作 ==========
    
    def get_stats(self) -> Dict:
        """获取统计数据"""
        cursor = self.connection.cursor()
        
        # 总人数
        cursor.execute('SELECT COUNT(*) as count FROM people')
        total_people = cursor.fetchone()['count']
        
        # 确诊人数
        cursor.execute('SELECT COUNT(*) as count FROM people WHERE status = %s', ('确诊',))
        confirmed_cases = cursor.fetchone()['count']
        
        # 活跃区域数
        cursor.execute('SELECT COUNT(DISTINCT region) as count FROM people')
        active_regions = cursor.fetchone()['count']
        
        # 今日流动记录数
        today = datetime.now().strftime('%Y-%m-%d')
        today_start = today + ' 00:00:00'
        today_end = today + ' 23:59:59'
        cursor.execute('SELECT COUNT(*) as count FROM movements WHERE movement_time >= %s AND movement_time <= %s', (today_start, today_end))
        today_movements = cursor.fetchone()['count']
        
        return {
            'totalPeople': total_people,
            'confirmedCases': confirmed_cases,
            'activeRegions': active_regions,
            'todayMovements': today_movements
        }
    
    def get_province_confirmed_ranking(self) -> List[Dict]:
        """获取各省确诊人数排名（新增、驻留、总计）"""
        cursor = self.connection.cursor()
        
        # 获取所有确诊人员
        cursor.execute('''
            SELECT id, hometown, region, last_update, status
            FROM people
            WHERE status = %s
        ''', ('确诊',))
        
        confirmed_people = cursor.fetchall()
        
        # 计算最近7天的时间范围
        from datetime import datetime, timedelta
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        
        # 统计各省数据
        province_stats = {}
        
        for row in confirmed_people:
            person = self._row_to_dict(row)
            # 获取省份（优先使用hometown，否则使用region转换）
            hometown = person.get('hometown', '')
            region = person.get('region', '')
            
            if hometown:
                province = hometown
            elif region:
                from map_sync import get_province_from_region
                province = get_province_from_region(region)
            else:
                continue
            
            if province == '未知省份':
                continue
            
            # 初始化省份统计
            if province not in province_stats:
                province_stats[province] = {
                    'province': province,
                    'total': 0,
                    'new': 0,
                    'resident': 0
                }
            
            # 总计+1
            province_stats[province]['total'] += 1
            
            # 判断是否为新增（最近7天内更新）
            last_update = person.get('lastUpdate', '')
            if last_update and last_update >= seven_days_ago:
                province_stats[province]['new'] += 1
            
            # 驻留人数 = 总计（因为都是当前确诊人员）
            province_stats[province]['resident'] = province_stats[province]['total']
        
        # 转换为列表并按总计排序
        ranking = list(province_stats.values())
        ranking.sort(key=lambda x: x['total'], reverse=True)
        
        return ranking
    
    # ========== 辅助方法 ==========
    
    def _row_to_dict(self, row) -> Dict:
        """将数据库行转换为字典"""
        if not row:
            return {}
        
        # pymysql 使用 DictCursor，row 已经是字典
        if isinstance(row, dict):
            result = row.copy()
        else:
            result = {}
            for key in row.keys():
                result[key] = row[key]
        
        # 创建新的结果字典用于字段名转换
        converted_result = {}
        for key, value in result.items():
            # 转换字段名（下划线转驼峰）
            if key == 'id_card':
                converted_result['idCard'] = value
            elif key == 'last_update':
                converted_result['lastUpdate'] = value
            elif key == 'created_at':
                converted_result['createdAt'] = value
            elif key == 'person_id':
                converted_result['personId'] = value
            elif key == 'person_name':
                converted_result['name'] = value
            elif key == 'from_region':
                converted_result['from'] = value
            elif key == 'to_region':
                converted_result['to'] = value
            elif key == 'movement_time':
                converted_result['time'] = value
            elif key == 'education_history':
                # 解析JSON字符串
                try:
                    converted_result['educationHistory'] = json.loads(value) if value else []
                except (json.JSONDecodeError, TypeError):
                    converted_result['educationHistory'] = []
            elif key == 'work_history':
                try:
                    converted_result['workHistory'] = json.loads(value) if value else []
                except (json.JSONDecodeError, TypeError):
                    converted_result['workHistory'] = []
            elif key == 'social_media':
                try:
                    converted_result['socialMedia'] = json.loads(value) if value else []
                except (json.JSONDecodeError, TypeError):
                    converted_result['socialMedia'] = []
            elif key == 'visit_records':
                try:
                    converted_result['visitRecords'] = json.loads(value) if value else []
                except (json.JSONDecodeError, TypeError):
                    converted_result['visitRecords'] = []
            elif key == 'flight_records':
                try:
                    converted_result['flightRecords'] = json.loads(value) if value else []
                except (json.JSONDecodeError, TypeError):
                    converted_result['flightRecords'] = []
            elif key == 'train_records':
                try:
                    converted_result['trainRecords'] = json.loads(value) if value else []
                except (json.JSONDecodeError, TypeError):
                    converted_result['trainRecords'] = []
            elif key == 'tags':
                try:
                    converted_result['tags'] = json.loads(value) if value else []
                except (json.JSONDecodeError, TypeError):
                    converted_result['tags'] = []
            elif key == 'hometown':
                converted_result['hometown'] = value
            elif key == 'nationality':
                converted_result['nationality'] = value
            elif key == 'visa_type':
                converted_result['visaType'] = value
            elif key == 'institution':
                converted_result['institution'] = value
            else:
                converted_result[key] = value
        return converted_result
    
    def clear_all_data(self):
        """清空所有数据（用于重新初始化）"""
        cursor = self.connection.cursor()
        try:
            cursor.execute('DELETE FROM movements')
            cursor.execute('DELETE FROM people')
            cursor.execute('DELETE FROM map_data')
            self.connection.commit()
        finally:
            cursor.close()
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()
