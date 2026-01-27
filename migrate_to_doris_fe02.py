"""
使用 doris-fe-02 (端口 9032) 进行迁移

如果 doris-fe-01 未启动，可以使用已运行的 doris-fe-02
"""
import os
import sys

# 设置环境变量使用 FE-02
os.environ['DORIS_PORT'] = '9032'

# 导入并运行迁移脚本
from migrate_to_doris import main

if __name__ == '__main__':
    print('=' * 60)
    print('使用 doris-fe-02 (端口 9032) 进行迁移')
    print('=' * 60)
    main()
