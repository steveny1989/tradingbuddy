#!/bin/bash
# 启动后端Flask服务

echo "启动TradingBuddy后端服务..."

# 设置环境变量
export FLASK_APP=src/web/app.py
export FLASK_ENV=development

# 启动Flask服务
python3 -m flask run --host=0.0.0.0 --port=5000
