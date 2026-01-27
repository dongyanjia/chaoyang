"""
地图数据与人员数据同步工具
实现地图数据和人员数据的双向同步

主要功能：
- 根据人员数据更新地图数据（统计各省份人数）
- 根据地图数据补充人员数据（如果地图人数大于实际人数）
- 处理地区到省份的映射关系
- 确保地图数据和人员数据的一致性

使用场景：
- 人员数据更新后，同步更新地图数据
- 地图数据更新后，补充相应的人员数据
- 系统初始化时，确保数据一致性

作者：系统开发团队
版本：1.0.0
"""
import random
from typing import Dict, List
from faker import Faker
from database import Database
from datetime import datetime, timedelta

# 初始化Faker库
fake = Faker('zh_CN')

# 地区到省份的映射关系 - 覆盖所有34个省份
REGION_TO_PROVINCE = {
    # 直辖市
    '北京': '北京市',
    '上海': '上海市',
    '天津': '天津市',
    '重庆': '重庆市',
    # 广东省
    '广州': '广东省', '深圳': '广东省', '珠海': '广东省', '佛山': '广东省', '东莞': '广东省', '中山': '广东省',
    # 浙江省
    '杭州': '浙江省', '宁波': '浙江省', '温州': '浙江省', '嘉兴': '浙江省', '绍兴': '浙江省',
    # 江苏省
    '南京': '江苏省', '苏州': '江苏省', '无锡': '江苏省', '常州': '江苏省', '徐州': '江苏省',
    # 山东省
    '济南': '山东省', '青岛': '山东省', '烟台': '山东省', '潍坊': '山东省', '临沂': '山东省',
    # 四川省
    '成都': '四川省', '绵阳': '四川省', '德阳': '四川省', '南充': '四川省', '宜宾': '四川省',
    # 湖北省
    '武汉': '湖北省', '襄阳': '湖北省', '宜昌': '湖北省', '荆州': '湖北省', '黄冈': '湖北省',
    # 河南省
    '郑州': '河南省', '洛阳': '河南省', '南阳': '河南省', '新乡': '河南省', '商丘': '河南省',
    # 湖南省
    '长沙': '湖南省', '株洲': '湖南省', '湘潭': '湖南省', '衡阳': '湖南省', '岳阳': '湖南省',
    # 安徽省
    '合肥': '安徽省', '芜湖': '安徽省', '蚌埠': '安徽省', '淮南': '安徽省', '马鞍山': '安徽省',
    # 福建省
    '福州': '福建省', '厦门': '福建省', '泉州': '福建省', '漳州': '福建省', '莆田': '福建省',
    # 陕西省
    '西安': '陕西省', '宝鸡': '陕西省', '咸阳': '陕西省', '渭南': '陕西省', '汉中': '陕西省',
    # 辽宁省
    '沈阳': '辽宁省', '大连': '辽宁省', '鞍山': '辽宁省', '抚顺': '辽宁省', '本溪': '辽宁省',
    # 河北省
    '石家庄': '河北省', '唐山': '河北省', '保定': '河北省', '邯郸': '河北省', '秦皇岛': '河北省',
    # 江西省
    '南昌': '江西省', '赣州': '江西省', '九江': '江西省', '上饶': '江西省', '宜春': '江西省',
    # 云南省
    '昆明': '云南省', '曲靖': '云南省', '玉溪': '云南省', '大理': '云南省', '红河': '云南省',
    # 广西壮族自治区
    '南宁': '广西壮族自治区', '桂林': '广西壮族自治区', '柳州': '广西壮族自治区', '北海': '广西壮族自治区', '梧州': '广西壮族自治区',
    # 贵州省
    '贵阳': '贵州省', '遵义': '贵州省', '六盘水': '贵州省', '安顺': '贵州省', '毕节': '贵州省',
    # 山西省
    '太原': '山西省', '大同': '山西省', '运城': '山西省', '临汾': '山西省', '长治': '山西省',
    # 内蒙古自治区
    '呼和浩特': '内蒙古自治区', '包头': '内蒙古自治区', '赤峰': '内蒙古自治区', '鄂尔多斯': '内蒙古自治区', '通辽': '内蒙古自治区',
    # 吉林省
    '长春': '吉林省', '吉林': '吉林省', '四平': '吉林省', '松原': '吉林省', '通化': '吉林省',
    # 黑龙江省
    '哈尔滨': '黑龙江省', '齐齐哈尔': '黑龙江省', '大庆': '黑龙江省', '牡丹江': '黑龙江省', '佳木斯': '黑龙江省',
    # 新疆维吾尔自治区
    '乌鲁木齐': '新疆维吾尔自治区', '克拉玛依': '新疆维吾尔自治区', '石河子': '新疆维吾尔自治区', '库尔勒': '新疆维吾尔自治区', '伊宁': '新疆维吾尔自治区',
    # 甘肃省
    '兰州': '甘肃省', '天水': '甘肃省', '酒泉': '甘肃省', '张掖': '甘肃省', '武威': '甘肃省',
    # 海南省
    '海口': '海南省', '三亚': '海南省', '儋州': '海南省', '琼海': '海南省', '文昌': '海南省',
    # 宁夏回族自治区
    '银川': '宁夏回族自治区', '石嘴山': '宁夏回族自治区', '吴忠': '宁夏回族自治区', '固原': '宁夏回族自治区', '中卫': '宁夏回族自治区',
    # 青海省
    '西宁': '青海省', '海东': '青海省', '格尔木': '青海省', '德令哈': '青海省', '玉树': '青海省',
    # 西藏自治区
    '拉萨': '西藏自治区', '日喀则': '西藏自治区', '昌都': '西藏自治区', '林芝': '西藏自治区', '那曲': '西藏自治区',
    # 香港特别行政区
    '香港': '香港特别行政区',
    # 澳门特别行政区
    '澳门': '澳门特别行政区',
    # 台湾省
    '台北': '台湾省', '高雄': '台湾省', '台中': '台湾省', '台南': '台湾省', '新北': '台湾省'
}

