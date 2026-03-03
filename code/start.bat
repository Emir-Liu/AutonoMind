@echo off

REM AutonoMind 启动脚本 (Windows)

echo Starting AutonoMind...

REM 检查虚拟环境
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM 激活虚拟环境
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM 安装依赖
echo Installing dependencies...
pip install -r requirements.txt

REM 复制环境变量配置
if not exist ".env" (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo Please configure .env file with your settings
    pause
    exit /b 1
)

REM 启动服务
echo Starting FastAPI server...
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
