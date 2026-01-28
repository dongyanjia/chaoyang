"""
初始化标签数据脚本
将前端默认标签导入到Doris数据库

使用方法:
    python init_tags.py
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from database import Database
from tag_service import get_tag_service

def init_tags():
    """初始化标签数据"""
    print("=" * 60)
    print("初始化标签数据")
    print("=" * 60)
    print()
    
    try:
        # 连接数据库
        print("[1/3] 连接数据库...")
        db = Database()
        db.connect()
        print("[OK] 数据库连接成功")
        print()
        
        # 获取标签服务
        print("[2/3] 初始化标签服务...")
        tag_service = get_tag_service(db)
        print("[OK] 标签服务初始化成功")
        print()
        
        # 导入标签
        print("[3/3] 导入标签数据...")
        print(f"  标签分类数量: {len(DEFAULT_TAG_CATEGORIES)}")
        
        # 统计标签总数
        total_tags = 0
        for category in DEFAULT_TAG_CATEGORIES:
            for sub_category in category.get('children', []):
                total_tags += len(sub_category.get('tags', []))
        print(f"  标签总数: {total_tags}")
        print()
        
        # 保存标签（清空旧标签）
        count = tag_service.extract_and_save_tags(DEFAULT_TAG_CATEGORIES, clear_existing=True)
        
        print()
        print("=" * 60)
        print(f"[OK] 标签初始化完成！")
        print(f"  成功导入 {count} 个标签")
        print("=" * 60)
        
        # 验证导入结果
        print()
        print("验证导入结果...")
        all_tags = tag_service.get_all_tags()
        print(f"  数据库中的标签分类数: {len(all_tags)}")
        
        db_tags_count = 0
        for cat in all_tags:
            for sub in cat.get('children', []):
                db_tags_count += len(sub.get('tags', []))
        print(f"  数据库中的标签总数: {db_tags_count}")
        
        if db_tags_count == count:
            print("[OK] 验证通过：标签数量匹配")
        else:
            print(f"[WARN] 警告：标签数量不匹配（导入: {count}, 查询: {db_tags_count}）")
        
    except Exception as e:
        print()
        print("=" * 60)
        print("[ERROR] 标签初始化失败！")
        print(f"  错误: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    # 注意：这里需要直接导入前端配置，但前端是JS文件
    # 我们需要手动定义默认标签结构
    DEFAULT_TAG_CATEGORIES = [
        {
            'id': 1,
            'name': '基本信息',
            'children': [
                {
                    'id': 1,
                    'name': '年龄',
                    'tags': ['18-25岁', '26-35岁', '36-45岁', '46-55岁', '56-65岁', '65岁以上']
                },
                {
                    'id': 2,
                    'name': '性别',
                    'tags': ['男', '女']
                },
                {
                    'id': 3,
                    'name': '职业',
                    'tags': ['外交官', '翻译', '导游', '外贸', '空乘', '飞行员', '船员', '记者', '商务', '学生',
                             '教授', '医生', '工程师', '艺术家', '音乐家', '运动员', '国际咨询', '跨国公司高管', '国际律师', '国际组织工作人员']
                },
                {
                    'id': 4,
                    'name': '籍贯',
                    'tags': ['北京市', '上海市', '天津市', '重庆市', '广东省', '浙江省', '江苏省', '山东省', '四川省', '湖北省', '河南省', '湖南省', '安徽省', '福建省', '陕西省', '辽宁省', '河北省', '江西省', '云南省', '广西壮族自治区', '贵州省', '山西省', '内蒙古自治区', '吉林省', '黑龙江省', '新疆维吾尔自治区', '甘肃省', '海南省', '宁夏回族自治区', '青海省', '西藏自治区', '香港特别行政区', '澳门特别行政区', '台湾省']
                },
                {
                    'id': 5,
                    'name': '状态',
                    'tags': ['正常', '疑似', '确诊', '康复']
                },
                {
                    'id': 6,
                    'name': '签证类型',
                    'tags': ['旅游签证', '工作签证', '学生签证', '商务签证', '探亲签证', '访问签证', 
                             '过境签证', '居留签证', '投资签证', '技术签证', '文化交流签证', '医疗签证',
                             '实习签证', '记者签证', '外交签证', '公务签证', '其他签证']
                },
                {
                    'id': 7,
                    'name': '机构',
                    'tags': ['美国疾病控制与预防中心', '英国国家医疗服务体系', '法国公共卫生署', '德国罗伯特·科赫研究所', '日本国立感染症研究所', '韩国疾病管理本部', '俄罗斯联邦消费者权益保护局', '印度国家疾病控制中心', '澳大利亚卫生部', '加拿大公共卫生署', '意大利国家卫生研究所', '西班牙卫生部', '巴西卫生部', '墨西哥卫生部', '世界卫生组织']
                }
            ]
        },
        {
            'id': 2,
            'name': '到访信息',
            'children': [
                {
                    'id': 1,
                    'name': '到访省份',
                    'tags': ['北京市', '上海市', '天津市', '重庆市', '广东省', '浙江省', '江苏省', '山东省', '四川省', '湖北省', '河南省', '湖南省', '安徽省', '福建省', '陕西省', '辽宁省', '河北省', '江西省', '云南省', '广西壮族自治区', '贵州省', '山西省', '内蒙古自治区', '吉林省', '黑龙江省', '新疆维吾尔自治区', '甘肃省', '海南省', '宁夏回族自治区', '青海省', '西藏自治区', '香港特别行政区', '澳门特别行政区', '台湾省']
                }
            ]
        },
        {
            'id': 3,
            'name': '民航铁路动态',
            'children': [
                {
                    'id': 1,
                    'name': '航班',
                    'tags': ['中国国际航空', '中国东方航空', '中国南方航空', '海南航空', '深圳航空']
                },
                {
                    'id': 2,
                    'name': '铁路',
                    'tags': ['高铁', '动车', '普通列车']
                }
            ]
        },
        {
            'id': 4,
            'name': '社交媒体动态',
            'children': [
                {
                    'id': 1,
                    'name': '平台类型',
                    'tags': ['微信', '微博', '抖音', 'QQ', '小红书', '知乎']
                }
            ]
        }
    ]
    
    success = init_tags()
    sys.exit(0 if success else 1)
