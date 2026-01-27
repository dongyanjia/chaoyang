"""
检查数据库数据脚本
用于检查数据库中的人员数据和日期字段

使用方法：
    python check_data.py
"""
from database import Database
from datetime import datetime, timedelta

def check_data():
    """检查数据库中的数据"""
    db = Database()
    db.connect()
    
    try:
        # 获取所有人员数据
        people = db.get_people()
        print(f'总数据量: {len(people)}')
        
        if len(people) == 0:
            print('⚠️ 数据库中没有数据！')
            return
        
        # 检查前5条数据的字段
        print('\n前5条数据的字段信息:')
        for i, person in enumerate(people[:5]):
            print(f'\n人员{i+1}:')
            print(f'  ID: {person.get("id")}')
            print(f'  姓名: {person.get("name")}')
            print(f'  地区: {person.get("region")}')
            print(f'  createdAt: {person.get("createdAt")}')
            print(f'  created_at: {person.get("created_at")}')
            print(f'  lastUpdate: {person.get("lastUpdate")}')
            print(f'  last_update: {person.get("last_update")}')
        
        # 计算今天的日期
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        today_str = today.strftime('%Y-%m-%d')
        
        print(f'\n日期信息:')
        print(f'  今天: {today_str}')
        print(f'  昨天: {yesterday_str}')
        
        # 统计昨天创建的数据
        yesterday_count = 0
        today_count = 0
        no_date_count = 0
        
        print(f'\n统计信息:')
        for person in people:
            created_date = person.get('createdAt') or person.get('created_at')
            if created_date:
                try:
                    # 提取日期部分
                    if isinstance(created_date, str):
                        date_str = created_date.split(' ')[0]
                    else:
                        d = datetime.fromisoformat(str(created_date))
                        date_str = d.strftime('%Y-%m-%d')
                    
                    if date_str == yesterday_str:
                        yesterday_count += 1
                    elif date_str == today_str:
                        today_count += 1
                except Exception as e:
                    print(f'日期解析错误: {created_date}, 错误: {e}')
                    no_date_count += 1
            else:
                no_date_count += 1
        
        print(f'  昨天创建的数据: {yesterday_count} 条')
        print(f'  今天创建的数据: {today_count} 条')
        print(f'  没有日期字段的数据: {no_date_count} 条')
        
        # 按地区统计昨天新增的数据
        print(f'\n各地区昨天新增统计:')
        region_counts = {}
        for person in people:
            created_date = person.get('createdAt') or person.get('created_at')
            if created_date:
                try:
                    if isinstance(created_date, str):
                        date_str = created_date.split(' ')[0]
                    else:
                        d = datetime.fromisoformat(str(created_date))
                        date_str = d.strftime('%Y-%m-%d')
                    
                    if date_str == yesterday_str:
                        region = person.get('region') or '未知'
                        region_counts[region] = region_counts.get(region, 0) + 1
                except:
                    pass
        
        if region_counts:
            for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
                print(f'  {region}: {count} 条')
        else:
            print('  无数据')
        
    except Exception as e:
        print(f'❌ 检查失败: {e}')
        import traceback
        traceback.print_exc()
    finally:
        db.disconnect()

if __name__ == '__main__':
    check_data()
