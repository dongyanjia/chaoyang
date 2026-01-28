"""
数据库初始化脚本
生成假数据并填充到数据库中

主要功能：
- 生成模拟的人员数据
- 生成流动记录数据
- 生成地图数据
- 生成趋势数据
- 支持清空现有数据或追加数据

使用方法：
    python init_database.py
    
或者在代码中调用：
    from init_database import init_database
    init_database(clear_existing=False, people_count=8000, movements_count=16000)

作者：系统开发团队
版本：1.0.0
"""
import random
import json
from datetime import datetime, timedelta
from faker import Faker
from database import Database

# 初始化Faker库，使用中文语言环境生成中文假数据
fake = Faker('zh_CN')

# 配置数据 - 扩展城市列表，覆盖所有34个省份
REGIONS = [
    # 直辖市
    '北京', '上海', '天津', '重庆',
    # 广东省
    '广州', '深圳', '珠海', '佛山', '东莞', '中山',
    # 浙江省
    '杭州', '宁波', '温州', '嘉兴', '绍兴',
    # 江苏省
    '南京', '苏州', '无锡', '常州', '徐州',
    # 山东省
    '济南', '青岛', '烟台', '潍坊', '临沂',
    # 四川省
    '成都', '绵阳', '德阳', '南充', '宜宾',
    # 湖北省
    '武汉', '襄阳', '宜昌', '荆州', '黄冈',
    # 河南省
    '郑州', '洛阳', '南阳', '新乡', '商丘',
    # 湖南省
    '长沙', '株洲', '湘潭', '衡阳', '岳阳',
    # 安徽省
    '合肥', '芜湖', '蚌埠', '淮南', '马鞍山',
    # 福建省
    '福州', '厦门', '泉州', '漳州', '莆田',
    # 陕西省
    '西安', '宝鸡', '咸阳', '渭南', '汉中',
    # 辽宁省
    '沈阳', '大连', '鞍山', '抚顺', '本溪',
    # 河北省
    '石家庄', '唐山', '保定', '邯郸', '秦皇岛',
    # 江西省
    '南昌', '赣州', '九江', '上饶', '宜春',
    # 云南省
    '昆明', '曲靖', '玉溪', '大理', '红河',
    # 广西壮族自治区
    '南宁', '桂林', '柳州', '北海', '梧州',
    # 贵州省
    '贵阳', '遵义', '六盘水', '安顺', '毕节',
    # 山西省
    '太原', '大同', '运城', '临汾', '长治',
    # 内蒙古自治区
    '呼和浩特', '包头', '赤峰', '鄂尔多斯', '通辽',
    # 吉林省
    '长春', '吉林', '四平', '松原', '通化',
    # 黑龙江省
    '哈尔滨', '齐齐哈尔', '大庆', '牡丹江', '佳木斯',
    # 新疆维吾尔自治区
    '乌鲁木齐', '克拉玛依', '石河子', '库尔勒', '伊宁',
    # 甘肃省
    '兰州', '天水', '酒泉', '张掖', '武威',
    # 海南省
    '海口', '三亚', '儋州', '琼海', '文昌',
    # 宁夏回族自治区
    '银川', '石嘴山', '吴忠', '固原', '中卫',
    # 青海省
    '西宁', '海东', '格尔木', '德令哈', '玉树',
    # 西藏自治区
    '拉萨', '日喀则', '昌都', '林芝', '那曲',
    # 香港特别行政区
    '香港',
    # 澳门特别行政区
    '澳门',
    # 台湾省
    '台北', '高雄', '台中', '台南', '新北'
]
STATUSES = ['正常', '疑似', '确诊', '康复']
GENDERS = ['男', '女']
# 经常出国的职业（20个）
OCCUPATIONS = ['外交官', '翻译', '导游', '外贸', '空乘', '飞行员', '船员', '记者', '商务', '学生',
                '教授', '医生', '工程师', '艺术家', '音乐家', '运动员', '国际咨询', '跨国公司高管', '国际律师', '国际组织工作人员']
# 机构列表（外国机构）
INSTITUTIONS = ['美国疾病控制与预防中心', '英国国家医疗服务体系', '法国公共卫生署', '德国罗伯特·科赫研究所',
                '日本国立感染症研究所', '韩国疾病管理本部', '俄罗斯联邦消费者权益保护局', '印度国家疾病控制中心',
                '澳大利亚卫生部', '加拿大公共卫生署', '意大利国家卫生研究所', '西班牙卫生部',
                '巴西卫生部', '墨西哥卫生部', '世界卫生组织']
