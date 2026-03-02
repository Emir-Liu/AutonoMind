# 测试执行问题与最佳实践

## 问题1: 模块导入错误

### 问题描述
```
ModuleNotFoundError: No module named 'main'
```

### 原因分析
测试文件使用了错误的导入路径:
- 错误: `from app.main import app`
- 正确: `from main import app` (main.py在backend目录下)

### 解决方案
在每个测试目录创建`conftest.py`,在fixture内部导入main:

```python
# conftest.py
@pytest.fixture(scope="function")
def client(db) -> Generator:
    """创建测试客户端"""
    from main import app  # 在fixture内部导入

    def override_get_db():
        try:
            yield db
            db.commit()
        finally:
            db.rollback()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
```

### 为什么在fixture内导入?
1. 避免导入时的循环依赖
2. 确保测试环境变量已设置
3. 允许pytest正确初始化测试环境

---

## 问题2: Windows命令兼容性

### 问题描述
Windows环境下使用Linux命令导致失败:
```bash
head -100  # Windows不支持
tail -20   # Windows不支持
```

### 解决方案
使用Windows兼容命令或跨平台Python脚本:

```bash
# Windows
findstr /C:"passed" /C:"failed"

# 或使用Python
python -m pytest tests/ -v --tb=no
```

---

## 问题3: 测试执行效率低

### 问题描述
测试执行时间长,每次都重新创建数据库

### 解决方案
使用pytest缓存和并行执行:

```bash
# 使用缓存
pytest tests/ --cache-clear  # 清除缓存
pytest tests/ -v            # 使用缓存加速

# 并行执行(需要pytest-xdist)
pip install pytest-xdist
pytest tests/ -n auto        # 自动并行
```

---

## 问题4: 数据库重置不完整

### 问题描述
E2E测试中多个测试使用相同用户名导致冲突:
```
sqlite3.IntegrityError: UNIQUE constraint failed: users.username
```

### 解决方案
在每个测试前重置数据库:

```python
def reset_database():
    """重置数据库：删除所有表并重新创建"""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

@pytest.fixture(scope="function")
def db() -> Generator:
    """创建测试数据库会话"""
    reset_database()  # 每个测试前重置
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
```

---

## 问题5: 命令重定向错误

### 问题描述
```bash
cmd1 && cmd2  # Windows不支持&&
```

### 解决方案
使用Windows语法:
```bash
cmd1 & cmd2   # Windows顺序执行
# 或分步执行
```

---

## 测试目录结构最佳实践

```
tests/
├── backend/                    # 后端测试
│   ├── tests/
│   │   ├── conftest.py        # 后端测试配置
│   │   ├── test_auth.py
│   │   ├── test_goals.py
│   │   └── ...
│   └── pytest.ini             # pytest配置
├── integration/               # 集成测试
│   ├── conftest.py           # 集成测试配置
│   ├── test_api_flow.py
│   └── test_e2e_complete_flow.py
├── security/                 # 安全测试
│   ├── conftest.py           # 安全测试配置
│   └── test_security.py
├── performance/              # 性能测试
│   ├── conftest.py           # 性能测试配置
│   └── test_performance.py
└── frontend/                # 前端测试
    ├── test_components.py
    └── test_pages.py
```

---

## conftest.py 标准模板

