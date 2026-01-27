"""
更新现有人员数据的到访信息，增加省份字段
"""
import json
from database import Database
from map_sync import REGION_TO_PROVINCE, PROVINCES
import random

def update_visit_records_with_province():
    """更新所有人员的到访信息，为缺少省份的记录添加省份"""
    print('=' * 50)
    print('开始更新到访信息，增加省份字段...')
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
            visit_records = person.get('visitRecords', [])
            
            if not visit_records:
                continue
            
            # 检查是否需要更新
            needs_update = False
            updated_records = []
            
            for record in visit_records:
                # 如果缺少省份字段，需要更新
                if 'province' not in record or not record.get('province'):
                    needs_update = True
                    city = record.get('city', '')
                    # 根据城市获取省份
                    if city in REGION_TO_PROVINCE:
                        province = REGION_TO_PROVINCE[city]
                    else:
                        # 如果城市不在映射中，随机选择一个省份
                        province = random.choice(PROVINCES)
                    
                    record['province'] = province
                
                updated_records.append(record)
            
            if needs_update:
                # 更新人员数据
                update_data = {
                    'name': person.get('name'),
                    'idCard': person.get('idCard'),
                    'region': person.get('region'),
                    'age': person.get('age'),
                    'phone': person.get('phone'),
                    'status': person.get('status'),
                    'avatar': person.get('avatar'),
                    'gender': person.get('gender', ''),
                    'occupation': person.get('occupation', ''),
                    'tags': person.get('tags', []),
                    'educationHistory': person.get('educationHistory', []),
                    'workHistory': person.get('workHistory', []),
                    'socialMedia': person.get('socialMedia', []),
                    'visitRecords': updated_records,
                    'flightRecords': person.get('flightRecords', []),
                    'trainRecords': person.get('trainRecords', [])
                }
                
                db.update_person(person_id, update_data)
                updated_count += 1
                
                if updated_count % 10 == 0:
                    print(f'已更新 {updated_count} 条记录...')
        
        print('\n' + '=' * 50)
        print('更新完成！')
        print('=' * 50)
        print(f'总记录数: {len(people)}')
        print(f'已更新: {updated_count}')
        print('=' * 50)
        
    except Exception as e:
        print(f'❌ 更新失败: {e}')
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.disconnect()


if __name__ == '__main__':
    update_visit_records_with_province()

