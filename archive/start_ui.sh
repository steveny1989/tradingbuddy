#!/bin/bash

# TradingBuddy UI 启动脚本

echo "🚀 启动 TradingBuddy UI 系统..."

# 检查Python依赖
echo "📦 检查Python依赖..."
pip install -r requirements.txt

# 启动后端服务器
echo "🔧 启动后端API服务器 (端口 5000)..."
cd src/web && python app.py &
BACKEND_PID=$!

# 等待后端启动
sleep 2

# 检查前端依赖
echo "📦 检查前端依赖..."
cd ../../frontend
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

# 启动前端开发服务器
echo "🎨 启动前端开发服务器 (端口 3000)..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ TradingBuddy UI 已启动！"
echo ""
echo "📍 前端地址: http://localhost:3000"
echo "📍 后端API: http://localhost:5000"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