# 省份列表（用于地图数据）
PROVINCES = [
    '北京市', '上海市', '天津市', '重庆市',
    '广东省', '浙江省', '江苏省', '山东省', '四川省', '湖北省', '河南省', '湖南省',
    '安徽省', '福建省', '陕西省', '辽宁省', '河北省', '江西省', '云南省', '广西壮族自治区',
    '贵州省', '山西省', '内蒙古自治区', '吉林省', '黑龙江省', '新疆维吾尔自治区',
    '甘肃省', '海南省', '宁夏回族自治区', '青海省', '西藏自治区',
    '香港特别行政区', '澳门特别行政区', '台湾省'
]

# 状态列表
STATUSES = ['正常', '疑似', '确诊', '康复']
GENDERS = ['男', '女']
OCCUPATIONS = ['教师', '医生', '工程师', '学生', '公务员', '商人', '工人', '农民', '自由职业', '退休']


def get_province_from_region(region: str) -> str:
    """根据地区获取对应的省份"""
    return REGION_TO_PROVINCE.get(region, '未知省份')


def sync_map_data_from_people(db: Database):
    """根据人员数据同步地图数据"""
    """统计每个省份的实际人员数量，并更新地图数据"""
    people = db.get_people()
    
    # 统计每个省份的人员数量（使用户籍字段）
    province_counts = {}
    for person in people:
        # 优先使用hometown（籍贯），如果没有则使用region转换
        hometown = person.get('hometown', '')
        if hometown:
            province = hometown
        else:
            region = person.get('region', '')
            province = get_province_from_region(region)
        if province and province != '未知省份':
            province_counts[province] = province_counts.get(province, 0) + 1
    
    # 更新地图数据
    for province in PROVINCES:
        count = province_counts.get(province, 0)
        db.update_map_data(province, count)
    
    print(f'✓ 已同步地图数据，共更新 {len(province_counts)} 个省份')
    return province_counts


