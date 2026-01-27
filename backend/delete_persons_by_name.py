"""
删除指定姓名的人员数据脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from database import Database

def delete_persons_by_names(names, delete_from_local=False):
    """根据姓名删除人员数据
    
    Args:
        names: 要删除的人员姓名列表
        delete_from_local: 是否同时删除本地人员库中的数据
    """
    db = Database()
    db.connect()
    
    deleted_count = 0
    deleted_names = []
    
    try:
        # 从系统库删除
        print('正在从系统库中查找...')
        people = db.get_people()
        
        # 查找要删除的人员
        persons_to_delete = []
        for person in people:
            if person.get('name') in names:
                persons_to_delete.append(person)
        
        if persons_to_delete:
            print(f'在系统库中找到 {len(persons_to_delete)} 条记录')
            # 删除找到的人员
            for person in persons_to_delete:
                person_id = person.get('id')
                person_name = person.get('name')
                success = db.delete_person(person_id)
                if success:
                    deleted_count += 1
                    deleted_names.append(f'{person_name}(系统库)')
                    print(f'[成功] 已删除系统库: {person_name} (ID: {person_id})')
                else:
                    print(f'[失败] 删除失败: {person_name} (ID: {person_id})')
        else:
            print('系统库中未找到匹配的人员')
        
        # 从本地人员库删除（如果指定）
        if delete_from_local:
            print('\n正在从本地人员库中查找...')
            local_people = db.get_local_people()
            
            local_persons_to_delete = []
            for person in local_people:
                if person.get('name') in names:
                    local_persons_to_delete.append(person)
            
            if local_persons_to_delete:
                print(f'在本地人员库中找到 {len(local_persons_to_delete)} 条记录')
                for person in local_persons_to_delete:
                    person_id = person.get('id')
                    person_name = person.get('name')
                    # 使用批量删除方法
                    success = db.batch_delete_local_people([person_id]) > 0
                    if success:
                        deleted_count += 1
                        deleted_names.append(f'{person_name}(本地库)')
                        print(f'[成功] 已删除本地库: {person_name} (ID: {person_id})')
                    else:
                        print(f'[失败] 删除失败: {person_name} (ID: {person_id})')
            else:
                print('本地人员库中未找到匹配的人员')
        
        if deleted_count == 0:
            print(f'\n未找到姓名为 {names} 的人员')
        else:
            print(f'\n总共删除 {deleted_count} 条记录')
            print(f'删除的人员: {", ".join(deleted_names)}')
        
        return deleted_count
        
    except Exception as e:
        print(f'删除过程中发生错误: {e}')
        import traceback
        traceback.print_exc()
        return 0
    finally:
        db.disconnect()

if __name__ == '__main__':
    # 要删除的人员姓名列表
    names_to_delete = ['张三', '李四']
    
    print(f'开始删除人员数据: {", ".join(names_to_delete)}')
    print('=' * 50)
    
    deleted_count = delete_persons_by_names(names_to_delete, delete_from_local=True)
    
    print('=' * 50)
    if deleted_count > 0:
        print(f'删除完成！共删除 {deleted_count} 条记录')
    else:
        print('未找到要删除的人员或删除失败')