# 签证类型列表
VISA_TYPES = ['旅游签证', '工作签证', '学生签证', '商务签证', '探亲签证', '访问签证', 
               '过境签证', '居留签证', '投资签证', '技术签证', '文化交流签证', '医疗签证',
               '实习签证', '记者签证', '外交签证', '公务签证', '其他签证']
SCHOOLS = ['北京大学', '清华大学', '复旦大学', '上海交通大学', '浙江大学', '中山大学', '华中科技大学', '西安交通大学', '四川大学', '武汉大学', 
           '北京师范大学', '中国人民大学', '北京理工大学', '北京航空航天大学', '南开大学', '天津大学', '大连理工大学', '东北大学', '吉林大学', 
           '哈尔滨工业大学', '同济大学', '华东师范大学', '南京大学', '东南大学', '中国科学技术大学', '厦门大学', '山东大学', '中国海洋大学', 
           '湖南大学', '中南大学', '华南理工大学', '重庆大学', '电子科技大学', '西北工业大学', '兰州大学']
MAJORS = ['计算机科学', '医学', '工程学', '经济学', '管理学', '文学', '法学', '教育学', '艺术学', '理学', '工学', '农学', '历史学', '哲学', '军事学']
DEGREES = ['专科', '本科', '硕士', '博士']
COMPANIES = ['阿里巴巴', '腾讯', '百度', '华为', '京东', '字节跳动', '美团', '滴滴', '小米', '网易', '新浪', '搜狐', '360', '拼多多', 
             '中国移动', '中国联通', '中国电信', '工商银行', '建设银行', '农业银行', '中国银行', '招商银行', '平安银行', '中信银行',
             '国家电网', '中石油', '中石化', '中国建筑', '中国中铁', '中国铁建', '中交集团', '中国电建']
POSITIONS = ['软件工程师', '产品经理', '数据分析师', '项目经理', '销售经理', '市场专员', '人力资源', '财务', '运营', '设计师', '测试工程师',
             '前端工程师', '后端工程师', '架构师', '技术总监', '部门经理', '区域经理', '客户经理', '业务员', '行政助理', '会计', '出纳']
SOCIAL_PLATFORMS = ['微信', '微博', '抖音', 'QQ', '小红书', '知乎', 'B站', '快手', '今日头条']
VISIT_PLACES = ['商场', '医院', '学校', '餐厅', '公园', '车站', '机场', '酒店', '超市', '电影院']
AIRLINES = ['中国国际航空', '中国东方航空', '中国南方航空', '海南航空', '深圳航空']
TRAIN_TYPES = ['高铁', '动车', '普通列车']

# 省份人口流动度等级定义（用于人员分配）
# 高流动度：一线城市和经济发达省份，人员数量多
# 中流动度：中等发达省份，人员数量中等
# 低流动度：经济欠发达或人口稀少省份，人员数量少
PROVINCE_MOBILITY_LEVELS = {
    # 高流动度省份（目标人数：200-400人）
    '北京市': 400,
    '上海市': 400,
    '广东省': 350,
    '浙江省': 300,
    '江苏省': 300,
    '香港特别行政区': 250,
    
    # 中高流动度省份（目标人数：150-250人）
    '山东省': 250,
    '四川省': 220,
    '湖北省': 200,
    '河南省': 200,
    '湖南省': 200,
    '安徽省': 180,
    '福建省': 180,
    '陕西省': 180,
    '重庆市': 180,
    '天津市': 180,
    
    # 中等流动度省份（目标人数：100-150人）
    '辽宁省': 150,
    '河北省': 140,
    '江西省': 130,
    '云南省': 120,
    '台湾省': 120,
    '广西壮族自治区': 120,
    '贵州省': 110,
    '山西省': 100,
    
    # 中低流动度省份（目标人数：50-100人）
    '内蒙古自治区': 90,
    '吉林省': 80,
    '黑龙江省': 70,
    '新疆维吾尔自治区': 60,
    '澳门特别行政区': 60,
    '甘肃省': 50,
    '海南省': 50,
    
    # 低流动度省份（目标人数：20-50人）
    '宁夏回族自治区': 40,
    '青海省': 30,
    '西藏自治区': 20
}

