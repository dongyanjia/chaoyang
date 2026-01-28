"""
测试标签 API，检查标签数据是否能正确查询
"""
import os
import sys
import pymysql
from database import Database
from tag_service import TagService

# Doris 数据库连接配置
DORIS_HOST = os.getenv('DORIS_HOST', 'localhost')
DORIS_PORT = int(os.getenv('DORIS_PORT', 9030))
DORIS_USER = os.getenv('DORIS_USER', 'root')
DORIS_PASSWORD = os.getenv('DORIS_PASSWORD', '')
DORIS_DATABASE = os.getenv('DORIS_DATABASE', 'flu_monitoring')

def test_tags_query():
    """测试标签查询"""
    print('=' * 50)
    print('测试标签查询')
    print('=' * 50)
    
    # 连接数据库
    db = Database()
    try:
        db.connect()
        print('[OK] 数据库连接成功')
        
        # 检查 tags 表是否存在
        cursor = db.connection.cursor()
        try:
            cursor.execute('SELECT COUNT(*) as count FROM tags')
            count = cursor.fetchone()['count']
            print(f'[OK] tags 表存在，共有 {count} 条记录')
        except Exception as e:
            print(f'[ERROR] tags 表查询失败: {e}')
            return
        
        # 查询所有标签（包括禁用的）
        cursor.execute('''
            SELECT category_name, sub_category_name, tag_name, is_active
            FROM tags
            ORDER BY category_name, sub_category_name, tag_name
            LIMIT 20
        ''')
        rows = cursor.fetchall()
        print(f'\n[INFO] 查询到 {len(rows)} 条标签记录（前20条）:')
        for row in rows:
            active_status = '启用' if row.get('is_active', 1) == 1 else '禁用'
            print(f'  - {row["category_name"]} > {row["sub_category_name"]} > {row["tag_name"]} [{active_status}]')
        
        # 查询启用的标签
        cursor.execute('''
            SELECT COUNT(*) as count FROM tags WHERE is_active = 1
        ''')
        active_count = cursor.fetchone()['count']
        print(f'\n[INFO] 启用的标签数量: {active_count}')
        
        # 查询禁用的标签
        cursor.execute('''
            SELECT COUNT(*) as count FROM tags WHERE is_active = 0 OR is_active IS NULL
        ''')
        inactive_count = cursor.fetchone()['count']
        print(f'[INFO] 禁用的标签数量: {inactive_count}')
        
        # 测试 TagService
        print('\n' + '=' * 50)
        print('测试 TagService.get_all_tags()')
        print('=' * 50)
        
        tag_service = TagService(db)
        tags = tag_service.get_all_tags(include_inactive=False)
        
        print(f'[INFO] TagService 返回 {len(tags)} 个分类')
        for category in tags:
            print(f'\n分类: {category["name"]} (ID: {category.get("id", "N/A")})')
            if 'children' in category:
                for child in category['children']:
                    tag_count = len(child.get('tags', []))
                    print(f'  子分类: {child["name"]} (ID: {child.get("id", "N/A")}) - {tag_count} 个标签')
                    if tag_count > 0:
                        print(f'    标签: {", ".join(child["tags"][:5])}{"..." if tag_count > 5 else ""}')
        
        if len(tags) == 0:
            print('\n[WARN] TagService 返回空列表！')
            print('[建议] 检查 tags 表中的 is_active 字段值')
            print('[建议] 可能需要运行 init_tags.py 初始化标签数据')
        
    except Exception as e:
        print(f'[ERROR] 测试失败: {e}')
        import traceback
        traceback.print_exc()
    finally:
        db.disconnect()

if __name__ == '__main__':
    test_tags_query()
