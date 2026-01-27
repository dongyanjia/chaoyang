"""
更新现有人员数据脚本
为数据库中已有的人员补全基本信息、教育经历、工作经历、社交媒体动态等

主要功能：
- 为已有人员数据补充缺失的字段
- 生成教育经历、工作经历等扩展信息
- 生成社交媒体动态
- 生成到访记录、航班记录、铁路记录
- 更新机构、签证类型等新字段
- 支持强制更新所有数据或仅更新缺失数据

使用方法：
    python update_people_data.py          # 仅更新缺失数据
    python update_people_data.py --force  # 强制更新所有数据

作者：系统开发团队
版本：1.0.0
"""
import random
import json
from datetime import datetime, timedelta
from faker import Faker
from database import Database

# 初始化Faker库，使用中文语言环境
fake = Faker('zh_CN')

# 配置数据
GENDERS = ['男', '女']
# 经常出国的职业（20个）
OCCUPATIONS = ['外交官', '翻译', '导游', '外贸', '空乘', '飞行员', '船员', '记者', '商务', '学生',
                '教授', '医生', '工程师', '艺术家', '音乐家', '运动员', '国际咨询', '跨国公司高管', '国际律师', '国际组织工作人员']
SCHOOLS = ['北京大学', '清华大学', '复旦大学', '上海交通大学', '浙江大学', '中山大学', '华中科技大学', '西安交通大学', '四川大学', '武汉大学', 
           '北京师范大学', '中国人民大学', '北京理工大学', '北京航空航天大学', '南开大学', '天津大学', '大连理工大学', '东北大学', '吉林大学', 
           '哈尔滨工业大学', '同济大学', '华东师范大学', '南京大学', '东南大学', '中国科学技术大学', '厦门大学', '山东大学', '中国海洋大学', 
           '湖南大学', '中南大学', '华南理工大学', '重庆大学', '电子科技大学', '西北工业大学', '兰州大学']
MAJORS = ['计算机科学', '医学', '工程学', '经济学', '管理学', '文学', '法学', '教育学', '艺术学', '理学', '工学', '农学', '历史学', '哲学', '军事学']
DEGREES = ['专科', '本科', '硕士', '博士']
COMPANIES = ['阿里巴巴', '腾讯', '百度', '华为', '京东', '字节跳动', '美团', '滴滴', '小米', '网易', '新浪', '搜狐', '360', '拼多多', 
             '中国移动', '中国联通', '中国电信', '工商银行', '建设银行', '农业银行', '中国银行', '招商银行', '平安银行', '中信银行',
             '国家电网', '中石油', '中石化', '中国建筑', '中国中铁', '中国铁建', '中交集团', '中国电建']

# 机构列表（外国机构）
INSTITUTIONS = ['美国疾病控制与预防中心', '英国国家医疗服务体系', '法国公共卫生署', '德国罗伯特·科赫研究所',
                '日本国立感染症研究所', '韩国疾病管理本部', '俄罗斯联邦消费者权益保护局', '印度国家疾病控制中心',
                '澳大利亚卫生部', '加拿大公共卫生署', '意大利国家卫生研究所', '西班牙卫生部',
                '巴西卫生部', '墨西哥卫生部', '世界卫生组织']

# 国籍列表
NATIONALITIES = ['美国', '英国', '法国', '德国', '日本', '韩国', '俄罗斯', '印度', '澳大利亚', '加拿大', 
                 '意大利', '西班牙', '巴西', '墨西哥', '泰国', '新加坡', '马来西亚', '印度尼西亚', '菲律宾', '越南', '其他']

# 签证类型列表
VISA_TYPES = ['旅游签证', '工作签证', '学生签证', '商务签证', '探亲签证', '访问签证', 
               '过境签证', '居留签证', '投资签证', '技术签证', '文化交流签证', '医疗签证',
               '实习签证', '记者签证', '外交签证', '公务签证', '其他签证']
POSITIONS = ['软件工程师', '产品经理', '数据分析师', '项目经理', '销售经理', '市场专员', '人力资源', '财务', '运营', '设计师', '测试工程师',
             '前端工程师', '后端工程师', '架构师', '技术总监', '部门经理', '区域经理', '客户经理', '业务员', '行政助理', '会计', '出纳']
SOCIAL_PLATFORMS = ['微信', '微博', '抖音', 'QQ', '小红书', '知乎', 'B站', '快手', '今日头条']
REGIONS = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '西安']
VISIT_PLACES = ['商场', '医院', '学校', '餐厅', '公园', '车站', '机场', '酒店', '超市', '电影院']
AIRLINES = ['中国国际航空', '中国东方航空', '中国南方航空', '海南航空', '深圳航空']
TRAIN_TYPES = ['高铁', '动车', '普通列车']


