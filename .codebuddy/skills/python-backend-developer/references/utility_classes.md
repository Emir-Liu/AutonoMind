# 工具类设计指南

本文档说明项目中通用工具类的设计原则和使用场景。

---

## 1. 文件操作类 (FileOperator)

### 设计原则

- **统一接口**: 使用静态方法提供一致的调用方式
- **多格式支持**: 支持bytes/str/dict三种内容类型
- **异常处理**: 捕获异常并返回None/False,不中断程序
- **路径灵活性**: 支持完整路径或路径+文件名组合

### 核心功能

```python
# 保存文件
FileOperator.save_file(content, path, filename)

# 读取文件
content = FileOperator.read_file(path, filename, byte=True/False)

# 读取JSON
data = FileOperator.read_json(path, filename)

# 获取文件信息
filename, name, ext = FileOperator.get_file_info(path)
```

### 使用场景

1. **配置文件管理**: 保存/加载YAML/JSON配置
2. **日志文件**: 保存分析结果到文件
3. **临时文件**: 处理上传的文件
4. **数据导出**: 生成CSV/JSON报告

---

## 2. 计时器类 (Timer)

### 设计原则

- **上下文管理器**: 支持`with`语法自动计时
- **灵活控制**: 手动start/stop和自动计时两种模式
- **信息丰富**: 记录开始/结束时间、总耗时
- **线程安全**: 基于time.time(),适用于单线程场景

### 核心功能

```python
# 方式1: 手动控制
timer = Timer()
# ... 执行代码 ...
elapsed = timer.stop()
print(f"耗时: {elapsed:.2f}秒")

# 方式2: 上下文管理器
with Timer() as t:
    # ... 执行代码 ...
print(f"耗时: {t.get_elapsed_time():.2f}秒")

# 方式3: 获取实时耗时
timer = Timer()
time.sleep(1)
print(f"已用时间: {timer.get_elapsed_time():.2f}秒")
```

### 使用场景

1. **性能监控**: 记录API响应时间
2. **任务计时**: 统计LLM调用耗时
3. **性能优化**: 识别慢查询/慢操作
4. **SLA监控**: 确保处理时间符合要求

---

## 3. ID生成器

### 设计原则

- **业务ID**: 提供业务相关的ID生成函数
- **统一格式**: 使用UUID保证唯一性
- **可扩展**: 支持自定义前缀
- **类型安全**: 返回字符串,便于存储和传输

### 核心功能

```python
# 生成UUID
uuid = generate_uuid()

# 生成业务ID
extract_id = generate_sop_extract_id()
classify_id = generate_sop_classify_id()
validate_id = generate_sop_validate_id()

# 生成带前缀的ID
task_id = generate_task_id('TASK')
```

### 使用场景

1. **任务ID**: 为异步任务生成唯一标识
2. **会话ID**: 标识用户会话
3. **数据ID**: 数据库记录的主键
4. **追踪ID**: 分布式追踪的trace_id

---

## 4. Redis Stream处理器

### 设计原则

- **封装原生API**: 简化redis-py的Stream操作
- **异常处理**: 统一处理连接和操作异常
- **消费者组**: 支持多消费者模式
- **灵活性**: 支持阻塞和非阻塞读取

### 核心功能

```python
# 初始化
handler = RedisStreamHandler(
    host='localhost',
    password='password',
    port=6379,
    db=0
)

# 写入消息
msg_id = handler.add_message('task_stream', {
    'task_id': '123',
    'type': 'validate',
    'data': '{"conversation": "test"}'
})

# 读取消息
messages = handler.read_messages('task_stream', count=1, block_ms=5000)

# 消费者组模式
handler.create_consumer_group('task_stream', 'worker_group')
messages = handler.read_messages_from_group(
    'task_stream',
    'worker_group',
    'consumer_1',
    count=1
)

# 确认消息
handler.ack_message('task_stream', 'worker_group', msg_id)
```

### 使用场景

1. **任务队列**: 异步任务调度
2. **消息队列**: 微服务间通信
3. **事件流**: 实时数据处理
4. **工作流**: 多步骤任务编排

### 消费者组最佳实践

```python
# 1. 创建消费者组
handler.create_consumer_group('task_stream', 'worker_group')

# 2. 多消费者并发处理
def worker(consumer_name: str):
    while True:
        messages = handler.read_messages_from_group(
            'task_stream',
            'worker_group',
            consumer_name,
            count=1,
            block_ms=5000
        )
        
        for stream, msg_list in messages:
            for msg_id, fields in msg_list:
                try:
                    # 处理消息
                    process_message(fields)
                    # 确认处理完成
                    handler.ack_message('task_stream', 'worker_group', msg_id)
                except Exception as e:
                    logger.error(f"处理消息失败: {e}")

# 3. 启动多个消费者
import threading
for i in range(3):
    t = threading.Thread(target=worker, args=(f'consumer_{i}',))
    t.start()
```

---

## 工具类选择指南

| 需求 | 工具类 | 说明 |
|------|--------|------|
| 文件保存/读取 | FileOperator | 支持多格式,自动创建目录 |
| 性能监控 | Timer | 上下文管理器,自动计时 |
| 唯一标识生成 | id_generator | UUID和业务ID |
| 异步任务队列 | RedisStreamHandler | Redis Streams,消费者组 |

---

## 最佳实践

### 1. 统一导入路径

```python
# 统一从utils导入
from app.utils.file_operator import FileOperator
from app.utils.time_operator import Timer, get_iso_timestamp
from app.utils.generate_id import generate_uuid
from app.utils.redis_stream import RedisStreamHandler
```

### 2. 异常处理模式

```python
# 不中断程序的异常处理
result = FileOperator.read_json(path)
if result is None:
    logger.error(f"读取配置文件失败: {path}")
    # 使用默认配置或优雅降级
    result = default_config
```

### 3. 上下文管理器优先

```python
# 推荐: 使用with语句
with Timer() as timer:
    process_data()
logger.info(f"处理耗时: {timer.get_elapsed_time():.2f}秒")

# 不推荐: 手动控制
timer = Timer()
process_data()
timer.stop()
```

### 4. ID命名规范

```python
# 业务ID: 模块_操作_id
generate_sop_extract_id()  # OK
task_validate_id            # OK
user_session_id             # OK

# 避免过于通用的命名
generate_id()               # 不推荐,太通用
create_id()                 # 不推荐,动词开头
```

---

## 扩展建议

### 1. 配置加载器

```python
class ConfigLoader:
    """统一配置加载器"""
    
    @staticmethod
    def load_yaml(path: str) -> dict:
        pass
    
    @staticmethod
    def load_json(path: str) -> dict:
        return FileOperator.read_json(path) or {}
```

### 2. 缓存装饰器

```python
from functools import wraps

def timed_cache(seconds: int = 300):
    """带过期时间的缓存装饰器"""
    cache = {}
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < seconds:
                    return result
            
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
            return result
        return wrapper
    return decorator
```

### 3. 重试装饰器

```python
def retry(max_attempts: int = 3, delay: float = 1.0):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator
```
