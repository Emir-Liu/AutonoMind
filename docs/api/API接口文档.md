# AutonoMind API 接口文档

## 1. 文档信息

| 字段 | 内容 |
|------|------|
| **文档名称** | AutonoMind API 接口文档 |
| **版本** | v1.0 |
| **创建日期** | 2026-03-02 |
| **基准 URL** | `http://localhost:8000/api/v1` |

---

## 2. 目录

1. [概述](#3-概述)
2. [认证](#4-认证)
3. [通用参数](#5-通用参数)
4. [响应格式](#6-响应格式)
5. [错误码](#7-错误码)
6. [API 接口](#8-api-接口)
   - [会话管理](#81-会话管理)
   - [消息管理](#82-消息管理)
   - [知识库管理](#83-知识库管理)
   - [工具管理](#84-工具管理)
   - [执行日志](#85-执行日志)

---

## 3. 概述

AutonoMind API 提供 RESTful 接口,支持以下核心功能:

- **会话管理**: 创建、查询、删除 Agent 会话
- **消息管理**: 发送消息、获取历史记录
- **知识库管理**: 添加、删除、更新、检索知识
- **工具管理**: 注册、查询、启用/禁用工具
- **执行日志**: 查询 Agent 执行过程和日志

---

## 4. 认证

### 4.1 认证方式

AutonoMind 支持两种认证方式:

#### JWT Token (推荐)

```http
Authorization: Bearer <your_jwt_token>
```

#### API Key

```http
X-API-Key: <your_api_key>
```

### 4.2 获取 Token

#### 登录获取 JWT Token

**请求**:
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400
  }
}
```

---

## 5. 通用参数

### 5.1 请求头

| 头 | 必需 | 说明 |
|-----|------|------|
| `Authorization` | 是 | JWT Token 或 API Key |
| `Content-Type` | 是 | `application/json` |
| `X-Request-ID` | 否 | 请求 ID,用于追踪 |

### 5.2 查询参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `page` | int | 1 | 页码 |
| `page_size` | int | 20 | 每页数量 |
| `sort_by` | string | created_at | 排序字段 |
| `order` | string | desc | 排序方向 (`asc`/`desc`) |

---

## 6. 响应格式

### 6.1 成功响应

```json
{
  "success": true,
  "data": {
    // 响应数据
  },
  "meta": {
    "timestamp": "2026-03-02T10:00:00Z",
    "request_id": "req_123456"
  }
}
```

### 6.2 分页响应

```json
{
  "success": true,
  "data": [
    // 数据列表
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

### 6.3 错误响应

```json
{
  "success": false,
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "参数验证失败",
    "details": {
      "query": ["不能为空"]
    }
  },
  "meta": {
    "timestamp": "2026-03-02T10:00:00Z",
    "request_id": "req_123456"
  }
}
```

---

## 7. 错误码

| 错误码 | HTTP 状态 | 说明 |
|--------|-----------|------|
| `UNAUTHORIZED` | 401 | 未授权或 Token 无效 |
| `FORBIDDEN` | 403 | 无权限访问 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `INVALID_PARAMETER` | 400 | 参数验证失败 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |
| `RATE_LIMIT_EXCEEDED` | 429 | 超出速率限制 |

---

## 8. API 接口

### 8.1 会话管理

#### 8.1.1 创建会话

创建一个新的 Agent 会话。

**请求**:
```http
POST /api/v1/sessions
Content-Type: application/json

{
  "user_id": "user_123",
  "agent_config": {
    "llm_provider": "openai",
    "llm_model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "metadata": {
    "source": "web",
    "tags": ["support"]
  }
}
```

**参数说明**:

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `user_id` | string | 是 | 用户 ID |
| `agent_config` | object | 否 | Agent 配置 |
| `agent_config.llm_provider` | string | 否 | LLM 提供商 |
| `agent_config.llm_model` | string | 否 | LLM 模型 |
| `agent_config.temperature` | float | 否 | 温度参数(0-1) |
| `agent_config.max_tokens` | int | 否 | 最大 token 数 |
| `metadata` | object | 否 | 元数据 |

**响应**:
```json
{
  "success": true,
  "data": {
    "session_id": "sess_abc123",
    "user_id": "user_123",
    "status": "active",
    "created_at": "2026-03-02T10:00:00Z",
    "agent_config": {
      "llm_provider": "openai",
      "llm_model": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 2000
    }
  }
}
```

---

#### 8.1.2 获取会话信息

获取指定会话的详细信息。

**请求**:
```http
GET /api/v1/sessions/{session_id}
```

**参数说明**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `session_id` | string | 是 | 会话 ID |

**响应**:
```json
{
  "success": true,
  "data": {
    "session_id": "sess_abc123",
    "user_id": "user_123",
    "status": "active",
    "message_count": 15,
    "created_at": "2026-03-02T10:00:00Z",
    "updated_at": "2026-03-02T11:30:00Z"
  }
}
```

---

#### 8.1.3 列出会话

获取用户的所有会话列表。

**请求**:
```http
GET /api/v1/sessions?user_id=user_123&page=1&page_size=20
```

**参数说明**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `user_id` | string | 是 | 用户 ID |
| `page` | int | 否 | 页码 |
| `page_size` | int | 否 | 每页数量 |
| `status` | string | 否 | 会话状态筛选 |

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "session_id": "sess_abc123",
      "status": "active",
      "message_count": 15,
      "created_at": "2026-03-02T10:00:00Z"
    },
    {
      "session_id": "sess_def456",
      "status": "archived",
      "message_count": 8,
      "created_at": "2026-03-01T15:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 25,
    "total_pages": 2
  }
}
```

---

#### 8.1.4 删除会话

删除指定会话及其所有消息。

**请求**:
```http
DELETE /api/v1/sessions/{session_id}
```

**响应**:
```json
{
  "success": true,
  "message": "会话已删除"
}
```

---

### 8.2 消息管理

#### 8.2.1 发送消息

向会话发送消息,Agent 自动处理并返回响应。

**请求**:
```http
POST /api/v1/sessions/{session_id}/messages
Content-Type: application/json

{
  "role": "user",
  "content": "帮我查询一下Python FastAPI的性能特点",
  "stream": false
}
```

**参数说明**:

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `role` | string | 是 | 角色 (`user`/`system`) |
| `content` | string | 是 | 消息内容 |
| `stream` | boolean | 否 | 是否流式返回 |

**响应**:
```json
{
  "success": true,
  "data": {
    "message_id": "msg_xyz789",
    "role": "assistant",
    "content": "FastAPI 是一个高性能的 Python Web 框架...",
    "retrieved_knowledge": [
      {
        "id": "kno_001",
        "content": "FastAPI 基于 Starlette...",
        "score": 0.92
      }
    ],
    "execution_steps": [
      {
        "step": "retrieve",
        "duration_ms": 250,
        "result": "检索到 3 条相关知识"
      },
      {
        "step": "decide",
        "duration_ms": 50,
        "result": "决定生成回答"
      }
    ],
    "created_at": "2026-03-02T10:01:00Z"
  }
}
```

---

#### 8.2.2 获取会话历史

获取会话的所有消息历史。

**请求**:
```http
GET /api/v1/sessions/{session_id}/messages?page=1&page_size=50
```

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "message_id": "msg_001",
      "role": "user",
      "content": "你好",
      "created_at": "2026-03-02T10:00:00Z"
    },
    {
      "message_id": "msg_002",
      "role": "assistant",
      "content": "你好!我是 AutonoMind,有什么可以帮助你的?",
      "created_at": "2026-03-02T10:00:01Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 15,
    "total_pages": 1
  }
}
```

---

### 8.3 知识库管理

#### 8.3.1 添加知识

手动添加单条知识到知识库。

**请求**:
```http
POST /api/v1/knowledge
Content-Type: application/json

{
  "content": "FastAPI 是一个高性能的 Python Web 框架",
  "source": "manual",
  "metadata": {
    "category": "technology",
    "tags": ["python", "fastapi"]
  }
}
```

**参数说明**:

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `content` | string | 是 | 知识内容 |
| `source` | string | 否 | 知识来源 |
| `metadata` | object | 否 | 元数据 |

**响应**:
```json
{
  "success": true,
  "data": {
    "id": "kno_001",
    "content": "FastAPI 是一个高性能的 Python Web 框架",
    "source": "manual",
    "metadata": {
      "category": "technology",
      "tags": ["python", "fastapi"]
    },
    "created_at": "2026-03-02T10:00:00Z"
  }
}
```

---

#### 8.3.2 批量添加知识

批量添加多条知识。

**请求**:
```http
POST /api/v1/knowledge/batch
Content-Type: application/json

{
  "knowledge_list": [
    {
      "content": "知识 1",
      "source": "manual"
    },
    {
      "content": "知识 2",
      "source": "manual"
    }
  ]
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "success_count": 2,
    "failed_count": 0,
    "knowledge_ids": ["kno_001", "kno_002"]
  }
}
```

---

#### 8.3.3 上传文档并添加知识

上传文档,自动提取和向量化。

**请求**:
```http
POST /api/v1/knowledge/upload
Content-Type: multipart/form-data

file: <文件>
source: "document"
metadata: {"category": "manual"}
```

**参数说明**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `file` | file | 是 | 文档文件(PDF/TXT/Markdown) |
| `source` | string | 否 | 知识来源 |
| `metadata` | object | 否 | 元数据 |

**响应**:
```json
{
  "success": true,
  "data": {
    "document_id": "doc_001",
    "knowledge_count": 25,
    "status": "processing",
    "estimated_time": 30
  }
}
```

---

#### 8.3.4 检索知识

在知识库中检索相关知识。

**请求**:
```http
POST /api/v1/knowledge/search
Content-Type: application/json

{
  "query": "Python FastAPI 的性能特点",
  "top_k": 10,
  "filters": {
    "source": "manual"
  },
  "rerank": true
}
```

**参数说明**:

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `query` | string | 是 | 查询文本 |
| `top_k` | int | 否 | 返回数量,默认 10 |
| `filters` | object | 否 | 过滤条件 |
| `rerank` | boolean | 否 | 是否重排序,默认 false |

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": "kno_001",
      "content": "FastAPI 基于 Starlette 和 Pydantic...",
      "score": 0.95,
      "metadata": {
        "source": "manual",
        "category": "technology"
      }
    },
    {
      "id": "kno_002",
      "content": "FastAPI 性能接近 Node.js...",
      "score": 0.88,
      "metadata": {
        "source": "manual"
      }
    }
  ],
  "total": 2
}
```

---

#### 8.3.5 获取知识详情

获取单条知识的详细信息。

**请求**:
```http
GET /api/v1/knowledge/{knowledge_id}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": "kno_001",
    "content": "FastAPI 是一个高性能的 Python Web 框架",
    "source": "manual",
    "metadata": {
      "category": "technology",
      "tags": ["python", "fastapi"]
    },
    "version": 1,
    "status": "active",
    "created_at": "2026-03-02T10:00:00Z",
    "updated_at": "2026-03-02T10:00:00Z"
  }
}
```

---

#### 8.3.6 更新知识

更新知识内容。

**请求**:
```http
PUT /api/v1/knowledge/{knowledge_id}
Content-Type: application/json

{
  "content": "更新后的知识内容",
  "metadata": {
    "category": "technology",
    "tags": ["python", "fastapi", "updated"]
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": "kno_001",
    "version": 2,
    "updated_at": "2026-03-02T11:00:00Z"
  }
}
```

---

#### 8.3.7 删除知识

删除知识。

**请求**:
```http
DELETE /api/v1/knowledge/{knowledge_id}
```

**响应**:
```json
{
  "success": true,
  "message": "知识已删除"
}
```

---

#### 8.3.8 列出知识

列出知识库中的知识,支持分页和过滤。

**请求**:
```http
GET /api/v1/knowledge?page=1&page_size=20&source=manual&status=active
```

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": "kno_001",
      "content": "FastAPI 是一个高性能的 Python Web 框架...",
      "source": "manual",
      "status": "active",
      "created_at": "2026-03-02T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

---

### 8.4 工具管理

#### 8.4.1 列出工具

列出所有可用工具。

**请求**:
```http
GET /api/v1/tools?enabled=true
```

**参数说明**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `enabled` | boolean | 否 | 是否只返回启用的工具 |

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "name": "search_knowledge",
      "description": "在知识库中搜索",
      "parameters": {
        "query": {
          "type": "string",
          "description": "搜索查询",
          "required": true
        },
        "top_k": {
          "type": "integer",
          "description": "返回数量",
          "default": 10
        }
      },
      "enabled": true,
      "created_at": "2026-03-02T10:00:00Z"
    },
    {
      "name": "query_database",
      "description": "查询数据库",
      "parameters": {
        "sql": {
          "type": "string",
          "description": "SQL 查询",
          "required": true
        }
      },
      "enabled": true,
      "created_at": "2026-03-02T10:00:00Z"
    }
  ]
}
```

---

#### 8.4.2 注册自定义工具

注册自定义工具。

**请求**:
```http
POST /api/v1/tools
Content-Type: application/json

{
  "name": "my_custom_tool",
  "description": "我的自定义工具",
  "parameters": {
    "input": {
      "type": "string",
      "description": "输入参数",
      "required": true
    }
  },
  "function_name": "my_module.my_function"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "name": "my_custom_tool",
    "id": "tool_001",
    "created_at": "2026-03-02T10:00:00Z"
  }
}
```

---

#### 8.4.3 启用/禁用工具

启用或禁用工具。

**请求**:
```http
PATCH /api/v1/tools/{tool_name}
Content-Type: application/json

{
  "enabled": false
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "name": "my_custom_tool",
    "enabled": false,
    "updated_at": "2026-03-02T11:00:00Z"
  }
}
```

---

### 8.5 执行日志

#### 8.5.1 查询执行日志

查询 Agent 执行日志。

**请求**:
```http
GET /api/v1/sessions/{session_id}/logs?step_type=retrieve&page=1
```

**参数说明**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `session_id` | string | 是 | 会话 ID |
| `step_type` | string | 否 | 步骤类型 (`retrieve`/`decide`/`execute`) |
| `page` | int | 否 | 页码 |
| `page_size` | int | 否 | 每页数量 |

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": "log_001",
      "session_id": "sess_abc123",
      "step_type": "retrieve",
      "input": {
        "query": "Python FastAPI"
      },
      "output": {
        "results_count": 5,
        "top_result_score": 0.95
      },
      "duration_ms": 250,
      "timestamp": "2026-03-02T10:01:00Z"
    },
    {
      "id": "log_002",
      "session_id": "sess_abc123",
      "step_type": "decide",
      "input": {
        "knowledge": [...]
      },
      "output": {
        "decision": "generate_answer",
        "reasoning": "知识足够,可以生成回答"
      },
      "duration_ms": 50,
      "timestamp": "2026-03-02T10:01:01Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 30,
    "total_pages": 2
  }
}
```

---

## 9. API 版本控制

AutonoMind API 使用 URL 路径进行版本控制:

- `/api/v1/` - 当前稳定版本
- `/api/v2/` - 未来版本(暂未发布)

---

## 10. 速率限制

| 用户类型 | 限制 |
|---------|------|
| 匿名用户 | 10 请求/分钟 |
| 认证用户 | 100 请求/分钟 |
| 企业用户 | 1000 请求/分钟 |

超出限制返回 `429 Too Many Requests`。

---

## 11. SDK 和客户端

### 11.1 Python SDK

```python
from autonomind import AutonoMindClient

# 初始化客户端
client = AutonoMindClient(
    api_key="your_api_key",
    base_url="http://localhost:8000"
)

# 创建会话
session = client.sessions.create(user_id="user_123")

# 发送消息
response = session.send_message("你好")
print(response.content)

# 添加知识
knowledge = client.knowledge.add(
    content="这是一条知识",
    source="manual"
)

# 检索知识
results = client.knowledge.search(
    query="FastAPI",
    top_k=10
)
```

### 11.2 JavaScript SDK

```javascript
import { AutonoMindClient } from '@autonomind/sdk';

const client = new AutonoMindClient({
  apiKey: 'your_api_key',
  baseUrl: 'http://localhost:8000'
});

// 创建会话
const session = await client.sessions.create({ userId: 'user_123' });

// 发送消息
const response = await session.sendMessage('你好');
console.log(response.content);
```

---

## 12. 附录

### 12.1 状态码说明

| HTTP 状态码 | 说明 |
|-----------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 429 | 超出速率限制 |
| 500 | 服务器内部错误 |

---

## 13. WebSocket 实时通信

### 13.1 连接

建立 WebSocket 连接以接收实时消息。

```http
ws://localhost:8000/api/v1/ws?token=<your_jwt_token>
```

**查询参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `token` | string | 是 | JWT Token |

### 13.2 消息格式

**服务器推送消息**:

```json
{
  "type": "message",
  "data": {
    "session_id": "sess_abc123",
    "message_id": "msg_xyz789",
    "content": "...",
    "role": "assistant"
  }
}
```

**消息类型**:

| 类型 | 说明 |
|------|------|
| `message` | 新消息 |
| `status` | 会话状态更新 |
| `error` | 错误通知 |
| `knowledge_update` | 知识库更新 |

### 13.3 心跳机制

客户端每30秒发送一次心跳:

```json
{
  "type": "ping"
}
```

服务器响应:

```json
{
  "type": "pong",
  "timestamp": "2026-03-02T10:00:00Z"
}
```

---

## 14. 流式响应 API

### 14.1 流式发送消息

支持 SSE(Server-Sent Events)流式返回 AI 响应。

```http
POST /api/v1/sessions/{session_id}/messages/stream
Content-Type: application/json

{
  "role": "user",
  "content": "写一篇关于 FastAPI 的文章"
}
```

**响应**(SSE 流):

```
data: {"type":"start","message_id":"msg_001"}

data: {"type":"token","content":"FastAPI"}

data: {"type":"token","content":" 是"}

data: {"type":"token","content":" 一个"}

...

data: {"type":"end","tokens_used":150}
```

---

## 15. 文件上传

### 15.1 单文件上传

```http
POST /api/v1/files/upload
Content-Type: multipart/form-data

file: <文件>
metadata: {"category": "document"}
```

**响应**:

```json
{
  "success": true,
  "data": {
    "file_id": "file_001",
    "filename": "document.pdf",
    "file_size": 1024000,
    "file_path": "documents/user_123/file_001.pdf",
    "url": "http://localhost:9000/autonomind/documents/user_123/file_001.pdf"
  }
}
```

### 15.2 批量上传

```http
POST /api/v1/files/upload/batch
Content-Type: multipart/form-data

files: <文件1>
files: <文件2>
files: <文件3>
```

---

## 16. 数据导出

### 16.1 导出会话记录

```http
GET /api/v1/sessions/{session_id}/export
Accept: application/json
```

**响应**:

```json
{
  "success": true,
  "data": {
    "format": "json",
    "content": {
      "session_id": "sess_abc123",
      "created_at": "2026-03-02T10:00:00Z",
      "messages": [...]
    }
  }
}
```

### 16.2 导出为其他格式

```http
GET /api/v1/sessions/{session_id}/export?format=markdown
Accept: text/markdown
```

---

## 17. 批量操作

### 17.1 批量删除知识

```http
DELETE /api/v1/knowledge/batch
Content-Type: application/json

{
  "knowledge_ids": ["kno_001", "kno_002", "kno_003"]
}
```

**响应**:

```json
{
  "success": true,
  "data": {
    "deleted_count": 3,
    "failed_count": 0
  }
}
```

### 17.2 批量更新知识

```http
PATCH /api/v1/knowledge/batch
Content-Type: application/json

{
  "updates": [
    {
      "knowledge_id": "kno_001",
      "metadata": {"category": "updated"}
    },
    {
      "knowledge_id": "kno_002",
      "status": "archived"
    }
  ]
}
```

---

## 18. 系统信息 API

### 18.1 获取系统状态

```http
GET /api/v1/system/status
```

**响应**:

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "components": {
      "database": "healthy",
      "vector_db": "healthy",
      "cache": "healthy",
      "queue": "healthy"
    },
    "uptime": 86400,
    "timestamp": "2026-03-02T10:00:00Z"
  }
}
```

### 18.2 获取系统统计

```http
GET /api/v1/system/stats
```

**响应**:

```json
{
  "success": true,
  "data": {
    "users": {
      "total": 100,
      "active": 80
    },
    "sessions": {
      "total": 1000,
      "active": 50
    },
    "knowledge": {
      "total": 5000,
      "active": 4800
    },
    "messages": {
      "total": 100000,
      "today": 1000
    }
  }
}
```

---

## 19. API 限流规则

### 19.1 限流配置

| 端点类型 | 限制 |
|---------|------|
| 认证 API | 10 req/min |
| 消息 API | 60 req/min |
| 知识检索 | 100 req/min |
| 文件上传 | 5 req/min |
| 其他 API | 100 req/min |

### 19.2 限流响应

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "请求过于频繁",
    "details": {
      "limit": 60,
      "remaining": 0,
      "reset_at": "2026-03-02T10:01:00Z"
    }
  }
}
```

---

## 20. API 变更日志

### v1.0 (2026-03-02)
- 初始版本发布
- 核心功能:会话管理、消息管理、知识库、工具管理、执行日志

---

**文档版本**: v1.0
**最后更新**: 2026-03-02