# 地图省份数据（保留用于兼容性，但实际使用PROVINCE_MOBILITY_LEVELS）
PROVINCES = {
    '北京市': (2500, 3000),
    '上海市': (2400, 3000),
    '广东省': (2200, 2800),
    '浙江省': (2000, 2600),
    '江苏省': (1900, 2500),
    '山东省': (1700, 2200),
    '四川省': (1600, 2100),
    '湖北省': (1500, 2000),
    '河南省': (1500, 2000),
    '湖南省': (1400, 1900),
    '安徽省': (1300, 1800),
    '福建省': (1300, 1800),
    '香港特别行政区': (1800, 2400),
    '陕西省': (1100, 1600),
    '辽宁省': (1000, 1500),
    '河北省': (900, 1400),
    '重庆市': (800, 1300),
    '天津市': (800, 1300),
    '江西省': (700, 1200),
    '云南省': (600, 1100),
    '台湾省': (1000, 1500),
    '广西壮族自治区': (500, 1000),
    '贵州省': (400, 900),
    '山西省': (300, 800),
    '内蒙古自治区': (200, 600),
    '吉林省': (150, 550),
    '黑龙江省': (100, 500),
    '新疆维吾尔自治区': (50, 450),
    '澳门特别行政区': (500, 1000),
    '甘肃省': (0, 400),
    '海南省': (0, 350),
    '宁夏回族自治区': (0, 300),
    '青海省': (0, 250),
    '西藏自治区': (0, 200)
}