def generate_tags(occupation, region):
    """生成标签"""
    tags = []
    if occupation:
        tags.append(occupation)
    if region:
        tags.append(f'{region}人')
    if random.random() > 0.5:
        tags.append('活跃用户')
    if random.random() > 0.6:
        tags.append('VIP会员')
    if random.random() > 0.7:
        tags.append('认证用户')
    return tags


def generate_education_history(age):
    """根据年龄生成教育经历"""
    education_history = []
    
    if age < 18:
        return education_history
    
    current_year = datetime.now().year
    birth_year = current_year - age
    
    # 小学（6-12岁）
    if age >= 12:
        education_history.append({
            'school': f'{random.choice(REGIONS)}市第一小学',
            'major': '基础教育',
            'degree': '小学',
            'startDate': f'{birth_year + 6}-09',
            'endDate': f'{birth_year + 12}-06'
        })
    
    # 初中（12-15岁）
    if age >= 15:
        education_history.append({
            'school': f'{random.choice(REGIONS)}市第一中学',
            'major': '基础教育',
            'degree': '初中',
            'startDate': f'{birth_year + 12}-09',
            'endDate': f'{birth_year + 15}-06'
        })
    
    # 高中/中专（15-18岁）
    if age >= 18:
        school_type = random.choice(['高中', '中专', '职高'])
        education_history.append({
            'school': f'{random.choice(REGIONS)}市第{random.randint(1, 10)}中学' if school_type == '高中' else f'{random.choice(REGIONS)}市职业技术学校',
            'major': random.choice(['理科', '文科', '工科', '商科']) if school_type == '高中' else random.choice(MAJORS),
            'degree': school_type,
            'startDate': f'{birth_year + 15}-09',
            'endDate': f'{birth_year + 18}-06'
        })
    
    # 大学及以上（18岁以后）
    if age >= 22:
        # 本科
        edu_count = random.randint(1, 3)
        for i in range(edu_count):
            start_year = birth_year + 18 + i * 4
            end_year = start_year + random.randint(3, 5)
            if end_year > current_year:
                end_year = current_year
            
            degree = random.choice(DEGREES)
            if i == 0:
                degree = '本科'
            elif i == 1:
                degree = random.choice(['硕士', '博士'])
            else:
                degree = '博士'
            
            education_history.append({
                'school': random.choice(SCHOOLS),
                'major': random.choice(MAJORS),
                'degree': degree,
                'startDate': f'{start_year}-09',
                'endDate': f'{end_year}-06' if end_year < current_year else '至今'
            })
    
    return education_history


def generate_work_history(age, occupation):
    """根据年龄和职业生成工作经历"""
    work_history = []
    
    if age < 22:
        return work_history
    
    current_year = datetime.now().year
    birth_year = current_year - age
    start_work_year = birth_year + 22  # 假设22岁开始工作
    
    # 根据年龄决定工作经历数量
    if age < 25:
        work_count = 1
    elif age < 30:
        work_count = random.randint(1, 2)
    elif age < 40:
        work_count = random.randint(2, 3)
    else:
        work_count = random.randint(3, 5)
    
    work_descriptions = {
        '教师': ['负责教学工作', '参与课程开发', '指导学生科研', '组织教学活动'],
        '医生': ['临床诊疗工作', '参与手术', '病例研究', '医学教学'],
        '工程师': ['产品开发', '技术攻关', '系统设计', '代码审查'],
        '学生': ['学习专业知识', '参与科研项目', '实习实践'],
        '公务员': ['行政管理工作', '政策执行', '公共服务', '文件处理'],
        '商人': ['业务拓展', '客户维护', '市场分析', '团队管理'],
        '工人': ['生产作业', '设备维护', '质量检测', '安全操作'],
        '农民': ['农业生产', '作物管理', '农机操作', '产品销售'],
        '自由职业': ['项目承接', '客户服务', '创意设计', '咨询服务'],
        '退休': ['退休前工作', '项目管理', '经验传承']
    }
    
    for i in range(work_count):
        start_year = start_work_year + i * random.randint(2, 4)
        end_year = start_year + random.randint(1, 6)
        if end_year > current_year:
            end_year = current_year
        
        # 根据职业选择合适的公司类型
        if occupation == '教师':
            company = f'{random.choice(REGIONS)}市第{random.randint(1, 20)}中学' if random.random() > 0.3 else f'{random.choice(REGIONS)}大学'
        elif occupation == '医生':
            company = f'{random.choice(REGIONS)}市第{random.randint(1, 5)}人民医院' if random.random() > 0.3 else f'{random.choice(REGIONS)}医学院附属医院'
        elif occupation == '学生':
            company = f'{random.choice(SCHOOLS)}' if random.random() > 0.5 else f'{random.choice(COMPANIES)}（实习）'
        elif occupation == '公务员':
            company = f'{random.choice(REGIONS)}市{random.choice(["政府", "税务局", "工商局", "教育局", "卫生局"])}'
        elif occupation == '农民':
            company = f'{random.choice(REGIONS)}市{random.choice(["农业合作社", "农场", "种植基地"])}'
        elif occupation == '退休':
            company = random.choice(COMPANIES)
        else:
            company = random.choice(COMPANIES)
        
        position = occupation if occupation != '学生' else '实习生'
        if occupation in ['工程师', '医生', '教师'] and i > 0:
            position = random.choice(POSITIONS)
        
        desc_list = work_descriptions.get(occupation, ['日常工作', '业务处理', '团队协作'])
        description = random.choice(desc_list)
        
        work_history.append({
            'company': company,
            'position': position,
            'startDate': f'{start_year}-01',
            'endDate': f'{end_year}-12' if end_year < current_year else '至今',
            'description': description
        })
    
    return work_history


