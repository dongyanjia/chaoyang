# Makefile for Docker operations

.PHONY: help build up down restart logs clean init-db init-tags test

help: ## 显示帮助信息
	@echo "可用命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

build: ## 构建所有镜像
	docker-compose build

build-no-cache: ## 强制重新构建所有镜像（不使用缓存）
	docker-compose build --no-cache

up: ## 启动所有服务
	docker-compose up -d

up-dev: ## 启动开发模式
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

down: ## 停止所有服务
	docker-compose down

down-v: ## 停止并删除数据卷
	docker-compose down -v

restart: ## 重启所有服务
	docker-compose restart

logs: ## 查看所有服务日志
	docker-compose logs -f

logs-backend: ## 查看后端日志
	docker-compose logs -f backend

logs-frontend: ## 查看前端日志
	docker-compose logs -f frontend

logs-doris: ## 查看Doris日志
	docker-compose logs -f doris-fe doris-be

ps: ## 查看服务状态
	docker-compose ps

exec-backend: ## 进入后端容器
	docker-compose exec backend bash

exec-frontend: ## 进入前端容器
	docker-compose exec frontend sh

init-db: ## 初始化数据库表结构
	docker-compose exec backend python init_doris_tables.py

init-tags: ## 初始化标签数据
	docker-compose exec backend python init_tags.py

init-data: ## 初始化测试数据（100条）
	docker-compose exec backend python init_database.py --people 100

clean: ## 清理未使用的Docker资源
	docker system prune -f

clean-all: ## 清理所有未使用的资源（包括镜像）
	docker system prune -a -f

test: ## 运行测试
	docker-compose exec backend python test_tags_api.py

status: ## 检查服务健康状态
	@echo "=== 服务状态 ==="
	@docker-compose ps
	@echo ""
	@echo "=== 健康检查 ==="
	@echo -n "前端: "
	@curl -s -o /dev/null -w "%{http_code}" http://localhost/ || echo "无法连接"
	@echo ""
	@echo -n "后端: "
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/stats || echo "无法连接"
	@echo ""
	@echo -n "Doris FE: "
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:8030/api/bootstrap || echo "无法连接"
	@echo ""
