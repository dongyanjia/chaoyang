"""
检查后端服务是否正常运行
"""
import sys
import socket

def check_port(host='localhost', port=8000):
    """检查端口是否被占用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

if __name__ == '__main__':
    print("检查后端服务状态...")
    print(f"端口 8000 是否被占用: {'是' if check_port() else '否'}")
    
    if check_port():
        print("\n✓ 后端服务正在运行")
        print("可以访问: http://localhost:8000")
        print("API文档: http://localhost:8000/")
    else:
        print("\n✗ 后端服务未运行")
        print("请运行: python run.py")

