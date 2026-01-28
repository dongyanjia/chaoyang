"""
标签服务模块
处理标签的提取、存储、查询和筛选
"""
import json
import pymysql
from typing import List, Dict, Optional
from datetime import datetime


class TagService:
    """标签服务类"""
    
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        if not self.db_connection:
            return
        
        try:
            # 如果传入的是 Database 对象，获取其 connection
            if hasattr(self.db_connection, 'connection'):
                conn = self.db_connection.connection
            else:
                conn = self.db_connection
            
            if not conn:
                return
            
            cursor = conn.cursor()
            
            # tags 表（Doris 语法，UNIQUE KEY 列必须在前面）
            # 先检查表是否存在，如果存在则尝试添加新字段
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    category_name VARCHAR(100) NOT NULL,
                    sub_category_name VARCHAR(100) NOT NULL,
                    tag_name VARCHAR(200) NOT NULL,
                    id BIGINT NOT NULL AUTO_INCREMENT,
                    category_order INT DEFAULT 0,
                    sub_category_order INT DEFAULT 0,
                    tag_order INT DEFAULT 0,
                    category_id INT,
                    sub_category_id INT,
                    tag_id INT,
                    created_at VARCHAR(50),
                    updated_at VARCHAR(50),
                    is_active TINYINT DEFAULT 1
                )
                UNIQUE KEY(category_name, sub_category_name, tag_name)
                DISTRIBUTED BY HASH(category_name) BUCKETS 10
                PROPERTIES (
                    "replication_num" = "1"
                )
            ''')
            
            # 尝试添加新字段（如果表已存在但字段不存在）
            try:
                cursor.execute('ALTER TABLE tags ADD COLUMN category_id INT')
            except:
                pass  # 字段已存在，忽略
            
            try:
                cursor.execute('ALTER TABLE tags ADD COLUMN sub_category_id INT')
            except:
                pass
            
            try:
                cursor.execute('ALTER TABLE tags ADD COLUMN tag_id INT')
            except:
                pass
            
            try:
                cursor.execute('ALTER TABLE tags ADD COLUMN is_active TINYINT DEFAULT 1')
            except:
                pass
            
            # person_tags 表（Doris 语法，UNIQUE KEY 列必须在前面）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS person_tags (
                    person_id BIGINT NOT NULL,
                    tag_id BIGINT NOT NULL,
                    tag_value VARCHAR(500),
                    id BIGINT NOT NULL AUTO_INCREMENT,
                    created_at VARCHAR(50)
                )
                UNIQUE KEY(person_id, tag_id, tag_value)
                DISTRIBUTED BY HASH(person_id) BUCKETS 10
                PROPERTIES (
                    "replication_num" = "1"
                )
            ''')
            
            if hasattr(self.db_connection, 'connection'):
                self.db_connection.connection.commit()
            else:
                self.db_connection.commit()
            print('[OK] 标签表初始化成功')
        except Exception as e:
            print(f'[ERROR] 标签表初始化失败: {e}')
            import traceback
            traceback.print_exc()
    
    def extract_and_save_tags(self, categories: List[Dict], clear_existing: bool = False) -> int:
        """从标签结构提取并保存所有标签到数据库
        
        Args:
            categories: 标签分类列表，格式为 [{'name': '分类名', 'children': [{'name': '子分类名', 'tags': ['标签1', '标签2']}]}]
            clear_existing: 是否先清空现有标签（标记为禁用）
        
        Returns:
            保存的标签数量
        """
        if not self.db_connection:
            return 0
        
        try:
            # 如果传入的是 Database 对象，获取其 connection
            if hasattr(self.db_connection, 'connection'):
                conn = self.db_connection.connection
            else:
                conn = self.db_connection
            
            if not conn:
                return 0
            
            cursor = conn.cursor()
            saved_count = 0
            now = datetime.now().isoformat()
            
            # 如果需要清空现有标签，先标记为禁用
            if clear_existing:
                try:
                    cursor.execute('''
                        UPDATE tags SET is_active = 0, updated_at = %s
                        WHERE is_active = 1
                    ''', (now,))
                    print(f'[INFO] 已标记 {cursor.rowcount} 个旧标签为禁用')
                except Exception as e:
                    print(f'[WARN] 清空旧标签失败: {e}')
            
            # 批量收集所有标签数据
            all_tag_data = []
            for cat_idx, category in enumerate(categories):
                category_name = category.get('name', '')
                category_id = category.get('id', cat_idx + 1)
                children = category.get('children', [])
                
                for sub_idx, sub_category in enumerate(children):
                    sub_category_name = sub_category.get('name', '')
                    sub_category_id = sub_category.get('id', sub_idx + 1)
                    tags = sub_category.get('tags', [])
                    
                    for tag_idx, tag_name in enumerate(tags):
                        if not tag_name:
                            continue
                        all_tag_data.append((
                            category_name,
                            sub_category_name,
                            tag_name,
                            cat_idx,
                            sub_idx,
                            tag_idx,
                            category_id,
                            sub_category_id,
                            tag_idx + 1,
                            now,
                            now,
                            1  # is_active
                        ))
            
            # 批量插入或更新（每次100条）
            batch_size = 100
            for i in range(0, len(all_tag_data), batch_size):
                batch = all_tag_data[i:i+batch_size]
                for item in batch:
                    try:
                        # 先尝试更新已存在的标签
                        cursor.execute('''
                            UPDATE tags 
                            SET category_order = %s, sub_category_order = %s, tag_order = %s,
                                category_id = %s, sub_category_id = %s, tag_id = %s,
                                updated_at = %s, is_active = 1
                            WHERE category_name = %s AND sub_category_name = %s AND tag_name = %s
                        ''', (item[3], item[4], item[5], item[6], item[7], item[8], item[10], 
                              item[0], item[1], item[2]))
                        
                        if cursor.rowcount == 0:
                            # 如果更新失败，则插入新记录
                            cursor.execute('''
                                INSERT INTO tags 
                                (category_name, sub_category_name, tag_name, 
                                 category_order, sub_category_order, tag_order,
                                 category_id, sub_category_id, tag_id,
                                 created_at, updated_at, is_active)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ''', item)
                        saved_count += 1
                    except Exception as e:
                        print(f'[WARN] 保存标签失败: {item[0]}/{item[1]}/{item[2]}, {e}')
            
            if hasattr(self.db_connection, 'connection'):
                self.db_connection.connection.commit()
            else:
                self.db_connection.commit()
            print(f'[OK] 已保存 {saved_count} 个标签到数据库')
            return saved_count
        except Exception as e:
            print(f'[ERROR] 提取标签失败: {e}')
            import traceback
            traceback.print_exc()
            if self.db_connection:
                if hasattr(self.db_connection, 'connection'):
                    self.db_connection.connection.rollback()
                elif hasattr(self.db_connection, 'rollback'):
                    self.db_connection.rollback()
            return 0
    
    def get_all_tags(self, include_inactive: bool = False) -> List[Dict]:
        """获取所有标签，按层级结构组织
        
        Args:
            include_inactive: 是否包含禁用的标签
        
        Returns:
            标签分类列表，格式为 [{'name': '分类名', 'id': 1, 'children': [{'name': '子分类名', 'id': 1, 'tags': ['标签1', '标签2']}]}]
        """
        if not self.db_connection:
            return []
        
        try:
            # 如果传入的是 Database 对象，获取其 connection
            if hasattr(self.db_connection, 'connection'):
                conn = self.db_connection.connection
            else:
                conn = self.db_connection
            
            if not conn:
                return []
            
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            # 构建查询条件
            where_clause = 'WHERE is_active = 1' if not include_inactive else ''
            
            # 检查表是否存在，如果不存在则返回空列表
            try:
                cursor.execute(f'''
                    SELECT category_name, sub_category_name, tag_name,
                           category_order, sub_category_order, tag_order,
                           category_id, sub_category_id, tag_id
                    FROM tags
                    {where_clause}
                    ORDER BY category_order, sub_category_order, tag_order
                ''')
                rows = cursor.fetchall()
            except pymysql.err.ProgrammingError as e:
                # 表不存在或其他SQL错误
                if 'doesn\'t exist' in str(e) or 'does not exist' in str(e):
                    print(f'[WARN] tags表不存在，返回空列表: {e}')
                    return []
                else:
                    raise  # 重新抛出其他SQL错误
            
            # 组织成层级结构
            categories = {}
            for row in rows:
                cat_name = row['category_name']
                sub_name = row['sub_category_name']
                tag_name = row['tag_name']
                cat_id = row.get('category_id') or row['category_order'] + 1
                sub_id = row.get('sub_category_id') or row['sub_category_order'] + 1
                
                if cat_name not in categories:
                    categories[cat_name] = {
                        'name': cat_name,
                        'id': cat_id,
                        'order': row['category_order'],
                        'children': {}
                    }
                
                if sub_name not in categories[cat_name]['children']:
                    categories[cat_name]['children'][sub_name] = {
                        'name': sub_name,
                        'id': sub_id,
                        'order': row['sub_category_order'],
                        'tags': []
                    }
                
                categories[cat_name]['children'][sub_name]['tags'].append(tag_name)
            
            # 转换为列表格式
            result = []
            for cat_name, cat_data in sorted(categories.items(), key=lambda x: x[1]['order']):
                children = []
                for sub_name, sub_data in sorted(cat_data['children'].items(), key=lambda x: x[1]['order']):
                    children.append({
                        'name': sub_name,
                        'id': sub_data['id'],
                        'tags': sub_data['tags']
                    })
                result.append({
                    'name': cat_name,
                    'id': cat_data['id'],
                    'children': children
                })
            
            return result
        except Exception as e:
            print(f'[ERROR] 获取标签列表失败: {e}')
            import traceback
            traceback.print_exc()
            return []
    
    def save_tags_from_frontend(self, categories: List[Dict]) -> Dict:
        """从前端保存标签到数据库
        
        Args:
            categories: 前端标签结构，格式为 [{'name': '分类名', 'id': 1, 'children': [{'name': '子分类名', 'id': 1, 'tags': ['标签1']}]}]
        
        Returns:
            {'success': bool, 'message': str, 'count': int}
        """
        try:
            count = self.extract_and_save_tags(categories, clear_existing=True)
            return {
                'success': True,
                'message': f'成功保存 {count} 个标签到数据库',
                'count': count
            }
        except Exception as e:
            print(f'[ERROR] 保存标签失败: {e}')
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'保存标签失败: {str(e)}',
                'count': 0
            }
    
    def get_tag_counts(self, area: str = None) -> Dict[str, int]:
        """获取每个标签对应的人员数量"""
        if not self.db_connection:
            return {}
        
        try:
            # 如果传入的是 Database 对象，获取其 connection
            if hasattr(self.db_connection, 'connection'):
                conn = self.db_connection.connection
            else:
                conn = self.db_connection
            
            if not conn:
                return {}
            
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            # 构建查询，统计每个标签的人员数量
            # 需要根据标签类型从不同字段查询
            counts = {}
            
            # 基本信息类标签（从 people 表直接查询）
            basic_tags_query = '''
                SELECT 
                    CONCAT("基本信息", "|", "年龄", "|", 
                        CASE 
                            WHEN age >= 18 AND age <= 25 THEN "18-25岁"
                            WHEN age >= 26 AND age <= 35 THEN "26-35岁"
                            WHEN age >= 36 AND age <= 45 THEN "36-45岁"
                            WHEN age >= 46 AND age <= 55 THEN "46-55岁"
                            WHEN age >= 56 AND age <= 65 THEN "56-65岁"
                            WHEN age > 65 THEN "65岁以上"
                            ELSE NULL
                        END) as tag_key,
                    COUNT(*) as count
                FROM people
                WHERE age >= 18
                GROUP BY tag_key
                HAVING tag_key IS NOT NULL
            '''
            cursor.execute(basic_tags_query)
            for row in cursor.fetchall():
                if row['tag_key']:
                    counts[row['tag_key']] = row['count']
            
            # 性别标签
            cursor.execute('''
                SELECT 
                    CONCAT("基本信息", "|", "性别", "|", gender) as tag_key,
                    COUNT(*) as count
                FROM people
                WHERE gender IS NOT NULL AND gender != ''
                GROUP BY gender
            ''')
            for row in cursor.fetchall():
                if row['tag_key']:
                    counts[row['tag_key']] = row['count']
            
            # 职业标签
            cursor.execute('''
                SELECT 
                    CONCAT("基本信息", "|", "职业", "|", occupation) as tag_key,
                    COUNT(*) as count
                FROM people
                WHERE occupation IS NOT NULL AND occupation != ''
                GROUP BY occupation
            ''')
            for row in cursor.fetchall():
                if row['tag_key']:
                    counts[row['tag_key']] = row['count']
            
            # 籍贯标签
            cursor.execute('''
                SELECT 
                    CONCAT("基本信息", "|", "籍贯", "|", hometown) as tag_key,
                    COUNT(*) as count
                FROM people
                WHERE hometown IS NOT NULL AND hometown != ''
                GROUP BY hometown
            ''')
            for row in cursor.fetchall():
                if row['tag_key']:
                    counts[row['tag_key']] = row['count']
            
            # 状态标签
            cursor.execute('''
                SELECT 
                    CONCAT("基本信息", "|", "状态", "|", status) as tag_key,
                    COUNT(*) as count
                FROM people
                WHERE status IS NOT NULL AND status != ''
                GROUP BY status
            ''')
            for row in cursor.fetchall():
                if row['tag_key']:
                    counts[row['tag_key']] = row['count']
            
            # 签证类型标签
            cursor.execute('''
                SELECT 
                    CONCAT("基本信息", "|", "签证类型", "|", visa_type) as tag_key,
                    COUNT(*) as count
                FROM people
                WHERE visa_type IS NOT NULL AND visa_type != ''
                GROUP BY visa_type
            ''')
            for row in cursor.fetchall():
                if row['tag_key']:
                    counts[row['tag_key']] = row['count']
            
            # 机构标签
            cursor.execute('''
                SELECT 
                    CONCAT("基本信息", "|", "机构", "|", institution) as tag_key,
                    COUNT(*) as count
                FROM people
                WHERE institution IS NOT NULL AND institution != ''
                GROUP BY institution
            ''')
            for row in cursor.fetchall():
                if row['tag_key']:
                    counts[row['tag_key']] = row['count']
            
            # TODO: 到访信息、航班、铁路等需要从 JSON 字段解析
            # 这里先返回基本信息的统计
            
            return counts
        except Exception as e:
            print(f'[ERROR] 获取标签计数失败: {e}')
            import traceback
            traceback.print_exc()
            return {}
    
    def filter_people_by_tags(self, tags: List[Dict], search_query: str = None, 
                              page: int = 1, page_size: int = 30) -> Dict:
        """根据标签筛选人员"""
        if not self.db_connection:
            return {'data': [], 'total': 0, 'page': page, 'page_size': page_size}
        
        try:
            # 如果传入的是 Database 对象，获取其 connection
            if hasattr(self.db_connection, 'connection'):
                conn = self.db_connection.connection
            else:
                conn = self.db_connection
            
            if not conn:
                return {'data': [], 'total': 0, 'page': page, 'page_size': page_size}
            
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            # 构建 WHERE 条件
            conditions = []
            params = []
            
            # 搜索条件
            if search_query:
                conditions.append('(name LIKE %s OR id_card LIKE %s)')
                search_param = f'%{search_query}%'
                params.extend([search_param, search_param])
            
            # 标签筛选条件
            # 同一类型（同一subCategory）取并集（OR），不同类型取交集（AND）
            if tags:
                # 按 category 和 sub_category 分组
                tag_groups = {}
                for tag in tags:
                    cat_name = tag.get('categoryName', '')
                    sub_name = tag.get('subCategoryName', '')
                    tag_name = tag.get('tagName', '')
                    
                    if not cat_name or not sub_name or not tag_name:
                        continue
                    
                    key = f"{cat_name}|{sub_name}"
                    if key not in tag_groups:
                        tag_groups[key] = []
                    tag_groups[key].append((cat_name, sub_name, tag_name))
                
                # 为每个组构建条件
                group_conditions = []
                for group_key, group_tags in tag_groups.items():
                    group_ors = []
                    for cat_name, sub_name, tag_name in group_tags:
                        # 根据标签类型构建条件
                        condition = self._build_tag_condition(cat_name, sub_name, tag_name, params)
                        if condition:
                            group_ors.append(condition)
                    
                    if group_ors:
                        group_conditions.append(f"({' OR '.join(group_ors)})")
                
                if group_conditions:
                    conditions.append(' AND '.join(group_conditions))
            
            # 构建完整查询
            where_clause = ' AND '.join(conditions) if conditions else '1=1'
            
            # 获取总数
            count_query = f'SELECT COUNT(*) as total FROM people WHERE {where_clause}'
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']
            
            # 获取分页数据
            offset = (page - 1) * page_size
            data_query = f'''
                SELECT * FROM people 
                WHERE {where_clause}
                ORDER BY id DESC
                LIMIT %s OFFSET %s
            '''
            params.extend([page_size, offset])
            cursor.execute(data_query, params)
            rows = cursor.fetchall()
            
            # 处理 JSON 字段
            people = []
            for row in rows:
                person = dict(row)
                for json_field in ['tags', 'education_history', 'work_history', 'social_media', 
                                 'visit_records', 'flight_records', 'train_records']:
                    if person.get(json_field):
                        try:
                            person[json_field] = json.loads(person[json_field])
                        except:
                            person[json_field] = []
                people.append(person)
            
            return {
                'data': people,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
        except Exception as e:
            print(f'[ERROR] 标签筛选失败: {e}')
            import traceback
            traceback.print_exc()
            return {'data': [], 'total': 0, 'page': page, 'page_size': page_size}
    
    def _build_tag_condition(self, category_name: str, sub_category_name: str, 
                             tag_name: str, params: List) -> Optional[str]:
        """构建单个标签的 SQL 条件"""
        if category_name == '基本信息':
            if sub_category_name == '年龄':
                # 年龄范围
                if tag_name == '18-25岁':
                    return 'age >= 18 AND age <= 25'
                elif tag_name == '26-35岁':
                    return 'age >= 26 AND age <= 35'
                elif tag_name == '36-45岁':
                    return 'age >= 36 AND age <= 45'
                elif tag_name == '46-55岁':
                    return 'age >= 46 AND age <= 55'
                elif tag_name == '56-65岁':
                    return 'age >= 56 AND age <= 65'
                elif tag_name == '65岁以上':
                    return 'age > 65'
            elif sub_category_name == '性别':
                params.append(tag_name)
                return 'gender = %s'
            elif sub_category_name == '职业':
                params.append(tag_name)
                return 'occupation = %s'
            elif sub_category_name == '籍贯':
                params.append(tag_name)
                return 'hometown = %s'
            elif sub_category_name == '状态':
                params.append(tag_name)
                return 'status = %s'
            elif sub_category_name == '签证类型':
                params.append(tag_name)
                return 'visa_type = %s'
            elif sub_category_name == '机构':
                params.append(tag_name)
                return 'institution = %s'
        
        elif category_name == '到访信息':
            if sub_category_name == '到访省份':
                # 需要从 visit_records JSON 字段中查询
                params.append(f'%"province":"{tag_name}"%')
                return 'visit_records LIKE %s'
        
        elif category_name == '民航铁路动态':
            if sub_category_name == '航班':
                params.append(f'%"airline":"{tag_name}"%')
                return 'flight_records LIKE %s'
            elif sub_category_name == '铁路':
                params.append(f'%"type":"{tag_name}"%')
                return 'train_records LIKE %s'
        
        elif category_name == '社交媒体动态':
            if sub_category_name == '平台类型':
                params.append(f'%"platform":"{tag_name}"%')
                return 'social_media LIKE %s'
        
        return None


# 全局标签服务实例
_tag_service = None

def get_tag_service(db_connection=None):
    """获取标签服务实例"""
    global _tag_service
    if _tag_service is None:
        _tag_service = TagService(db_connection)
    return _tag_service
