# Python后端设计模式应用

本文档整理了Python后端开发中的设计模式和架构思路,适用于各种后端项目。

## 1. 分层架构设计

### 职责划分

```
┌─────────────────────────────────────────┐
│         API层                      │
│  - 接口定义                         │
│  - 参数验证(Pydantic)               │
│  - 响应封装                         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Func层                     │
│  - 业务逻辑组装                     │
│  - 任务编排                         │
│  - 状态管理                         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Core层                     │
│  - 核心算法实现                     │
│  - 抽象基类                         │
│  - 复杂业务逻辑                     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Utils层                    │
│  - 通用工具类                       │
│  - 基础设施                         │
│  - 第三方封装                       │
└─────────────────────────────────────────┘
```

### 设计原则

1. **单向依赖**: 上层依赖下层,下层不依赖上层
2. **接口隔离**: 通过抽象基类定义接口,具体实现替换不影响上层
3. **单一职责**: 每层专注自己的职责,不越界处理

---

## 2. 抽象基类模式

### 应用场景

当有多个相似功能的模块时,定义抽象基类统一接口。

### 实现示例

#### 对话分析器基类

```python
class BaseConversationAnalyzer(ABC):
    """对话分析器抽象基类"""
    
    def __init__(
        self, 
        llm_model_name, 
        llm_model_api_key,
        llm_model_base_url, 
        llm_model_api_type
    ):
        # 统一的初始化逻辑
        self.llm = LLMOperator(...).get_llm()
    
    @abstractmethod
    def analyze(self, conversation_json: Dict, **kwargs) -> Dict:
        """分析方法,子类必须实现"""
        pass
    
    def _format_conversation_text(self, conversation: Dict) -> str:
        """通用方法:格式化对话文本"""
        # 默认实现,子类可覆盖
        transcripts = conversation.get('transcripts', [])
        formatted = []
        for item in transcripts:
            formatted.append(f"[{item['turn_id']}] {item['speaker']}: {item['text']}")
        return "\n".join(formatted)
```

### 优势

- **统一接口**: 所有分析器使用相同的调用方式
- **代码复用**: 通用方法在基类实现一次
- **易扩展**: 新增分析器只需继承并实现抽象方法

---

## 3. 混入类(Mixin)模式

### 应用场景

当多个类需要相同的功能,但又不适合通过继承获取时使用。

### 实现示例

#### 批量分析混入

```python
class BatchAnalyzerMixin(Generic[T]):
    """批量分析混入类"""
    
    def analyze_batch(self, conversation: Dict, analyzer_instance):
        """批量分析逻辑"""
        # 1. 提取对话
        transcripts = self._extract_conversation(conversation)
        
        # 2. 检查是否需要切片
        if not self._need_slice(transcripts):
            return analyzer_instance.analyze(conversation)
        
        # 3. 切片处理
        slices = self.slicer.slice_conversation(transcripts)
        
        # 4. 批量分析并合并
        results = [analyzer_instance.analyze({"transcripts": s}) for s in slices]
        return self._merge_results(results)

# 使用混入
class TabooAnalyzerBatch(BatchAnalyzerMixin, BaseConversationAnalyzer):
    """禁忌语批量分析器"""
    pass  # 自动获得批量处理能力
```

### 优势

- **功能组合**: 通过多重继承灵活组合功能
- **避免继承层次过深**: 不需要多层继承
- **可复用**: 一个混入可以被多个类使用

---

## 4. DTO模式

### 应用场景

统一管理请求数据转换、任务状态更新、响应构造。

### 实现示例

```python
class BaseDTOModel(ABC):
    """DTO基类"""
    
    def __init__(self):
        # 统一的状态管理
        self.task_status = TaskStatus.processing
        self.error_code = None
        self.error_info = None
        
        # 统一的时间统计
        self.start_time = get_utc_datetime()
        self.end_time = None
        self.elapsed_time = 0
    
    @abstractmethod
    def from_request(self, request: Any):
        """从请求提取数据"""
        pass
    
    @abstractmethod
    def create_task_status(self):
        """创建任务状态记录"""
        pass
    
    def update_task_status(self, task_status, error_code=None):
        """统一的状态更新逻辑"""
        self.task_status = task_status
        self.error_code = error_code
        
        # 调用数据库更新
        if task_status == TaskStatus.completed:
            self.complete_task_status()
        elif task_status == TaskStatus.failed:
            self.fail_task_status()
```

### 优势

- **数据验证**: Pydantic自动验证请求参数
- **状态追踪**: 统一管理任务生命周期
- **代码简化**: 业务逻辑不需要关注状态更新细节

---

## 5. 工厂模式

### 应用场景

根据类型动态创建对象,避免if-else分支。

### 实现示例

