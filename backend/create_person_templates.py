"""
创建人员档案导入模板文件
生成JSON、Excel和CSV格式的模板文件，用于工作区数据管理模块的数据导入
"""
import pandas as pd
import json
import os

# 创建模板目录
template_dir = 'templates'
os.makedirs(template_dir, exist_ok=True)

def create_json_template():
    """创建JSON模板文件"""
    json_template = [
        {
            "name": "张三",
            "idCard": "110101199001011234",
            "age": 30,
            "gender": "男",
            "occupation": "教师",
            "hometown": "北京市",
            "region": "北京市",
            "phone": "13800138000",
            "status": "正常",
            "nationality": "中国",
            "visaType": "",
            "institution": "",
            "tags": ["重点人员", "教师"],
            "educationHistory": [
                {
                    "school": "北京大学",
                    "degree": "本科",
                    "major": "计算机科学",
                    "startDate": "2010-09",
                    "endDate": "2014-06"
                }
            ],
            "workHistory": [
                {
                    "company": "北京市第一中学",
                    "position": "教师",
                    "description": "负责数学教学工作",
                    "startDate": "2014-09",
                    "endDate": "至今"
                }
            ],
            "socialMedia": [],
            "visitRecords": [
                {
                    "place": "上海市",
                    "date": "2024-01-15",
                    "purpose": "出差"
                }
            ],
            "flightRecords": [],
            "trainRecords": []
        }
    ]
    
    json_file = os.path.join(template_dir, 'person_template.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_template, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] 已创建JSON模板: {json_file}")
    return json_file

def create_excel_template():
    """创建Excel模板文件"""
    # 基础字段（必需字段）
    df_data = {
        'name': ['张三', '李四'],
        'idCard': ['110101199001011234', '110101199002021235'],
        'age': [30, 25],
        'gender': ['男', '女'],
        'occupation': ['教师', '医生'],
        'hometown': ['北京市', '上海市'],
        'region': ['北京市', '上海市'],
        'phone': ['13800138000', '13800138001'],
        'status': ['正常', '正常'],
        'nationality': ['中国', '中国'],
        'visaType': ['', ''],
        'institution': ['', ''],
        'tags': ['重点人员,教师', ''],
        'educationHistory': ['北京大学|本科|计算机科学|2010-09|2014-06', ''],
        'workHistory': ['北京市第一中学|教师|负责数学教学工作|2014-09|至今', ''],
        'visitRecords': ['上海市|2024-01-15|出差', ''],
        'flightRecords': ['', ''],
        'trainRecords': ['', '']
    }
    
    df = pd.DataFrame(df_data)
    excel_file = os.path.join(template_dir, 'person_template.xlsx')
    df.to_excel(excel_file, index=False, engine='openpyxl')
    
    print(f"[OK] 已创建Excel模板: {excel_file}")
    return excel_file

def create_csv_template():
    """创建CSV模板文件"""
    df_data = {
        'name': ['张三', '李四'],
        'idCard': ['110101199001011234', '110101199002021235'],
        'age': [30, 25],
        'gender': ['男', '女'],
        'occupation': ['教师', '医生'],
        'hometown': ['北京市', '上海市'],
        'region': ['北京市', '上海市'],
        'phone': ['13800138000', '13800138001'],
        'status': ['正常', '正常'],
        'nationality': ['中国', '中国'],
        'visaType': ['', ''],
        'institution': ['', ''],
        'tags': ['重点人员,教师', ''],
        'educationHistory': ['北京大学|本科|计算机科学|2010-09|2014-06', ''],
        'workHistory': ['北京市第一中学|教师|负责数学教学工作|2014-09|至今', ''],
        'visitRecords': ['上海市|2024-01-15|出差', ''],
        'flightRecords': ['', ''],
        'trainRecords': ['', '']
    }
    
    df = pd.DataFrame(df_data)
    csv_file = os.path.join(template_dir, 'person_template.csv')
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    
    print(f"[OK] 已创建CSV模板: {csv_file}")
    return csv_file

if __name__ == '__main__':
    print("正在创建人员档案导入模板文件...")
    print("=" * 60)
    
    create_json_template()
    create_excel_template()
    create_csv_template()
    
    print("=" * 60)
    print("所有模板文件创建完成！")
    print(f"模板文件位置: {os.path.abspath(template_dir)}")
    print("\n模板文件说明:")
    print("- JSON模板: 支持完整的嵌套结构（教育经历、工作经历等）")
    print("- Excel模板: 第一行为表头，复杂字段使用分隔符（|）")
    print("- CSV模板: 逗号分隔，第一行为表头，复杂字段使用分隔符（|）")
    print("\n必需字段: name（姓名）、idCard（身份证号）")
    print("可选字段: age、gender、occupation、hometown、region、phone、status等")

