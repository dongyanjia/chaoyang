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
DB_CONFIG = {
    'host': os.getenv('DORIS_HOST', 'localhost'),
    'port': int(os.getenv('DORIS_PORT', 9030)),
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
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
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
        
        # 人员表 - 使用 Doris 的数据类型
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS people (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                id_card VARCHAR(50) NOT NULL,
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
                institution VARCHAR(200),
                UNIQUE KEY uk_id_card (id_card)
            ) ENGINE=OLAP
            DUPLICATE KEY(id)
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
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                person_id BIGINT NOT NULL,
                category VARCHAR(50) NOT NULL,
                priority_level INT DEFAULT 1,
                reason TEXT,
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uk_person_category (person_id, category)
            ) ENGINE=OLAP
            DUPLICATE KEY(id)
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
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
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
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                province_name VARCHAR(100) NOT NULL,
                value INT NOT NULL DEFAULT 0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uk_province (province_name)
            ) ENGINE=OLAP
            DUPLICATE KEY(id)
            DISTRIBUTED BY HASH(id) BUCKETS 10
            PROPERTIES (
                "replication_num" = "1",
                "storage_format" = "V2"
            )
        ''')
        
        # 趋势数据表（存储每日的趋势数据）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trend_data (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                date DATE NOT NULL,
                confirmed_count INT NOT NULL DEFAULT 0,
                suspected_count INT NOT NULL DEFAULT 0,
                recovered_count INT NOT NULL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uk_date (date)
            ) ENGINE=OLAP
            DUPLICATE KEY(id)
            DISTRIBUTED BY HASH(id) BUCKETS 10
            PROPERTIES (
                "replication_num" = "1",
                "storage_format" = "V2"
            )
        ''')
        
        # 流动统计表（存储各地区的流动数量）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flow_statistics (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                region VARCHAR(100) NOT NULL,
                flow_count INT NOT NULL DEFAULT 0,
                period VARCHAR(20) NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uk_region_period (region, period)
            ) ENGINE=OLAP
            DUPLICATE KEY(id)
            DISTRIBUTED BY HASH(id) BUCKETS 10
            PROPERTIES (
                "replication_num" = "1",
                "storage_format" = "V2"
            )
        ''')
        
        # 本地人员表（用户导入的数据）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS local_people (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
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
                data.get('region', ''),
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
        cursor = self.connection.cursor()
        try:
            for i, person in enumerate(people_list):
                try:
                    if not person.get('name') or not person.get('idCard'):
                        errors.append(f'第{i+1}条数据缺少必要字段：name或idCard')
                        continue
                    
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
                for error in errors[:5]:
                    print(f'  - {error}')
            
            return count
        finally:
            cursor.close()
    
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
        
        # 转换字段名（下划线转驼峰）
        field_mapping = {
            'id_card': 'idCard',
            'last_update': 'lastUpdate',
            'created_at': 'createdAt',
            'person_id': 'personId',
            'person_name': 'name',
            'from_region': 'from',
            'to_region': 'to',
            'movement_time': 'time',
            'education_history': 'educationHistory',
            'work_history': 'workHistory',
            'social_media': 'socialMedia',
            'visit_records': 'visitRecords',
            'flight_records': 'flightRecords',
            'train_records': 'trainRecords',
            'visa_type': 'visaType'
        }
        
        for old_key, new_key in field_mapping.items():
            if old_key in result:
                result[new_key] = result.pop(old_key)
        
        # 解析JSON字段
        json_fields = ['tags', 'educationHistory', 'workHistory', 'socialMedia', 
                       'visitRecords', 'flightRecords', 'trainRecords']
        for field in json_fields:
            if field in result and isinstance(result[field], str):
                try:
                    result[field] = json.loads(result[field]) if result[field] else []
                except (json.JSONDecodeError, TypeError):
                    result[field] = []
        
        return result
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()
