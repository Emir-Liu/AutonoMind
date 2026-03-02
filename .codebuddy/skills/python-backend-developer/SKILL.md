---
name: Python后端开发工程师
description: 专业的Python后端开发技能包,包含FastAPI/Flask/Django框架、数据库操作、LLM集成、任务队列等通用技术知识和模板代码。适用于各类Python后端服务开发、API设计、异步任务处理等场景。
---

# Python后端开发工程师技能

## 概述

本技能提供专业的Python后端开发知识、模板代码和最佳实践,涵盖分层架构、设计模式、LLM集成、异步任务处理等核心能力。这是一个**通用技能包**,不绑定任何具体项目,可以被不同的代理调用。

## 何时使用本技能

当Python后端工程师代理工作时,会自动调用本技能获取:
- 分层架构设计知识
- 设计模式和代码模板
- LLM集成最佳实践
- 异步任务处理方案
- 通用工具类和最佳实践

## 核心能力

### 1. 分层架构实现

采用**API→Func→Core→Utils**四层架构:

- **API层**: 接口定义、参数验证、响应封装
- **Func层**: 业务逻辑组装、任务编排、状态管理
- **Core层**: 核心算法实现、抽象基类、复杂业务逻辑
- **Utils层**: 通用工具类、基础设施、第三方封装

### 2. 设计模式应用

- **抽象基类**: 定义统一接口,复用通用代码
- **混入类(Mixin)**: 功能组合,避免继承过深
- **工厂模式**: 动态创建对象,解耦类型选择
- **DTO模式**: 统一数据传输和状态管理

### 3. LLM集成

使用LangChain集成多种LLM:
- OpenAI兼容接口
- Qwen3等本地模型
- Token使用统计
- 重试机制和错误处理

### 4. 异步任务处理

- 线程池管理(见`assets/task_manager_template.py`)
- Redis Streams任务队列
- 任务状态跟踪
- 回调机制

### 5. 长文本处理

- 对话切片策略
- 摘要生成
- 结果合并

## 技能内容

### 1. 架构设计知识 (`references/design_patterns.md`)

包含:
- **分层架构设计**: API → Func → Core → Utils 四层架构
- **抽象基类模式**: 统一接口,代码复用
- **混入类模式**: 功能组合,避免继承过深
- **工厂模式**: 动态创建对象,解耦类型选择
- **DTO模式**: 统一数据验证和状态管理
- **回调机制设计**: LLM回调、任务回调
- **错误处理设计**: 细粒度错误码、自动收集
- **配置管理模式**: 环境隔离、配置优先级
- **日志管理设计**: 分级日志、结构化日志、日志轮转

### 2. 代码模板 (`assets/`)

#### 基础工具类模板
- `file_operator.py` - 文件保存/读取/JSON处理
- `time_operator.py` - 计时器/时间格式化
- `id_generator.py` - UUID和业务ID生成
- `redis_stream_handler.py` - Redis Stream消息队列

#### 核心模板
- `llm_config_template.py` - LLM配置和Token统计回调
- `task_manager_template.py` - 线程池任务管理器

### 3. 使用示例

#### 创建LLM
```python
from assets.llm_config_template import create_llm_qwen3, TokenUsageCallback

# 创建OpenAI兼容的LLM
llm = create_llm_qwen3(
    model_name="qwen3-32b-awq",
    api_key="your_key",
    base_url="http://localhost:8000"
)

# 使用Token统计回调
token_callback = TokenUsageCallback()
result = chain.invoke(input, config={"callbacks": [token_callback]})
stats = token_callback.get_stats()
```

#### 使用任务管理器
```python
from assets.task_manager_template import TaskWorker, TaskStatus

with TaskWorker(max_workers=5) as worker:
    # 提交任务
    future = worker.submit_task("task_1", process_func, data)

    # 查询状态
    status = worker.get_task_status("task_1")
    print(f"状态: {status.value}")
```

#### 应用设计模式
```python
# 从设计模式文档中学习并应用
# 参考 references/design_patterns.md

# 抽象基类示例
from abc import ABC, abstractmethod

class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, data) -> dict:
        pass

# 混入类示例
class BatchAnalyzerMixin:
    def analyze_batch(self, data_list):
        return [self.analyze(data) for data in data_list]
```

## 通用代码规范

### 必须遵守的规范
1. **类型注解**: 所有函数必须使用类型注解
2. **异常处理**: 细粒度错误码,区分失败原因
3. **Token统计**: 所有LLM调用必须包含Token统计
4. **日志分级**: DEBUG/INFO/ERROR分级记录
5. **计时器**: 耗时操作使用计时器记录
6. **配置隔离**: 使用环境变量和配置类

### 质量检查清单
- [ ] 符合分层架构原则
- [ ] 使用抽象基类定义接口
- [ ] LLM调用包含Token统计
- [ ] 异常使用细粒度错误码
- [ ] 任务状态统一管理
- [ ] 日志分级记录
- [ ] 配置环境隔离
- [ ] 所有函数有类型注解

## 适用场景

本技能适用于:
- ✅ FastAPI后端服务开发
- ✅ LLM集成(OpenAI/Qwen3等)
- ✅ 异步任务处理
- ✅ 分层架构设计
- ✅ Redis Streams任务队列
- ✅ 抽象基类和设计模式应用
- ✅ LLM调用和Token管理优化
- ✅ 任何Python后端项目
