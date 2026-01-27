"""
查询指定姓名的人员数据脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from database import Database

def check_persons_by_names(names):
    """根据姓名查询人员数据"""
    db = Database()
    db.connect()
    
    try:
        # 获取所有人员
        people = db.get_people()
        
        print(f'数据库中总共有 {len(people)} 条人员记录')
        print('=' * 50)
        
        # 查找匹配的人员
        found_persons = []
        for person in people:
            person_name = person.get('name', '')
            if any(name in person_name for name in names):
                found_persons.append(person)
        
        if not found_persons:
            print(f'未找到姓名为 {names} 的人员')
            print('\n所有人员姓名示例（前20个）:')
            for i, person in enumerate(people[:20]):
                print(f'  {i+1}. {person.get("name")} (ID: {person.get("id")})')
        else:
            print(f'找到 {len(found_persons)} 条匹配记录:')
            for person in found_persons:
                print(f'  - {person.get("name")} (ID: {person.get("id")}, 地区: {person.get("region")}, 状态: {person.get("status")})')
        
        return found_persons
        
    except Exception as e:
        print(f'查询过程中发生错误: {e}')
        import traceback
        traceback.print_exc()
        return []
    finally:
        db.disconnect()

if __name__ == '__main__':
    # 要查询的人员姓名列表
    names_to_check = ['张三', '李四']
    
    print(f'查询人员数据: {", ".join(names_to_check)}')
    print('=' * 50)
    
    found_persons = check_persons_by_names(names_to_check)