```python
class StreamFactory:
    """流处理器工厂"""
    
    _registry = {}
    
    @classmethod
    def register(cls, stream_type: str, handler_class):
        """注册处理器"""
        cls._registry[stream_type] = handler_class
    
    @classmethod
    def create(cls, stream_type: str, **kwargs):
        """创建处理器实例"""
        handler_class = cls._registry.get(stream_type)
        if not handler_class:
            raise ValueError(f"未知的流类型: {stream_type}")
        return handler_class(**kwargs)

# 注册
StreamFactory.register("sop_validate", SopValidateStream)
StreamFactory.register("sop_extract", SopExtractStream)

# 使用
processor = StreamFactory.create("sop_validate", stream_key="test")
```

### 优势

- **解耦**: 使用者不需要知道具体类
- **易扩展**: 新增类型只需注册
- **配置化**: 可通过配置文件决定创建哪个实例

---

## 6. 回调机制设计

### LLM回调

```python
class TokenUsageCallback(BaseCallbackHandler):
    """统计Token消耗"""
    
    def on_llm_end(self, response, **kwargs):
        # 自动累加Token使用量
        token_usage = response.llm_output.get('token_usage', {})
        self.total_tokens += token_usage.get('total_tokens', 0)

# 使用
token_callback = TokenUsageCallback()
result = chain.invoke(input, config={"callbacks": [token_callback]})
```

### 任务完成回调

```python
def callback(url: str, data: Dict):
    """统一的回调函数"""
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            logger.info("回调成功")
        else:
            logger.error(f"回调失败: {response.status_code}")
    except Exception as e:
        logger.error(f"回调异常: {e}")

# 检查所有任务完成后回调
if all(task.status == TaskStatus.completed for task in tasks):
    callback(url=config.CALLBACK_URL, data=result_data)
```

---

## 7. 错误处理设计

### 细粒度错误码

```python
class ErrorStatus:
    """错误状态基类"""
    
    @classmethod
    def get_all_errors(cls) -> dict:
        """自动收集所有错误码"""
        all_errors = []
        for attr_name in dir(cls):
            if not attr_name.startswith('_') and attr_name.isupper():
                attr_value = getattr(cls, attr_name)
                if isinstance(attr_value, str) and attr_value:
                    all_errors.append(attr_value)
        return set(all_errors)

class CommonErrorStatus(ErrorStatus):
    DATABASE_CONNECTION_ERROR = 'database_connection_error'
    LLM_CONNECTION_ERROR = 'llm_connection_error'
    MINIO_CONNECTION_ERROR = 'minio_connection_error'
```

### 异常处理流程

```python
try:
    # 步骤1: 读取文件
    content = MinIOClient().read_bytes(path)
except Exception as e:
    # 细分错误,更新任务状态
    dto.update_task_status(
        task_status=TaskStatus.failed,
        error_code=SOPExtractorErrorStatus.SOP_TEMPLATE_ACCESS_ERROR,
        error_info=f'读取文件失败:{e}'
    )
    raise  # 继续抛出,让上层处理
```

### 优势

- **问题定位**: 错误码明确指出问题所在
- **自动收集**: 自动收集所有定义的错误码
- **统一管理**: 错误信息集中定义

---

## 8. 配置管理模式

### 环境隔离

```python
class Config(BaseSettings):
    # 应用配置
    APP_NAME: str = "SOP Engine"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str
    
    # LLM配置
    llm_model_name: str
    llm_model_api_key: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
```

### 配置优先级

1. 环境变量(最高优先级)
2. .env文件
3. 默认值(最低优先级)

---

## 9. 日志管理设计

### 分级日志

```python
logger = LoguruOperator.init_app(
    name="sop_validator",
    log_dir="./logs",
    console_level="INFO",    # 控制台只显示INFO及以上
    file_level="DEBUG"        # 文件记录DEBUG
)

# 使用
logger.debug("调试信息")  # 只写文件
logger.info("普通信息")   # 控制台+文件
logger.error("错误信息")  # 控制台+文件
```

### 结构化日志

```python
logger.bind(
    task_id="123",
    conversation_id="456",
    user_id="789"
).info("验证完成")
```

### 日志轮转

```python
log.add_file_handler(
    filename="logs/app.log",
    rotation="200 MB",      # 大小限制
    retention="30 days",     # 保留时间
    compression="zip"        # 压缩旧日志
)
```

---

## 10. 设计模式选择指南

| 场景 | 推荐模式 | 理由 |
|------|----------|------|
| 多个相似功能模块 | 抽象基类 | 统一接口,复用代码 |
| 多个类需要相同功能 | 混入类 | 灵活组合,避免继承过深 |
| 根据类型创建对象 | 工厂模式 | 解耦,易扩展 |
| 统一管理请求响应 | DTO模式 | 数据验证,状态跟踪 |
| 需要统计信息 | 回调机制 | 不侵入业务逻辑 |
| 统一配置管理 | 单例+配置类 | 全局唯一,环境隔离 |
| 大文本处理 | 切片模式 | 避免超长上下文 |
