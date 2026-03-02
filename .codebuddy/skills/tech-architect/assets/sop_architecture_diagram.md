# SOP引擎架构设计参考

## 1. 系统架构

### 1.1 分层架构

```
┌─────────────────────────────────────────────────────────┐
│                     API层 (FastAPI)                      │
│  - RESTful接口定义                                       │
│  - Pydantic参数验证                                      │
│  - 统一响应封装                                          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Func层 (业务逻辑)                     │
│  - SOP模板提取 (func_sop_extractor)                     │
│  - 对话分类 (func_sop_classifier)                       │
│  - 对话验证 (func_sop_validator)                        │
│  - 任务编排和状态管理                                    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Core层 (核心功能)                     │
│  ├─ FileReader: PDF/DOCX解析                          │
│  ├─ SopExtractor: LLM模板提取                          │
│  ├─ BaseConversationAnalyzer: 抽象分析器基类            │
│  ├─ BatchAnalyzerMixin: 长文本切片混入                  │
│  └─ StepValidator: 步骤验证器                          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Utils层 (基础设施)                    │
│  ├─ FileOperator: 文件操作                             │
│  ├─ MinIOClient: 对象存储                              │
│  ├─ LLMOperator: LLM调用                               │
│  ├─ RedisStreamHandler: 消息队列                        │
│  └─ Timer: 性能计时                                    │
└─────────────────────────────────────────────────────────┘
```

### 1.2 数据流架构

#### SOP模板提取流程

```
用户上传文档
    ↓
API层接收文件
    ↓
Func层创建任务
    ↓
Redis Streams推送任务
    ↓
Worker从队列获取任务
    ↓
Core层解析文档(FileReader)
    ↓
Core层提取模板(SopExtractor)
    ├─ 阶段1: 提取模板列表(LLM)
    └─ 阶段2: 提取模板内容(LLM)
    ↓
Func层保存结果到MinIO
    ↓
Func层更新数据库状态
    ↓
回调前端通知完成
```

#### 对话验证流程

```
前端提交验证请求
    ↓
API层验证参数
    ↓
Func层创建验证任务
    ↓
Core层加载SOP模板(MinIO)
    ↓
Core层验证对话
    ├─ 步骤验证(规则匹配+LLM)
    ├─ 禁忌语检测(关键词)
    └─ 敏感词检测(关键词+LLM)
    ↓
Func层保存结果
    ↓
Func层更新任务状态
    ↓
回调前端通知完成
```

## 2. 核心设计模式

### 2.1 抽象基类模式

**目的**: 定义统一接口,便于扩展新的分析器

```python
# 抽象基类
class BaseConversationAnalyzer(ABC):
    @abstractmethod
    def __init__(self, llm_config: Dict[str, str]):
        pass
    
    @abstractmethod
    def analyze(self, conversation_json: Dict[str, Any]) -> Dict[str, Any]:
        pass

# 具体实现
class StepValidator(BaseConversationAnalyzer):
    def __init__(self, llm_config: Dict[str, str]):
        self.llm = LLMOperator(**llm_config).get_llm()
    
    def analyze(self, conversation_json: Dict[str, Any]) -> Dict[str, Any]:
        # 具体验证逻辑
        pass

class TabooDetector(BaseConversationAnalyzer):
    def __init__(self, llm_config: Dict[str, str]):
        self.llm = LLMOperator(**llm_config).get_llm()
    
    def analyze(self, conversation_json: Dict[str, Any]) -> Dict[str, Any]:
        # 具体检测逻辑
        pass
```

### 2.2 混入类(Mixin)模式

**目的**: 功能组合,避免继承过深

```python
# 混入类: 提供批量处理能力
class BatchAnalyzerMixin(Generic[T]):
    def analyze_batch(self, conversation: Dict, analyzer_instance) -> Dict:
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
class StepValidator(BatchAnalyzerMixin, BaseConversationAnalyzer):
    def __init__(self, llm_config: Dict[str, str], slice_config: SliceConfig):
        super().__init__()
        self.slicer = ConversationSlicer(slice_config)
    
    def analyze(self, conversation_json: Dict[str, Any]) -> Dict[str, Any]:
        # 使用混入的批量处理能力
        return self.analyze_batch(conversation_json, self)
```

### 2.3 DTO模式

**目的**: 统一数据传输和状态管理

```python
class BaseDTOModel(ABC):
    """DTO基类,统一任务数据传输和状态管理"""
    
    def __init__(self):
        self.task_status = TaskStatus.processing
        self.error_code = None
        self.error_info = None
        self.start_time = get_utc_datetime()
        self.end_time = None
        self.elapsed_time = 0
    
    @abstractmethod
    def from_request(self, request: Any):
        pass
    
    @abstractmethod
    def create_task_status(self):
        pass
    
    def update_task_status(self, task_status, error_code=None, error_info=None):
        self.task_status = task_status
        self.error_code = error_code
        self.error_info = error_info
```

