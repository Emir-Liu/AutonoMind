#!/bin/bash

# AutonoMind 启动脚本

echo "Starting AutonoMind..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# 激活虚拟环境
echo "Activating virtual environment..."
source venv/bin/activate

# 安装依赖
echo "Installing dependencies..."
pip install -r requirements.txt

# 复制环境变量配置
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please configure .env file with your settings"
    exit 1
fi

# 启动服务
echo "Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
