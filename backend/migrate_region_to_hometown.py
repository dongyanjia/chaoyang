"""
迁移人员数据：将region字段迁移到hometown（籍贯）字段
"""
from database import Database
from map_sync import REGION_TO_PROVINCE, PROVINCES
import random

def migrate_region_to_hometown():
    """将现有人员的region字段迁移到hometown字段"""
    print('=' * 50)
    print('开始迁移地区到籍贯...')
    print('=' * 50)
    
    db = Database()
    db.connect()
    
    try:
        # 获取所有人员
        people = db.get_people()
        print(f'找到 {len(people)} 条人员记录')
        
        updated_count = 0
        
        for person in people:
            person_id = person['id']
            region = person.get('region', '')
            hometown = person.get('hometown', '')
            
            # 如果已经有hometown，跳过
            if hometown:
                continue
            
            # 根据region获取对应的省份作为籍贯
            if region in REGION_TO_PROVINCE:
                new_hometown = REGION_TO_PROVINCE[region]
            else:
                # 如果region不在映射中，随机选择一个省份
                new_hometown = random.choice(PROVINCES)
            
            # 更新数据
            update_data = {
                'name': person.get('name'),
                'idCard': person.get('idCard'),
                'region': region,  # 保留region字段用于兼容
                'age': person.get('age'),
                'phone': person.get('phone'),
                'status': person.get('status'),
                'avatar': person.get('avatar'),
                'gender': person.get('gender', ''),
                'occupation': person.get('occupation', ''),
                'hometown': new_hometown,
                'tags': person.get('tags', []),
                'educationHistory': person.get('educationHistory', []),
                'workHistory': person.get('workHistory', []),
                'socialMedia': person.get('socialMedia', []),
                'visitRecords': person.get('visitRecords', []),
                'flightRecords': person.get('flightRecords', []),
                'trainRecords': person.get('trainRecords', [])
            }
            
            db.update_person(person_id, update_data)
            updated_count += 1
            
            if updated_count % 10 == 0:
                print(f'已更新 {updated_count} 条记录...')
        
        print('\n' + '=' * 50)
        print('迁移完成！')
        print('=' * 50)
        print(f'总记录数: {len(people)}')
        print(f'已更新: {updated_count}')
        print('=' * 50)
        
    except Exception as e:
        print(f'❌ 迁移失败: {e}')
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.disconnect()


if __name__ == '__main__':
    migrate_region_to_hometown()