### 2.4 工厂模式

**目的**: 动态创建对象,解耦类型选择

```python
class StreamFactory:
    """流处理器工厂"""
    _registry = {}
    
    @classmethod
    def register(cls, stream_type: str, handler_class: Type):
        cls._registry[stream_type] = handler_class
    
    @classmethod
    def create(cls, stream_type: str, **kwargs):
        handler_class = cls._registry.get(stream_type)
        if not handler_class:
            raise ValueError(f"未知的流类型: {stream_type}")
        return handler_class(**kwargs)

# 注册处理器
StreamFactory.register("sop_validate", SopValidateStream)
StreamFactory.register("sop_extract", SopExtractStream)

# 使用
processor = StreamFactory.create("sop_validate", stream_key="test")
```

## 3. 数据库设计

### 3.1 核心表结构

```sql
-- SOP模板表
CREATE TABLE sop_templates (
    sop_template_id VARCHAR(64) PRIMARY KEY,
    template_name VARCHAR(255) NOT NULL,
    product_type VARCHAR(50) NOT NULL,
    product_subtype VARCHAR(100),
    description TEXT,
    risk_level VARCHAR(10),
    structure JSON COMMENT '树形结构',
    detection_rules JSON COMMENT '检测规则',
    version VARCHAR(20) DEFAULT '2.0',
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- SOP验证任务表
CREATE TABLE sop_validation_tasks (
    validation_id VARCHAR(50) PRIMARY KEY,
    sop_template_id VARCHAR(50) NOT NULL,
    conversation_json_path VARCHAR(500) NOT NULL,
    result_json_path VARCHAR(500),
    status VARCHAR(10) NOT NULL DEFAULT 'processing',
    progress INT DEFAULT 0,
    processing_time FLOAT,
    error_code VARCHAR(50),
    error_detail TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    failed_at TIMESTAMP,
    FOREIGN KEY (sop_template_id) REFERENCES sop_templates(sop_template_id)
);

-- 对话表
CREATE TABLE conversations (
    conversation_id VARCHAR(50) PRIMARY KEY,
    session_id VARCHAR(50),
    speaker_a_id VARCHAR(50),
    speaker_b_id VARCHAR(50),
    transcript_path VARCHAR(500),
    duration INT COMMENT '时长(秒)',
    word_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 4. 性能优化策略

### 4.1 数据库优化

```sql
-- 索引优化
CREATE INDEX idx_sop_template_product ON sop_templates(product_type, product_subtype);
CREATE INDEX idx_validation_status ON sop_validation_tasks(status);
CREATE INDEX idx_validation_created ON sop_validation_tasks(created_at);
CREATE INDEX idx_conversation_session ON conversations(session_id);

-- 查询优化
-- 使用EXPLAIN分析慢查询
EXPLAIN SELECT * FROM sop_validation_tasks 
WHERE status = 'processing' 
ORDER BY created_at DESC LIMIT 100;
```

### 4.2 缓存策略

```python
# SOP模板缓存
def get_template_with_cache(template_id: str):
    # 1. 尝试从Redis缓存获取
    cache_key = f"sop:template:{template_id}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # 2. 从MinIO加载
    template = load_template_from_minio(template_id)
    
    # 3. 写入缓存(1小时)
    redis_client.setex(cache_key, 3600, json.dumps(template))
    
    return template

# 检测规则缓存
def get_detection_rules(template_id: str):
    cache_key = f"sop:rules:{template_id}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    template = get_template_with_cache(template_id)
    rules = template.get('detection_rules', {})
    
    redis_client.setex(cache_key, 3600, json.dumps(rules))
    return rules
```

### 4.3 异步处理

```python
# 使用Redis Streams实现任务队列
def submit_validation_task(dto: SOPValidationDTO):
    # 1. 创建任务记录
    task_id = generate_uuid()
    dto.create_task_status()
    
    # 2. 推送到Redis Streams
    handler = RedisStreamHandler()
    handler.add_message(
        stream_key='sop_validation_tasks',
        data={
            'task_id': task_id,
            'conversation_path': dto.conversation_json_path,
            'template_id': dto.sop_template_id,
            'timestamp': get_iso_timestamp()
        }
    )
    
    return task_id

# Worker处理任务
def worker_loop():
    handler = RedisStreamHandler()
    while True:
        messages = handler.read_messages_from_group(
            stream_key='sop_validation_tasks',
            consumer_group='validation_workers',
            consumer_name=f'worker_{os.getpid()}',
            count=1,
            block_ms=5000
        )
        
        for stream, msg_list in messages:
            for msg_id, fields in msg_list:
                try:
                    process_validation_task(fields)
                    handler.ack_message('sop_validation_tasks', 'validation_workers', msg_id)
                except Exception as e:
                    logger.error(f"处理任务失败: {e}")
