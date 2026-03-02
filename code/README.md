# AutonoMind Backend Code

## 项目结构

```
code/
├── api/                # API层 - 接口定义、参数验证、响应封装
│   ├── v1/            # API版本v1
│   │   ├── __init__.py
│   │   ├── agents/    # 智能体相关接口
│   │   ├── sessions/  # 会话相关接口
│   │   ├── knowledge/ # 知识库相关接口
│   │   └── system/    # 系统相关接口
│   └── __init__.py
├── func/               # Func层 - 业务逻辑组装、任务编排、状态管理
│   ├── agents/        # 智能体业务逻辑
│   ├── sessions/      # 会话业务逻辑
│   ├── knowledge/     # 知识库业务逻辑
│   └── __init__.py
├── core/               # Core层 - 核心算法实现、抽象基类、复杂业务逻辑
│   ├── agents/        # 智能体核心实现
│   ├── knowledge/     # 知识检索核心
│   ├── decision/      # 决策引擎核心
│   ├── tool/          # 工具执行核心
│   ├── evolution/     # 进化引擎核心
│   └── __init__.py
├── utils/              # Utils层 - 通用工具类、基础设施、第三方封装
│   ├── database.py    # 数据库工具
│   ├── cache.py       # 缓存工具
│   ├── queue.py       # 消息队列工具
│   ├── storage.py     # 存储工具
│   ├── logger.py      # 日志工具
│   ├── config.py      # 配置工具
│   ├── llm.py         # LLM工具
│   └── __init__.py
├── models/             # 数据模型
│   ├── database.py    # 数据库模型
│   ├── schemas/       # Pydantic模型
│   └── __init__.py
├── main.py            # FastAPI应用主入口
├── config.py          # 全局配置
└── requirements.txt   # 依赖包
```

## 分层架构说明

### API层
- 职责: 接口定义、参数验证、响应封装
- 包含: 路由定义、请求模型、响应模型、异常处理

### Func层
- 职责: 业务逻辑组装、任务编排、状态管理
- 包含: 业务流程、任务协调、状态转换

### Core层
- 职责: 核心算法实现、抽象基类、复杂业务逻辑
- 包含: 抽象接口、核心算法、业务规则

### Utils层
- 职责: 通用工具类、基础设施、第三方封装
- 包含: 数据库操作、缓存、消息队列、存储、日志等
