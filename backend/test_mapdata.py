"""测试地图数据API"""
from app import app
import json

with app.test_client() as client:
    response = client.get('/api/stats')
    data = json.loads(response.data)
    
    print('=' * 50)
    print('API响应测试')
    print('=' * 50)
    print(f'状态码: {response.status_code}')
    print(f'返回的键: {list(data.keys())}')
    print(f'mapData是否存在: {"mapData" in data}')
    
    if 'mapData' in data:
        map_data = data['mapData']
        print(f'mapData数量: {len(map_data)}')
        print(f'mapData前5个:')
        for item in map_data[:5]:
            print(f'  - {item}')
    else:
        print('错误: mapData字段不存在！')
    
    print('=' * 50)