def sync_people_from_map_data(db: Database, target_province: str = None, target_count: int = None):
    """根据地图数据补充人员数据"""
    """如果某个省份的地图人数大于实际人员数，则补充相应的人员"""
    map_data = db.get_map_data()
    people = db.get_people()
    
    # 统计当前每个省份的实际人员数量（使用户籍字段）
    current_province_counts = {}
    for person in people:
        # 优先使用hometown（籍贯），如果没有则使用region转换
        hometown = person.get('hometown', '')
        if hometown:
            province = hometown
        else:
            region = person.get('region', '')
            province = get_province_from_region(region)
        if province and province != '未知省份':
            current_province_counts[province] = current_province_counts.get(province, 0) + 1
    
    # 获取省份对应的地区列表
    province_to_regions = {}
    for region, province in REGION_TO_PROVINCE.items():
        if province not in province_to_regions:
            province_to_regions[province] = []
        province_to_regions[province].append(region)
    
    added_count = 0
    
    # 遍历地图数据
    for map_item in map_data:
        province = map_item['name']
        map_target_count = map_item['value']
        current_count = current_province_counts.get(province, 0)
        
        # 如果目标数量大于当前数量，需要补充人员
        if map_target_count > current_count:
            need_add = map_target_count - current_count
            
            # 获取该省份对应的地区列表
            regions = province_to_regions.get(province, [])
            if not regions:
                # 如果没有对应的地区，使用省份名称作为地区
                regions = [province]
            
            # 为每个需要补充的人员生成数据
            for i in range(need_add):
                region = random.choice(regions)
                age = random.randint(18, 80)
                gender = random.choice(GENDERS)
                occupation = random.choice(OCCUPATIONS)
                status = random.choice(STATUSES)
                
                # 生成人员数据（基础信息）
                person_data = {
                    'name': fake.name(),
                    'idCard': fake.ssn(),
                    'region': region,  # 保留region用于兼容
                    'age': age,
                    'phone': fake.phone_number(),
                    'status': status,
                    'avatar': f'/api/avatars/avatar_{random.randint(1, 20)}.jpg',
                    'lastUpdate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'gender': gender,
                    'occupation': occupation,
                    'hometown': province,  # 使用省份作为籍贯
                    'tags': [occupation, f'{province}人'],
                    'educationHistory': [],
                    'workHistory': [],
                    'socialMedia': [],
                    'visitRecords': [],
                    'flightRecords': [],
                    'trainRecords': []
                }
                
                # 创建人员
                new_person = db.create_person(person_data)
                
                # 为新创建的人员生成扩展信息
                try:
                    from update_people_data import (
                        generate_education_history,
                        generate_work_history,
                        generate_social_media,
                        generate_visit_records,
                        generate_flight_records,
                        generate_train_records
                    )
                    
                    # 生成扩展信息
                    update_data = {
                        'name': new_person.get('name'),
                        'idCard': new_person.get('idCard'),
                        'region': region,  # 保留region用于兼容
                        'age': age,
                        'phone': new_person.get('phone'),
                        'status': status,
                        'avatar': new_person.get('avatar'),
                        'gender': gender,
                        'occupation': occupation,
                        'hometown': province,  # 使用省份作为籍贯
                        'tags': person_data['tags'],
                        'educationHistory': generate_education_history(age),
                        'workHistory': generate_work_history(age, occupation),
                        'socialMedia': generate_social_media(age),
                        'visitRecords': generate_visit_records(region),
                        'flightRecords': generate_flight_records(region),
                        'trainRecords': generate_train_records(region)
                    }
                    
                    # 更新人员信息
                    db.update_person(new_person['id'], update_data)
                except Exception as e:
                    print(f'生成扩展信息失败: {e}')
                
                added_count += 1
    
    if added_count > 0:
        print(f'✓ 已根据地图数据补充 {added_count} 个人员')
    
    return added_count


def adjust_people_by_map_data(db: Database):
    """根据地图数据调整人员数据（删除多余的人员）"""
    """如果某个省份的实际人员数大于地图人数，则删除多余的人员"""
    map_data = db.get_map_data()
    people = db.get_people()
    
    # 统计当前每个省份的实际人员数量（使用户籍字段）
    province_people = {}
    for person in people:
        # 优先使用hometown（籍贯），如果没有则使用region转换
        hometown = person.get('hometown', '')
        if hometown:
            province = hometown
        else:
            region = person.get('region', '')
            province = get_province_from_region(region)
        if province and province != '未知省份':
            if province not in province_people:
                province_people[province] = []
            province_people[province].append(person)
    
    deleted_count = 0
    
    # 创建地图数据的字典
    map_data_dict = {item['name']: item['value'] for item in map_data}
    
    # 遍历每个省份
    for province, person_list in province_people.items():
        target_count = map_data_dict.get(province, 0)
        current_count = len(person_list)
        
        # 如果当前数量大于目标数量，需要删除多余的人员
        if current_count > target_count:
            need_delete = current_count - target_count
            
            # 随机选择要删除的人员（优先删除状态为"正常"的人员）
            person_list.sort(key=lambda p: 0 if p.get('status') == '正常' else 1)
            
            for i in range(min(need_delete, len(person_list))):
                person = person_list[i]
                db.delete_person(person['id'])
                deleted_count += 1
    
    if deleted_count > 0:
        print(f'✓ 已根据地图数据删除 {deleted_count} 个多余人员')
    
    return deleted_count


def full_sync(db: Database):
    """完整同步：先根据人员数据更新地图数据，再根据地图数据补充人员"""
    print('开始完整同步地图数据和人员数据...')
    
    # 第一步：根据人员数据同步地图数据
    sync_map_data_from_people(db)
    
    # 第二步：根据地图数据补充人员
    sync_people_from_map_data(db)
    
    # 第三步：根据地图数据调整人员（删除多余的）
    adjust_people_by_map_data(db)
    
    print('✓ 完整同步完成')


if __name__ == '__main__':
    # 测试同步功能
    db = Database()
    db.connect()
    
    try:
        full_sync(db)
    finally:
        db.disconnect()