```python
"""
测试配置文件
每个测试目录都应该有自己的conftest.py
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# 2. 设置测试环境变量
TEST_DB_PATH = "./test_xxx.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ["TESTING"] = "true"

# 3. 导入模型和工具
from app.models import User, Goal, Plan, Task
from app.core.security import get_password_hash, create_access_token
from app.core.database import Base, get_db

# 4. 创建测试专用引擎
test_engine = create_engine(
    f"sqlite:///{TEST_DB_PATH}",
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# 5. 数据库重置函数
def reset_database():
    """重置数据库"""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

# 6. 数据库fixture
@pytest.fixture(scope="function")
def db() -> Generator:
    """创建测试数据库会话"""
    reset_database()
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

# 7. 测试客户端fixture
@pytest.fixture(scope="function")
def client(db) -> Generator:
    """创建测试客户端"""
    from main import app  # 重要:在fixture内导入

    def override_get_db():
        try:
            yield db
            db.commit()
        finally:
            db.rollback()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

# 8. 测试用户fixture
@pytest.fixture
def test_user(db) -> User:
    """创建测试用户"""
    password_hash = get_password_hash('pass123')
    user = User(
        username="testuser",
        password_hash=password_hash,
        email="test@example.com"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# 9. 认证头fixture
@pytest.fixture
def auth_headers(test_user) -> dict:
    """创建认证请求头"""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}

# 10. 清理fixture
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    """测试会话结束时清理测试数据库文件"""
    yield
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
```

---

## 测试命名规范

### 测试文件命名
- `test_<module>.py` - 单元测试
- `test_<feature>_flow.py` - 集成测试
- `test_e2e_<scenario>.py` - E2E测试
- `test_security.py` - 安全测试
- `test_performance.py` - 性能测试

### 测试类命名
```python
class Test<Feature>:           # 功能测试
class Test<Feature>Flow:        # 流程测试
class Test<Feature>Scenarios:   # 场景测试
class TestBoundaryConditions:    # 边界测试
```

### 测试方法命名
```python
def test_<action>_<condition>():
    """测试<动作>_<条件>"""
    
def test_<module>_<feature>():
    """测试<模块>_<功能>"""
```

---

## 常用测试命令

### 运行所有测试
```bash
pytest tests/ -v
```

### 运行特定测试
```bash
# 运行特定文件
pytest tests/security/test_security.py -v

# 运行特定类
pytest tests/security/test_security.py::TestAuthentication -v

# 运行特定方法
pytest tests/security/test_security.py::TestAuthentication::test_weak_password_rejected -v
```

### 查看测试覆盖率
```bash
pip install pytest-cov
pytest tests/ --cov=backend/app --cov-report=html
```

### 并行执行
```bash
pip install pytest-xdist
pytest tests/ -n auto
```

### 只运行失败的测试
```bash
pytest tests/ --lf
```

---

## 测试最佳实践清单

### ✅ 应该做的
- [x] 每个测试目录都有conftest.py
- [x] 使用独立的测试数据库
- [x] 每个测试前重置数据库
- [x] 使用fixture提供测试数据
- [x] 测试后清理资源
- [x] 使用描述性的测试名称
- [x] 测试正常流程和异常流程
- [x] 测试边界条件

### ❌ 不应该做的
- [x] 在模块顶部直接导入main
- [x] 多个测试共享数据库状态
- [x] 测试间有依赖关系
- [x] 忽略测试清理
- [x] 使用硬编码的测试数据
- [x] 测试用例太复杂
- [x] 缺少异常场景测试

---

## 故障排查流程

### 1. 导入错误
```
ModuleNotFoundError
```
**检查**:
- conftest.py是否存在
- sys.path是否正确设置
- 是否在fixture内导入main

### 2. 数据库错误
```
IntegrityError
```
**检查**:
- 是否在测试前重置数据库
- 测试数据是否唯一
- 是否有外键约束冲突

### 3. 认证错误
```
401 Unauthorized
```
**检查**:
- auth_headers fixture是否正确
- token是否过期
- token格式是否正确

### 4. 断言错误
```
AssertionError
```
**检查**:
- 响应数据结构是否正确
- 断言逻辑是否正确
- 是否使用了正确的状态码

---

## 性能优化建议

1. **使用pytest缓存**: `-v --cache-clear` → `-v`
2. **并行执行**: `pytest tests/ -n auto`
3. **只运行修改的测试**: `pytest tests/ --modified`
4. **使用快速数据库**: SQLite测试数据库
5. **避免重复初始化**: 使用scope='session'的fixture

---

**版本**: 1.0
**创建日期**: 2026-01-30
**适用项目**: LifeManager MVP
