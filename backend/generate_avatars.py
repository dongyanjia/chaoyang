"""
生成假头像图片
"""
from PIL import Image, ImageDraw, ImageFont
import os
import random

def generate_avatar(filename, size=200):
    """生成一个随机颜色的头像"""
    # 创建图像
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)
    
    # 随机背景颜色
    bg_color = (
        random.randint(100, 255),
        random.randint(100, 255),
        random.randint(100, 255)
    )
    
    # 绘制圆形背景
    margin = 10
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=bg_color,
        outline=(200, 200, 200),
        width=3
    )
    
    # 绘制简单的面部特征
    center = size // 2
    eye_y = center - 30
    eye_size = 15
    
    # 眼睛
    draw.ellipse(
        [center - 40 - eye_size//2, eye_y - eye_size//2,
         center - 40 + eye_size//2, eye_y + eye_size//2],
        fill=(50, 50, 50)
    )
    draw.ellipse(
        [center + 40 - eye_size//2, eye_y - eye_size//2,
         center + 40 + eye_size//2, eye_y + eye_size//2],
        fill=(50, 50, 50)
    )
    
    # 嘴巴
    draw.arc(
        [center - 30, center, center + 30, center + 40],
        start=0,
        end=180,
        fill=(50, 50, 50),
        width=3
    )
    
    # 保存
    avatars_dir = os.path.join(os.path.dirname(__file__), 'avatars')
    os.makedirs(avatars_dir, exist_ok=True)
    img.save(os.path.join(avatars_dir, filename), 'JPEG', quality=95)

if __name__ == '__main__':
    print('正在生成头像图片...')
    for i in range(1, 21):
        generate_avatar(f'avatar_{i}.jpg')
        print(f'已生成头像 {i}/20')
    print('头像生成完成！')

