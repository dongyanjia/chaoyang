#!/bin/bash
# Docker 快速启动脚本

set -e

echo "=========================================="
echo "全国流感人群流动监测系统 - Docker 启动脚本"
echo "=========================================="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: 未找到 Docker，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "错误: 未找到 Docker Compose，请先安装 Docker Compose"
    exit 1
fi

# 检查是否使用 docker compose (v2)
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo "1. 构建 Docker 镜像..."
$DOCKER_COMPOSE build

echo ""
echo "2. 启动所有服务..."
$DOCKER_COMPOSE up -d

echo ""
echo "3. 等待服务启动（30秒）..."
sleep 30

echo ""
echo "4. 检查服务状态..."
$DOCKER_COMPOSE ps

echo ""
echo "5. 初始化数据库表结构..."
$DOCKER_COMPOSE exec -T backend python init_doris_tables.py || echo "数据库初始化可能已存在，跳过"

echo ""
echo "=========================================="
echo "启动完成！"
echo "=========================================="
echo ""
echo "访问地址:"
echo "  前端: http://localhost"
echo "  后端API: http://localhost:8000"
echo "  Doris FE: http://localhost:8030"
echo ""
echo "常用命令:"
echo "  查看日志: $DOCKER_COMPOSE logs -f"
echo "  停止服务: $DOCKER_COMPOSE down"
echo "  查看状态: $DOCKER_COMPOSE ps"
echo ""
echo "初始化数据（可选）:"
echo "  初始化标签: $DOCKER_COMPOSE exec backend python init_tags.py"
echo "  初始化测试数据: $DOCKER_COMPOSE exec backend python init_database.py --people 100"
echo ""