```

## 5. 安全设计

### 5.1 API安全

```python
# JWT认证
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = decode_jwt(token)
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# 接口保护
@app.post("/api/v1/sop/validate", dependencies=[Depends(verify_token)])
async def validate_conversation(request: ValidationRequest):
    pass
```

### 5.2 数据安全

```python
# 敏感信息脱敏
def mask_sensitive_data(text: str) -> str:
    """脱敏处理: 隐藏身份证号、手机号等"""
    # 手机号脱敏
    text = re.sub(r'(\d{3})\d{4}(\d{4})', r'\1****\2', text)
    # 身份证号脱敏
    text = re.sub(r'(\d{6})\d{8}(\d{4})', r'\1********\2', text)
    return text

# 数据加密存储
from cryptography.fernet import Fernet

cipher = Fernet(ENCRYPTION_KEY)

def encrypt_data(data: str) -> str:
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(encrypted: str) -> str:
    return cipher.decrypt(encrypted.encode()).decode()
```

## 6. 监控和日志

### 6.1 性能监控

```python
# 使用Timer记录关键操作
from app.utils.time_operator import Timer

with Timer() as timer:
    result = validate_conversation(conversation, template)

logger.info(f"验证耗时: {timer.get_elapsed_time():.2f}秒")

# 自定义Prometheus指标
from prometheus_client import Counter, Histogram

# 指标定义
validation_requests_total = Counter(
    'sop_validation_requests_total',
    'Total validation requests',
    ['status']
)

validation_duration_seconds = Histogram(
    'sop_validation_duration_seconds',
    'Validation request duration',
    buckets=[0.1, 0.5, 1, 2, 5, 10]
)

# 使用指标
validation_requests_total.labels(status='success').inc()
validation_duration_seconds.observe(duration)
```

### 6.2 日志记录

```python
from loguru import logger

# 结构化日志
logger.info(
    "开始验证对话",
    extra={
        'task_id': task_id,
        'template_id': template_id,
        'conversation_length': len(conversation)
    }
)

# 错误日志
logger.error(
    "验证失败",
    exc_info=True,
    extra={
        'task_id': task_id,
        'error_code': error_code,
        'error_detail': str(e)
    }
)
```

## 7. 扩展性设计

### 7.1 新增分析器

```python
# 1. 继承抽象基类
class SentimentAnalyzer(BaseConversationAnalyzer):
    def __init__(self, llm_config: Dict[str, str]):
        self.llm = LLMOperator(**llm_config).get_llm()
    
    def analyze(self, conversation_json: Dict[str, Any]) -> Dict[str, Any]:
        # 情感分析逻辑
        pass

# 2. 注册到工厂
StreamFactory.register("sentiment_analysis", SentimentStream)
```

### 7.2 新增数据源

```python
# 支持新的文档格式
class ExcelReader(BaseFileReader):
    def run(self) -> str:
        from openpyxl import load_workbook
        wb = load_workbook(self.file_path or io.BytesIO(self.file_bytes))
        # 提取文本
        pass

# 注册到FileReaderFactory
FileReaderFactory.register('xlsx', ExcelReader)
FileReaderFactory.register('xls', ExcelReader)
```

## 8. 技术决策记录(ADR)

### ADR-001: 选择FastAPI作为Web框架

**状态**: 已接受

**背景**: 需要一个高性能的Python Web框架用于SOP引擎API服务

**决策**: 选择FastAPI作为主要Web框架

**理由**:
1. 基于Starlette和Pydantic,性能优异
2. 自动生成API文档(支持Swagger和ReDoc)
3. 类型安全,支持异步
4. 社区活跃,文档完善
5. 与LangChain集成良好

**后果**:
- 正面: 开发效率高,类型安全,自动文档
- 负面: 学习曲线,生态不如Django

### ADR-002: 选择Redis Streams作为任务队列

**状态**: 已接受

**背景**: 需要一个可靠的任务队列来处理异步任务

**决策**: 使用Redis Streams实现任务队列

**理由**:
1. 支持消费者组模式,多worker并发
2. 消息持久化,不丢失
3. 性能优异,延迟低
4. 与Redis缓存共用,简化架构

**后果**:
- 正面: 高性能,可靠,易实现
- 负面: 需要处理消息确认和重试机制

### ADR-003: 选择MinIO作为对象存储

**状态**: 已接受

**背景**: 需要存储大量文档文件和模板JSON

**决策**: 使用MinIO作为对象存储

**理由**:
1. S3兼容API,易于使用
2. 自主可控,可本地部署
3. 成本低,性能好
4. 与S3生态兼容

**后果**:
- 正面: 自主可控,成本低,兼容性好
- 负面: 需要自己运维,分布式配置复杂