def generate_people_data(db: Database, count: int = 8000):
    """生成人员假数据
    根据人口流动度分配人员，高流动度省份人员多，低流动度省份人员少
    确保每个省份都有人，且有明显的区分度
    """
    print(f'正在生成 {count} 条人员数据...')
    
    people = []
    batch_size = 100  # 每批处理100条，显示进度
    
    # 导入省份列表和映射关系
    from map_sync import PROVINCES as ALL_PROVINCES, REGION_TO_PROVINCE
    
    # 计算总目标人数
    total_target = sum(PROVINCE_MOBILITY_LEVELS.values())
    print(f'总目标人数: {total_target}人（实际生成: {count}人）')
    
    # 如果目标总数与count不一致，按比例调整
    scale_factor = count / total_target if total_target > 0 else 1.0
    
    # 计算每个省份的目标人数（按比例缩放，但确保至少1人）
    province_targets = {}
    for province, target in PROVINCE_MOBILITY_LEVELS.items():
        scaled_target = max(1, int(target * scale_factor))
        province_targets[province] = scaled_target
    
    # 调整总数，确保总和等于count
    current_total = sum(province_targets.values())
    if current_total != count:
        diff = count - current_total
        # 将差值分配给高流动度省份
        high_mobility_provinces = sorted(
            [(p, t) for p, t in province_targets.items() if PROVINCE_MOBILITY_LEVELS[p] >= 200],
            key=lambda x: PROVINCE_MOBILITY_LEVELS[x[0]],
            reverse=True
        )
        for i in range(abs(diff)):
            if diff > 0:
                province_targets[high_mobility_provinces[i % len(high_mobility_provinces)][0]] += 1
            else:
                province_targets[high_mobility_provinces[i % len(high_mobility_provinces)][0]] = max(1, province_targets[high_mobility_provinces[i % len(high_mobility_provinces)][0]] - 1)
    
    print(f'\n各省份目标人数分布:')
    sorted_targets = sorted(province_targets.items(), key=lambda x: x[1], reverse=True)
    for province, target in sorted_targets[:10]:
        mobility_level = PROVINCE_MOBILITY_LEVELS[province]
        level_name = '高' if mobility_level >= 200 else ('中' if mobility_level >= 100 else '低')
        print(f'  {province}: {target}人 (流动度: {level_name})')
    print(f'  ... (共{len(province_targets)}个省份)')
    
    # 统计每个省份已生成的人数
    province_counts = {province: 0 for province in ALL_PROVINCES}
    
    # 为每个省份生成目标数量的人员
    print(f'\n开始生成人员数据...')
    for province, target_count in province_targets.items():
        # 找到该省份对应的城市
        province_cities = [city for city, p in REGION_TO_PROVINCE.items() if p == province]
        if not province_cities:
            # 如果没有对应城市，使用省份名称作为城市
            province_cities = [province.replace('省', '').replace('市', '').replace('自治区', '').replace('特别行政区', '').replace('维吾尔', '').replace('壮族', '').replace('回族', '')]
        
        # 为该省份生成目标数量的人员
        for person_idx in range(target_count):
            region = random.choice(province_cities) if province_cities else REGIONS[0]
            age = random.randint(18, 80)
            gender = random.choice(GENDERS)
            occupation = random.choice(OCCUPATIONS)
            
            # 生成标签
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
            
            # 生成教育经历（更完整的教育经历）
            education_history = []
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
                edu_count = random.randint(1, 3)
                for j in range(edu_count):
                    start_year = birth_year + 18 + j * 4
                    end_year = start_year + random.randint(3, 5)
                    if end_year > current_year:
                        end_year = current_year
                    
                    degree = '本科' if j == 0 else ('硕士' if j == 1 else '博士')
                    
                    education_history.append({
                        'school': random.choice(SCHOOLS),
                        'major': random.choice(MAJORS),
                        'degree': degree,
                        'startDate': f'{start_year}-09',
                        'endDate': f'{end_year}-06' if end_year < current_year else '至今'
                    })
            
            # 生成工作经历（更真实的工作经历）
            work_history = []
            if age >= 22:  # 22岁开始工作
                current_year = datetime.now().year
                birth_year = current_year - age
                start_work_year = birth_year + 22
                
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
                
                for j in range(work_count):
                    start_year = start_work_year + j * random.randint(2, 4)
                    end_year = start_year + random.randint(1, 6)
                    if end_year > current_year:
                        end_year = current_year
                    
                    # 根据职业选择合适的公司类型
                    if occupation == '教师':
                        company = f'{random.choice(REGIONS)}市第{random.randint(1, 20)}中学' if random.random() > 0.3 else f'{random.choice(SCHOOLS)}'
                    elif occupation == '医生':
                        company = f'{random.choice(REGIONS)}市第{random.randint(1, 5)}人民医院' if random.random() > 0.3 else f'{random.choice(SCHOOLS)}附属医院'
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
                    if occupation in ['工程师', '医生', '教师'] and j > 0:
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
            
            # 生成社交媒体动态（更丰富的内容）
            social_media = []
            # 根据年龄决定社交媒体动态数量
            if age < 25:
                social_count = random.randint(5, 15)
            elif age < 40:
                social_count = random.randint(3, 10)
            else:
                social_count = random.randint(2, 8)
            
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
            
            for j in range(social_count):
                days_ago = random.randint(0, 180)  # 最近6个月
                post_time = (datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))).strftime('%Y-%m-%d %H:%M:%S')
                
                social_media.append({
                    'platform': random.choice(SOCIAL_PLATFORMS),
                    'content': random.choice(contents),
                    'time': post_time
                })
            
            # 按时间排序
            social_media.sort(key=lambda x: x['time'], reverse=True)
            
            # 生成到访信息
            from map_sync import REGION_TO_PROVINCE, PROVINCES
            visit_records = []
            visit_count = random.randint(3, 15)
            for j in range(visit_count):
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
            
            # 生成民航记录
            flight_records = []
            flight_count = random.randint(0, 8)
            for j in range(flight_count):
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
            
            # 生成铁路记录
            train_records = []
            train_count = random.randint(0, 12)
            for j in range(train_count):
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
            
            # 生成签证类型和机构
            visa_type = random.choice(VISA_TYPES)
            institution = random.choice(INSTITUTIONS)
            
            person = {
                'name': fake.name(),
                'idCard': fake.ssn(),
                'region': region,  # 保留region用于兼容，但主要使用hometown
                'age': age,
                'phone': fake.phone_number(),
                'status': random.choice(STATUSES),
                'avatar': f'/api/avatars/avatar_{len(people) % 20 + 1}.jpg',
                'lastUpdate': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S'),
                'gender': gender,
                'occupation': occupation,
                'hometown': province,  # 使用当前省份作为籍贯
                'visaType': visa_type,
                'institution': institution,
                'tags': tags,
                'educationHistory': education_history,
                'workHistory': work_history,
                'socialMedia': social_media,
                'visitRecords': visit_records,
                'flightRecords': flight_records,
                'trainRecords': train_records
            }
            people.append(person)
            province_counts[province] += 1  # 更新省份计数
            
            # 每处理一定数量显示进度
            if len(people) % batch_size == 0 or len(people) == count:
                progress = len(people) / count * 100
                print(f'  进度: {len(people)}/{count} ({progress:.1f}%)')
        
        # 显示该省份完成情况
        if target_count > 0:
            print(f'  [OK] {province}: {province_counts[province]}/{target_count}人')
    
    # 直接使用 SQL 插入，跳过查询返回，减少内存占用
    print('正在插入数据库...')
    inserted_count = 0
    cursor = db.connection.cursor()
    
    for idx, person in enumerate(people):
        try:
            # 直接执行 INSERT，不查询返回结果
            cursor.execute('''
                INSERT INTO people (name, id_card, region, age, phone, status, avatar, last_update, 
                                  gender, occupation, tags, education_history, work_history, social_media,
                                  visit_records, flight_records, train_records, hometown, nationality, visa_type, institution)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                person['name'],
                person['idCard'],
                person.get('region', ''),
                int(person['age']),
                person['phone'],
                person['status'],
                person.get('avatar', ''),
                person.get('lastUpdate', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                person.get('gender', ''),
                person.get('occupation', ''),
                json.dumps(person.get('tags', []), ensure_ascii=False) if isinstance(person.get('tags'), list) else person.get('tags', '[]'),
                json.dumps(person.get('educationHistory', []), ensure_ascii=False) if isinstance(person.get('educationHistory'), list) else person.get('educationHistory', '[]'),
                json.dumps(person.get('workHistory', []), ensure_ascii=False) if isinstance(person.get('workHistory'), list) else person.get('workHistory', '[]'),
                json.dumps(person.get('socialMedia', []), ensure_ascii=False) if isinstance(person.get('socialMedia'), list) else person.get('socialMedia', '[]'),
                json.dumps(person.get('visitRecords', []), ensure_ascii=False) if isinstance(person.get('visitRecords'), list) else person.get('visitRecords', '[]'),
                json.dumps(person.get('flightRecords', []), ensure_ascii=False) if isinstance(person.get('flightRecords'), list) else person.get('flightRecords', '[]'),
                json.dumps(person.get('trainRecords', []), ensure_ascii=False) if isinstance(person.get('trainRecords'), list) else person.get('trainRecords', '[]'),
                person.get('hometown', ''),
                person.get('nationality', ''),
                person.get('visaType', ''),
                person.get('institution', '')
            ))
            inserted_count += 1
            
            # 每插入一定数量提交一次，减少内存占用
            if (idx + 1) % 20 == 0:
                db.connection.commit()
                progress = (idx + 1) / len(people) * 100
                print(f'  插入进度: {idx + 1}/{len(people)} ({progress:.1f}%)')
                
        except Exception as insert_error:
            error_msg = str(insert_error)
            # 如果是内存错误，等待一下再继续
            if 'MEM' in error_msg or 'memory' in error_msg.lower():
                print(f'  [WARN] 第 {idx + 1} 条数据插入时内存不足，等待后继续...')
                import time
                time.sleep(2)  # 等待2秒让内存释放
                try:
                    # 重试一次
                    cursor.execute('''
                        INSERT INTO people (name, id_card, region, age, phone, status, avatar, last_update, 
                                          gender, occupation, tags, education_history, work_history, social_media,
                                          visit_records, flight_records, train_records, hometown, nationality, visa_type, institution)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        person['name'],
                        person['idCard'],
                        person.get('region', ''),
                        int(person['age']),
                        person['phone'],
                        person['status'],
                        person.get('avatar', ''),
                        person.get('lastUpdate', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                        person.get('gender', ''),
                        person.get('occupation', ''),
                        json.dumps(person.get('tags', []), ensure_ascii=False) if isinstance(person.get('tags'), list) else person.get('tags', '[]'),
                        json.dumps(person.get('educationHistory', []), ensure_ascii=False) if isinstance(person.get('educationHistory'), list) else person.get('educationHistory', '[]'),
                        json.dumps(person.get('workHistory', []), ensure_ascii=False) if isinstance(person.get('workHistory'), list) else person.get('workHistory', '[]'),
                        json.dumps(person.get('socialMedia', []), ensure_ascii=False) if isinstance(person.get('socialMedia'), list) else person.get('socialMedia', '[]'),
                        json.dumps(person.get('visitRecords', []), ensure_ascii=False) if isinstance(person.get('visitRecords'), list) else person.get('visitRecords', '[]'),
                        json.dumps(person.get('flightRecords', []), ensure_ascii=False) if isinstance(person.get('flightRecords'), list) else person.get('flightRecords', '[]'),
                        json.dumps(person.get('trainRecords', []), ensure_ascii=False) if isinstance(person.get('trainRecords'), list) else person.get('trainRecords', '[]'),
                        person.get('hometown', ''),
                        person.get('nationality', ''),
                        person.get('visaType', ''),
                        person.get('institution', '')
                    ))
                    inserted_count += 1
                except:
                    print(f'  [ERROR] 重试后仍然失败，跳过第 {idx + 1} 条数据')
                    continue
            else:
                print(f'  [WARN] 插入第 {idx + 1} 条数据失败: {error_msg[:100]}')
                continue
    
    # 提交剩余的数据
    db.connection.commit()
    cursor.close()
    print(f'[OK] 已生成并插入 {inserted_count}/{len(people)} 条人员数据')
    
    return people


