"""
测试地图数据同步
验证3000人的数据是否正确同步到地图
"""
from database import Database
from map_sync import sync_map_data_from_people

def test_map_sync():
    """测试地图数据同步"""
    print('=' * 50)
    print('测试地图数据同步')
    print('=' * 50)
    
    db = Database()
    db.connect()
    
    try:
        # 获取人员数据
        people = db.get_people()
        print(f'人员总数: {len(people)}')
        
        # 统计各省份的人员数量
        from map_sync import PROVINCES
        province_counts = {}
        for person in people:
            hometown = person.get('hometown', '')
            if hometown:
                province = hometown
            else:
                region = person.get('region', '')
                from map_sync import get_province_from_region
                province = get_province_from_region(region)
            
            if province and province != '未知省份':
                province_counts[province] = province_counts.get(province, 0) + 1
        
        print(f'\n各省份人员分布（前10个）:')
        sorted_provinces = sorted(province_counts.items(), key=lambda x: x[1], reverse=True)
        for province, count in sorted_provinces[:10]:
            print(f'  {province}: {count}人')
        
        print(f'\n有人员的省份数: {len(province_counts)}')
        print(f'总省份数: {len(PROVINCES)}')
        
        # 同步地图数据
        print('\n正在同步地图数据...')
        sync_map_data_from_people(db)
        
        # 获取同步后的地图数据
        map_data = db.get_map_data()
        print(f'\n同步后的地图数据:')
        total_map_count = 0
        for item in sorted(map_data, key=lambda x: x['value'], reverse=True)[:10]:
            print(f'  {item["name"]}: {item["value"]}人')
            total_map_count += item['value']
        
        print(f'\n地图数据总人数: {total_map_count}')
        print(f'实际人员总数: {len(people)}')
        
        if total_map_count == len(people):
            print('\n✓ 地图数据同步正确！')
        else:
            print(f'\n⚠️ 警告: 地图数据总人数({total_map_count})与实际人员数({len(people)})不一致')
        
    finally:
        db.disconnect()

if __name__ == '__main__':
    test_map_sync()

