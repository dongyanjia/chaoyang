"""
初始化重点人员数据
"""
from database import Database
import random

# 重点人员类别
CATEGORIES = ['高风险人员', '密切接触者', '疑似病例', '确诊病例', '境外输入', '其他']

# 优先级原因模板
REASONS = {
    '高风险人员': ['近期有高风险地区旅居史', '与确诊病例有接触', '出现相关症状', '核酸检测异常'],
    '密切接触者': ['与确诊病例密切接触', '与疑似病例密切接触', '同航班/同车厢', '同住人员确诊'],
    '疑似病例': ['出现发热症状', '出现咳嗽症状', '出现乏力症状', '核酸检测待确认'],
    '确诊病例': ['核酸检测阳性', '已确诊', '需要隔离治疗', '病情稳定'],
    '境外输入': ['从高风险国家入境', '入境后检测阳性', '隔离期间异常', '境外输入病例'],
    '其他': ['特殊情况', '需要重点关注', '上级指示', '其他原因']
}

def init_key_persons():
    """初始化重点人员数据"""
    print('=' * 50)
    print('开始初始化重点人员数据...')
    print('=' * 50)
    
    db = Database()
    db.connect()
    
    try:
        # 获取所有人员
        people = db.get_people()
        print(f'找到 {len(people)} 条人员记录')
        
        if len(people) == 0:
            print('⚠️  没有人员数据，请先初始化人员数据')
            return
        
        # 根据人员状态和随机选择，分配到不同类别
        key_person_count = 0
        
        for person in people:
            # 根据状态分配类别
            status = person.get('status', '正常')
            category = None
            priority_level = random.randint(1, 3)
            
            if status == '确诊':
                category = '确诊病例'
                priority_level = 1
            elif status == '疑似':
                category = '疑似病例'
                priority_level = 2
            else:
                # 随机分配到其他类别
                if random.random() < 0.15:  # 15%的概率成为重点人员
                    category = random.choice(CATEGORIES)
                    # 避免重复分配
                    if category == '确诊病例' and status != '确诊':
                        category = random.choice(['高风险人员', '密切接触者', '其他'])
                    if category == '疑似病例' and status != '疑似':
                        category = random.choice(['高风险人员', '密切接触者', '其他'])
            
            if category:
                reason = random.choice(REASONS.get(category, ['需要重点关注']))
                db.add_key_person(
                    person_id=person['id'],
                    category=category,
                    priority_level=priority_level,
                    reason=reason
                )
                key_person_count += 1
        
        print(f'✓ 已创建 {key_person_count} 条重点人员记录')
        
        # 统计各类别数量
        print('\n各类别统计:')
        for category in CATEGORIES:
            count = len(db.get_key_persons(category=category))
            if count > 0:
                print(f'  {category}: {count} 人')
        
        print('\n' + '=' * 50)
        print('重点人员数据初始化完成！')
        print('=' * 50)
        
    except Exception as e:
        print(f'❌ 初始化失败: {e}')
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.disconnect()


if __name__ == '__main__':
    init_key_persons()

