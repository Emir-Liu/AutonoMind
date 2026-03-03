# AutonoMind 快速启动指南

## 前置要求

- Python 3.10+
- Docker (可选，用于启动基础服务)
- Git

## 启动步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd AutonoMind/code
```

### 2. 创建虚拟环境

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置必要的参数
# - OPENAI_API_KEY (必须)
# - OPENAI_API_BASE (必须，使用OpenAI或其他兼容服务)
# - OPENAI_MODEL (必须)
```

### 5. 启动基础服务（可选）

如果你已安装Docker，可以使用docker-compose启动基础服务：

```bash
docker-compose up -d
```

这将启动：
- PostgreSQL (端口 5432)
- Redis (端口 6379)
- Qdrant (端口 6333)
- RabbitMQ (端口 5672, 15672)
- MinIO (端口 9000, 9001)

### 6. 启动应用

**方式1: 使用启动脚本**

**Linux/macOS:**
```bash
bash start.sh
```

**Windows:**
```cmd
start.bat
```

**方式2: 手动启动**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 7. 验证启动

访问以下URL验证服务是否正常运行：

- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health
- 系统信息: http://localhost:8000/api/v1/system/info

## 开发模式

开发模式下，应用会自动重载代码变更。

## 生产部署

生产部署请参考 `../docs/development/部署指南.md`

## 常见问题

### 1. 数据库连接失败

确保PostgreSQL正在运行，并检查 `.env` 中的数据库配置。

### 2. Redis连接失败

确保Redis正在运行，或设置环境变量 `REDIS_ENABLED=false` 禁用缓存。

### 3. LLM调用失败

检查 `.env` 中的LLM配置：
- `OPENAI_API_KEY` 是否正确
- `OPENAI_API_BASE` 是否正确
- `OPENAI_MODEL` 是否可用

## 目录结构

```
code/
├── api/          # API层
├── func/         # 业务逻辑层
├── core/         # 核心算法层
├── utils/        # 工具层
├── models/       # 数据模型
├── config.py     # 配置
├── main.py       # 应用入口
└── requirements.txt
```

## 下一步

- 阅读 `../docs/` 目录下的设计文档
- 查看API文档: http://localhost:8000/docs
- 开始开发新功能