def generate_social_media(age):
    """生成社交媒体动态"""
    social_media = []
    
    # 根据年龄决定社交媒体动态数量
    if age < 25:
        count = random.randint(5, 15)
    elif age < 40:
        count = random.randint(3, 10)
    else:
        count = random.randint(2, 8)
    
    contents = [
        '今天天气真好！',
        '分享一些生活感悟',
        '工作之余的休闲时光',
        '最近在学习新技能',
        '和朋友一起聚餐',
        '周末去公园散步',
        '看了一部不错的电影',
        '推荐一本好书',
        '今天完成了一个重要项目',
        '记录生活中的美好瞬间',
        '参加了一个有趣的活动',
        '今天心情不错',
        '分享一张美图',
        '思考人生',
        '努力工作，加油！',
        '享受周末时光',
        '今天学到了新知识',
        '和家人一起度过美好时光',
        '运动让我充满活力',
        '今天是个好日子'
    ]
    
    for i in range(count):
        days_ago = random.randint(0, 180)  # 最近6个月
        post_time = (datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))).strftime('%Y-%m-%d %H:%M:%S')
        
        social_media.append({
            'platform': random.choice(SOCIAL_PLATFORMS),
            'content': random.choice(contents),
            'time': post_time
        })
    
    # 按时间排序
    social_media.sort(key=lambda x: x['time'], reverse=True)
    
    return social_media


def generate_visit_records(region):
    """生成到访信息"""
    # 导入省份映射
    from map_sync import REGION_TO_PROVINCE, PROVINCES
    
    visit_records = []
    visit_count = random.randint(3, 15)
    for i in range(visit_count):
        days_ago = random.randint(0, 180)
        visit_time = (datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))).strftime('%Y-%m-%d %H:%M:%S')
        visit_city = random.choice(REGIONS)
        # 根据城市获取省份
        visit_province = REGION_TO_PROVINCE.get(visit_city, random.choice(PROVINCES))
        visit_records.append({
            'place': random.choice(VISIT_PLACES),
            'city': visit_city,
            'province': visit_province,
            'time': visit_time
        })
    visit_records.sort(key=lambda x: x['time'], reverse=True)
    return visit_records


def generate_flight_records(region):
    """生成民航记录"""
    flight_records = []
    flight_count = random.randint(0, 8)
    for i in range(flight_count):
        days_ago = random.randint(0, 365)
        flight_time = (datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))).strftime('%Y-%m-%d %H:%M:%S')
        flight_number = f'{random.choice(["CA", "MU", "CZ", "HU", "ZH"])}{random.randint(1000, 9999)}'
        flight_records.append({
            'airline': random.choice(AIRLINES),
            'flightNumber': flight_number,
            'fromCity': random.choice(REGIONS),
            'toCity': random.choice([r for r in REGIONS if r != region]),
            'time': flight_time
        })
    flight_records.sort(key=lambda x: x['time'], reverse=True)
    return flight_records


def generate_train_records(region):
    """生成铁路记录"""
    train_records = []
    train_count = random.randint(0, 12)
    for i in range(train_count):
        days_ago = random.randint(0, 365)
        train_time = (datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))).strftime('%Y-%m-%d %H:%M:%S')
        train_number = f'{random.choice(["G", "D", "K", "T", "Z"])}{random.randint(1, 9999)}'
        train_records.append({
            'type': random.choice(TRAIN_TYPES),
            'trainNumber': train_number,
            'fromCity': random.choice(REGIONS),
            'toCity': random.choice([r for r in REGIONS if r != region]),
            'time': train_time
        })
    train_records.sort(key=lambda x: x['time'], reverse=True)
    return train_records