def generate_movements_data(db: Database, people_list: list, movements_count: int = 200):
    """生成流动记录假数据"""
    print(f'正在生成 {movements_count} 条流动记录...')
    
    if not people_list:
        print('[WARN] 没有人员数据，跳过流动记录生成')
        return []
    
    movements = []
    for i in range(movements_count):
        # 从已有的人员列表中随机选择
        person = random.choice(people_list)
        # 使用索引+1作为person_id（因为数据是按顺序插入的）
        person_idx = people_list.index(person)
        person_id = person_idx + 1
        
        from_region = random.choice(REGIONS)
        to_region = random.choice([r for r in REGIONS if r != from_region])
        
        movement = {
            'personId': person_id,
            'name': person.get('name', f'人员{person_id}'),
            'avatar': person.get('avatar', '/api/avatars/avatar_1.jpg'),
            'from': from_region,
            'to': to_region,
            'time': (datetime.now() - timedelta(hours=random.randint(0, 720))).strftime('%Y-%m-%d %H:%M:%S'),
            'status': random.choice(STATUSES)
        }
        movements.append(movement)
        db.create_movement(movement)
    
    print(f'[OK] 已生成 {movements_count} 条流动记录')
    return movements


def generate_map_data(db: Database):
    """生成地图数据（各省份监测人数）"""
    print('正在生成地图数据...')
    
    map_data = []
    for province, (min_val, max_val) in PROVINCES.items():
        value = random.randint(min_val, max_val)
        map_data.append({
            'name': province,
            'value': value
        })
        db.update_map_data(province, value)
    
    print(f'[OK] 已生成 {len(map_data)} 个省份的地图数据')
    return map_data


