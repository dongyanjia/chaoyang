"""
测试后端API是否正常工作
"""
import requests
import json

BASE_URL = 'http://localhost:8000'

def test_api():
    print("=" * 50)
    print("测试后端API")
    print("=" * 50)
    
    # 测试根路由
    try:
        print("\n1. 测试根路由 /")
        response = requests.get(f"{BASE_URL}/")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 测试stats接口
    try:
        print("\n2. 测试 /api/stats")
        response = requests.get(f"{BASE_URL}/api/stats")
        print(f"   状态码: {response.status_code}")
        data = response.json()
        print(f"   统计数据: {data.get('stats', {})}")
        print(f"   地图数据数量: {len(data.get('mapData', []))}")
        if data.get('mapData'):
            print(f"   地图数据示例: {data.get('mapData')[:3]}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 测试people接口
    try:
        print("\n3. 测试 /api/people")
        response = requests.get(f"{BASE_URL}/api/people")
        print(f"   状态码: {response.status_code}")
        print(f"   人员数量: {len(response.json())}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == '__main__':
    test_api()