def update_people_data(force_update=False):
    """更新现有人员数据"""
    print('=' * 50)
    print('开始更新人员数据...')
    print('=' * 50)
    
    db = Database()
    db.connect()
    
    try:
        # 获取所有人员
        people = db.get_people()
        print(f'找到 {len(people)} 条人员记录')
        
        updated_count = 0
        skipped_count = 0
        
        for person in people:
            person_id = person['id']
            age = person.get('age', random.randint(18, 80))
            
            # 检查是否需要更新
            needs_update = False
            if force_update:
                needs_update = True
            else:
                # 检查是否缺少扩展信息
                if not person.get('gender') or not person.get('occupation'):
                    needs_update = True
                elif not person.get('tags') or person.get('tags') == []:
                    needs_update = True
                elif not person.get('educationHistory') or person.get('educationHistory') == []:
                    needs_update = True
                elif not person.get('workHistory') or person.get('workHistory') == []:
                    needs_update = True
                elif not person.get('socialMedia') or person.get('socialMedia') == []:
                    needs_update = True
                elif not person.get('visitRecords') or person.get('visitRecords') == []:
                    needs_update = True
                elif not person.get('flightRecords') or person.get('flightRecords') == []:
                    needs_update = True
                elif not person.get('trainRecords') or person.get('trainRecords') == []:
                    needs_update = True
                elif not person.get('institution'):
                    needs_update = True
                elif not person.get('visaType'):
                    needs_update = True
            
            if not needs_update:
                skipped_count += 1
                continue
            
            # 生成扩展信息
            gender = person.get('gender') or random.choice(GENDERS)
            occupation = person.get('occupation') or random.choice(OCCUPATIONS)
            region = person.get('region', random.choice(REGIONS))
            
            # 生成籍贯信息
            from map_sync import PROVINCES, REGION_TO_PROVINCE
            hometown = person.get('hometown')
            if not hometown:
                # 如果没有籍贯，根据region获取对应的省份作为籍贯，或者随机选择一个省份
                hometown = REGION_TO_PROVINCE.get(region, random.choice(PROVINCES))
            
            tags = person.get('tags') or generate_tags(occupation, region)
            education_history = person.get('educationHistory') or generate_education_history(age)
            work_history = person.get('workHistory') or generate_work_history(age, occupation)
            social_media = person.get('socialMedia') or generate_social_media(age)
            visit_records = person.get('visitRecords') or generate_visit_records(region)
            flight_records = person.get('flightRecords') or generate_flight_records(region)
            train_records = person.get('trainRecords') or generate_train_records(region)
            
            # 生成机构、签证信息
            institution = person.get('institution') or random.choice(INSTITUTIONS)
            visa_type = person.get('visaType') or random.choice(VISA_TYPES)
            
            # 更新数据
            update_data = {
                'name': person.get('name'),
                'idCard': person.get('idCard'),
                'region': region,  # 保留region用于兼容
                'age': age,
                'phone': person.get('phone'),
                'status': person.get('status'),
                'avatar': person.get('avatar'),
                'gender': gender,
                'occupation': occupation,
                'hometown': hometown,
                'tags': tags if isinstance(tags, list) else [],
                'educationHistory': education_history if isinstance(education_history, list) else [],
                'workHistory': work_history if isinstance(work_history, list) else [],
                'socialMedia': social_media if isinstance(social_media, list) else [],
                'visitRecords': visit_records if isinstance(visit_records, list) else [],
                'flightRecords': flight_records if isinstance(flight_records, list) else [],
                'trainRecords': train_records if isinstance(train_records, list) else [],
                'institution': institution,
                'visaType': visa_type
            }
            
            db.update_person(person_id, update_data)
            updated_count += 1
            
            if updated_count % 10 == 0:
                print(f'已更新 {updated_count} 条记录...')
        
        print('\n' + '=' * 50)
        print('数据更新完成！')
        print('=' * 50)
        print(f'总记录数: {len(people)}')
        print(f'已更新: {updated_count}')
        print(f'已跳过: {skipped_count}')
        print('=' * 50)
        
    except Exception as e:
        print(f'❌ 更新失败: {e}')
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.disconnect()


if __name__ == '__main__':
    import sys
    
    # 检查是否强制更新所有记录
    force_update = '--force' in sys.argv or '-f' in sys.argv
    
    if force_update:
        print('⚠️  警告：将强制更新所有人员记录（包括已有完整信息的记录）')
        confirm = input('确定要继续吗？(y/n): ')
        if confirm.lower() != 'y':
            print('已取消')
            exit(0)
    
    update_people_data(force_update=force_update)