def generate_trend_data(db: Database, days: int = 30):
    """生成趋势数据（最近N天的趋势）"""
    print(f'正在生成最近 {days} 天的趋势数据...')
    
    now = datetime.now()
    trend_data = []
    
    for i in range(days):
        date = (now - timedelta(days=days - 1 - i)).strftime('%Y-%m-%d')
        # 生成趋势数据，使其有一定的波动性
        base_confirmed = random.randint(5, 15)
        base_suspected = random.randint(10, 25)
        base_recovered = random.randint(3, 12)
        
        # 添加一些随机波动
        confirmed_count = max(0, base_confirmed + random.randint(-3, 5))
        suspected_count = max(0, base_suspected + random.randint(-5, 8))
        recovered_count = max(0, base_recovered + random.randint(-2, 4))
        
        trend_data.append({
            'date': date,
            'confirmedCount': confirmed_count,
            'suspectedCount': suspected_count,
            'recoveredCount': recovered_count
        })
        db.create_trend_data(date, confirmed_count, suspected_count, recovered_count)
    
    print(f'[OK] 已生成 {len(trend_data)} 天的趋势数据')
    return trend_data


def generate_flow_statistics(db: Database, movements: list, periods: list = ['today', 'week', 'month']):
    """生成流动统计"""
    print('正在生成流动统计...')
    
    now = datetime.now()
    flow_statistics = []
    
    for period in periods:
        # 计算日期范围
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0)
        elif period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        else:
            start_date = datetime(2020, 1, 1)
        
        # 统计各地区的流动数量
        region_flows = {}
        for movement in movements:
            movement_time = datetime.strptime(movement['time'], '%Y-%m-%d %H:%M:%S')
            if movement_time >= start_date:
                from_region = movement['from']
                to_region = movement['to']
                
                # 统计出发地
                if from_region not in region_flows:
                    region_flows[from_region] = 0
                region_flows[from_region] += 1
                
                # 统计目的地
                if to_region not in region_flows:
                    region_flows[to_region] = 0
                region_flows[to_region] += 1
        
        # 如果没有流动记录，为每个地区生成随机数据
        if not region_flows:
            for region in REGIONS:
                region_flows[region] = random.randint(10, 50)
        
        # 保存到数据库
        flow_data = []
        for region, flow_count in region_flows.items():
            flow_data.append({
                'region': region,
                'flowCount': flow_count
            })
            db.create_flow_statistics(region, flow_count, period=period)
        
        flow_statistics.extend(flow_data)
        print(f'[OK] 已生成 {period} 周期的流动统计 ({len(flow_data)} 个地区)')
    
    return flow_statistics


