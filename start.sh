#!/bin/bash

echo "===================================="
echo "全国流感人群流动监测系统"
echo "===================================="
echo ""

echo "[1/2] 启动后端服务..."
cd backend
python3 run.py &
BACKEND_PID=$!
sleep 3

echo "[2/2] 启动前端服务..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "===================================="
echo "服务启动完成！"
echo "前端地址: http://localhost:3000"
echo "后端地址: http://localhost:8000"
echo "===================================="
echo "按 Ctrl+C 停止服务"

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait

