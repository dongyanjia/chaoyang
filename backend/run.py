"""
后端服务启动脚本

功能：
- 启动Flask后端服务
- 检查并生成头像文件（如果缺失）
- 配置服务端口和主机地址

使用方法：
    python run.py

服务配置：
- 端口：8000
- 主机：0.0.0.0（允许外部访问）
- 调试模式：开启（开发环境）

作者：系统开发团队
版本：1.0.0
"""
from app import app
import os

if __name__ == '__main__':
    # 确保头像目录存在，如果为空则生成默认头像
    avatars_dir = os.path.join(os.path.dirname(__file__), 'avatars')
    if not os.path.exists(avatars_dir) or len(os.listdir(avatars_dir)) == 0:
        print('检测到头像目录为空，正在生成头像...')
        try:
            from generate_avatars import generate_avatar
            os.makedirs(avatars_dir, exist_ok=True)
            # 生成20个默认头像
            for i in range(1, 21):
                generate_avatar(f'avatar_{i}.jpg')
            print('头像生成完成！')
        except Exception as e:
            print(f'生成头像失败: {e}')
    
    # 从环境变量读取配置
    flask_env = os.getenv('FLASK_ENV', 'development')
    debug_mode = flask_env == 'development' or os.getenv('FLASK_DEBUG', '0') == '1'
    port = int(os.getenv('PORT', 8000))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f'启动后端服务...')
    print(f'环境: {flask_env}')
    print(f'调试模式: {debug_mode}')
    print(f'后端API地址: http://{host}:{port}')
    
    # 启动Flask应用
    app.run(debug=debug_mode, port=port, host=host)