def init_database(clear_existing: bool = False, people_count: int = 100, movements_count: int = 300):
    """初始化数据库
    
    Args:
        clear_existing: 是否清空现有数据
        people_count: 生成的人员数量
        movements_count: 生成的流动记录数量
    """
    print('=' * 50)
    print('开始初始化数据库...')
    print('=' * 50)
    
    db = Database()
    db.connect()
    
    try:
        # 清空现有数据（如果需要）
        if clear_existing:
            print('清空现有数据...')
            db.clear_all_data()
            print('[OK] 已清空现有数据')
        
        # 生成人员数据
        people = generate_people_data(db, people_count)
        
        # 生成流动记录（传入人员列表，避免查询数据库）
        movements = generate_movements_data(db, people, movements_count)
        
        # 根据人员数据同步地图数据（确保地图显示实际的人员分布）
        print('正在根据人员数据同步地图数据...')
        try:
            from map_sync import sync_map_data_from_people
            sync_map_data_from_people(db)
            map_data = db.get_map_data()
        except Exception as e:
            print(f'[WARN] 同步地图数据失败（可能内存不足）: {e}')
            map_data = []
        
        # 生成趋势数据（最近30天）
        try:
            trend_data = generate_trend_data(db, days=30)
        except Exception as e:
            print(f'[WARN] 生成趋势数据失败（可能内存不足）: {e}')
            trend_data = []
        
        # 生成流动统计
        try:
            flow_statistics = generate_flow_statistics(db, movements, periods=['today', 'week', 'month'])
        except Exception as e:
            print(f'[WARN] 生成流动统计失败（可能内存不足）: {e}')
            flow_statistics = []
        
        # 显示统计信息（如果查询失败，使用默认值）
        try:
            stats = db.get_stats()
        except Exception as e:
            print(f'[WARN] 获取统计信息失败（可能内存不足）: {e}')
            stats = {
                'totalPeople': len(people),
                'confirmedCases': 0,
                'activeRegions': 0,
                'todayMovements': 0
            }
        print('\n' + '=' * 50)
        print('数据库初始化完成！')
        print('=' * 50)
        print(f'人员总数: {stats["totalPeople"]}')
        print(f'确诊病例: {stats["confirmedCases"]}')
        print(f'活跃区域: {stats["activeRegions"]}')
        print(f'今日流动: {stats["todayMovements"]}')
        print(f'地图数据: {len(map_data)} 个省份')
        print(f'趋势数据: {len(trend_data)} 天')
        print(f'流动统计: {len(flow_statistics)} 条记录')
        print('=' * 50)
        
    except Exception as e:
        print(f'[ERROR] 初始化失败: {e}')
        raise
    finally:
        db.disconnect()


if __name__ == '__main__':
    import sys
    
    # 解析命令行参数
    clear = '--clear' in sys.argv or '-c' in sys.argv
    
    # 获取数量参数
    people_count = 8000
    movements_count = 16000
    
    for i, arg in enumerate(sys.argv):
        if arg == '--people' and i + 1 < len(sys.argv):
            people_count = int(sys.argv[i + 1])
        elif arg == '--movements' and i + 1 < len(sys.argv):
            movements_count = int(sys.argv[i + 1])
    
    init_database(clear_existing=clear, people_count=people_count, movements_count=movements_count)

