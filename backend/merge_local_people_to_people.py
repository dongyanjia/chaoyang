"""
合并本地人员表（local_people）到人员表（people）的脚本

功能：
1. 将 local_people 表中的数据合并到 people 表
2. 处理数据冲突（通过 id_card 匹配）
3. 如果 local_people 中的记录在 people 表中已存在，则更新 people 表
4. 如果 local_people 中的记录不存在，则插入到 people 表

使用方法：
    python merge_local_people_to_people.py
"""

import os
import sys
import pymysql
from datetime import datetime
from typing import Dict, Optional

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 从 database.py 导入数据库配置
from database import DORIS_HOST, DORIS_PORT, DORIS_USER, DORIS_PASSWORD, DORIS_DATABASE


def get_connection():
    """获取数据库连接"""
    return pymysql.connect(
        host=DORIS_HOST,
        port=DORIS_PORT,
        user=DORIS_USER,
        password=DORIS_PASSWORD,
        database=DORIS_DATABASE,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


def merge_local_people_to_people():
    """合并 local_people 表到 people 表"""
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        # 1. 获取所有 local_people 数据
        print("正在读取 local_people 表数据...")
        cursor.execute('SELECT * FROM local_people ORDER BY id')
        local_people = cursor.fetchall()
        print(f"找到 {len(local_people)} 条本地人员记录")
        
        if len(local_people) == 0:
            print("local_people 表为空，无需合并")
            return
        
        # 2. 统计信息
        inserted_count = 0
        updated_count = 0
        skipped_count = 0
        errors = []
        
        # 3. 处理每条记录
        for idx, local_person in enumerate(local_people, 1):
            try:
                # 准备数据，处理 NULL 值
                name = local_person.get('name') or ''
                id_card = local_person.get('id_card') or ''
                region = local_person.get('region') or ''
                age = local_person.get('age') or 0
                phone = local_person.get('phone') or ''
                status = local_person.get('status') or '正常'
                
                # 如果 name 为空，跳过
                if not name:
                    print(f"  跳过第 {idx} 条记录：姓名为空")
                    skipped_count += 1
                    continue
                
                # 如果 id_card 为空，生成一个临时 id_card（使用 local_people 的 id）
                if not id_card:
                    id_card = f'LOCAL_{local_person.get("id")}'
                    print(f"  第 {idx} 条记录没有身份证号，使用临时ID: {id_card}")
                
                # 检查 people 表中是否已存在（通过 id_card 匹配）
                cursor.execute('SELECT id FROM people WHERE id_card = %s', (id_card,))
                existing_person = cursor.fetchone()
                
                if existing_person:
                    # 如果已存在，更新记录
                    person_id = existing_person['id']
                    print(f"  第 {idx} 条记录已存在（id_card: {id_card}），更新记录 ID: {person_id}")
                    
                    # 更新 people 表（保留 people 表中的数据，只更新 local_people 中有值的字段）
                    update_fields = []
                    update_values = []
                    
                    # 只更新非空字段
                    if local_person.get('region'):
                        update_fields.append('region = %s')
                        update_values.append(local_person.get('region'))
                    if local_person.get('age'):
                        update_fields.append('age = %s')
                        update_values.append(local_person.get('age'))
                    if local_person.get('phone'):
                        update_fields.append('phone = %s')
                        update_values.append(local_person.get('phone'))
                    if local_person.get('status'):
                        update_fields.append('status = %s')
                        update_values.append(local_person.get('status'))
                    if local_person.get('avatar'):
                        update_fields.append('avatar = %s')
                        update_values.append(local_person.get('avatar'))
                    if local_person.get('gender'):
                        update_fields.append('gender = %s')
                        update_values.append(local_person.get('gender'))
                    if local_person.get('occupation'):
                        update_fields.append('occupation = %s')
                        update_values.append(local_person.get('occupation'))
                    if local_person.get('tags'):
                        update_fields.append('tags = %s')
                        update_values.append(local_person.get('tags'))
                    if local_person.get('education_history'):
                        update_fields.append('education_history = %s')
                        update_values.append(local_person.get('education_history'))
                    if local_person.get('work_history'):
                        update_fields.append('work_history = %s')
                        update_values.append(local_person.get('work_history'))
                    if local_person.get('social_media'):
                        update_fields.append('social_media = %s')
                        update_values.append(local_person.get('social_media'))
                    if local_person.get('visit_records'):
                        update_fields.append('visit_records = %s')
                        update_values.append(local_person.get('visit_records'))
                    if local_person.get('flight_records'):
                        update_fields.append('flight_records = %s')
                        update_values.append(local_person.get('flight_records'))
                    if local_person.get('train_records'):
                        update_fields.append('train_records = %s')
                        update_values.append(local_person.get('train_records'))
                    if local_person.get('hometown'):
                        update_fields.append('hometown = %s')
                        update_values.append(local_person.get('hometown'))
                    if local_person.get('nationality'):
                        update_fields.append('nationality = %s')
                        update_values.append(local_person.get('nationality'))
                    if local_person.get('visa_type'):
                        update_fields.append('visa_type = %s')
                        update_values.append(local_person.get('visa_type'))
                    if local_person.get('institution'):
                        update_fields.append('institution = %s')
                        update_values.append(local_person.get('institution'))
                    
                    # 更新 last_update
                    update_fields.append('last_update = %s')
                    update_values.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    
                    if update_fields:
                        update_values.append(person_id)
                        update_sql = f"UPDATE people SET {', '.join(update_fields)} WHERE id = %s"
                        cursor.execute(update_sql, update_values)
                        updated_count += 1
                    else:
                        print(f"  第 {idx} 条记录无需更新")
                        skipped_count += 1
                else:
                    # 如果不存在，插入新记录
                    print(f"  第 {idx} 条记录不存在，插入新记录（id_card: {id_card}）")
                    
                    # 确保必填字段有值
                    if not region:
                        region = '未知'
                    if not phone:
                        phone = ''
                    if not status:
                        status = '正常'
                    
                    # 插入到 people 表
                    cursor.execute('''
                        INSERT INTO people (
                            id_card, name, region, age, phone, status, avatar, last_update, created_at,
                            gender, occupation, tags, education_history, work_history, social_media,
                            visit_records, flight_records, train_records, hometown, nationality, visa_type, institution
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        id_card,
                        name,
                        region,
                        age,
                        phone,
                        status,
                        local_person.get('avatar'),
                        local_person.get('last_update') or datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        local_person.get('created_at') or datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        local_person.get('gender') or '',
                        local_person.get('occupation') or '',
                        local_person.get('tags') or '[]',
                        local_person.get('education_history') or '[]',
                        local_person.get('work_history') or '[]',
                        local_person.get('social_media') or '[]',
                        local_person.get('visit_records') or '[]',
                        local_person.get('flight_records') or '[]',
                        local_person.get('train_records') or '[]',
                        local_person.get('hometown') or '',
                        local_person.get('nationality') or '',
                        local_person.get('visa_type') or '',
                        local_person.get('institution') or ''
                    ))
                    inserted_count += 1
                
                # 每处理 100 条记录提交一次
                if (idx % 100) == 0:
                    connection.commit()
                    print(f"  已处理 {idx} 条记录，提交事务...")
            
            except Exception as e:
                error_msg = f"处理第 {idx} 条记录失败: {str(e)}"
                print(f"  [错误] {error_msg}")
                errors.append(error_msg)
                import traceback
                traceback.print_exc()
                continue
        
        # 提交剩余的事务
        connection.commit()
        
        # 4. 输出统计信息
        print("\n" + "="*60)
        print("合并完成！")
        print("="*60)
        print(f"总记录数: {len(local_people)}")
        print(f"插入记录: {inserted_count}")
        print(f"更新记录: {updated_count}")
        print(f"跳过记录: {skipped_count}")
        print(f"错误记录: {len(errors)}")
        
        if errors:
            print("\n错误详情:")
            for error in errors[:10]:  # 只显示前10个错误
                print(f"  - {error}")
            if len(errors) > 10:
                print(f"  ... 还有 {len(errors) - 10} 个错误")
        
        # 5. 询问是否删除 local_people 表
        print("\n" + "="*60)
        print("提示：合并完成后，可以删除 local_people 表")
        print("删除命令：DROP TABLE IF EXISTS local_people;")
        print("="*60)
        
    except Exception as e:
        print(f"\n合并过程发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    print("="*60)
    print("合并 local_people 表到 people 表")
    print("="*60)
    print(f"数据库: {DORIS_DATABASE}")
    print(f"主机: {DORIS_HOST}:{DORIS_PORT}")
    print("="*60)
    
    # 确认操作
    confirm = input("\n确认要合并 local_people 表到 people 表吗？(yes/no): ")
    if confirm.lower() not in ['yes', 'y']:
        print("操作已取消")
        sys.exit(0)
    
    merge_local_people_to_people()
