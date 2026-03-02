# 测试设计模式

## 1. AAA 模式 (Arrange-Act-Assert)

测试代码的标准结构：

```python
def test_user_registration():
    # Arrange: 准备测试数据和环境
    user_data = {
        "username": "test_user",
        "email": "test@example.com",
        "password": "123456"
    }
    
    # Act: 执行被测操作
    response = api.post("/auth/register", json=user_data)
    
    # Assert: 验证结果
    assert response.status_code == 200
    assert "token" in response.json()
```

## 2. 参数化测试

使用不同参数运行相同测试：

```python
import pytest

@pytest.mark.parametrize("username,expected", [
    ("user1", True),
    ("user2", True),
    ("", False),  # 空用户名
    ("a" * 51, False),  # 超长用户名
])
def test_username_validation(username, expected):
    result = validate_username(username)
    assert result == expected
```

## 3. Fixture 模式

共享测试资源和环境：

```python
import pytest

@pytest.fixture
def test_user():
    """创建测试用户"""
    user = create_user("test", "test@test.com", "password")
    yield user
    # 清理
    delete_user(user.id)

@pytest.fixture
def auth_client(test_user):
    """已认证的客户端"""
    token = login(test_user.username, "password")
    client = APIClient()
    client.set_token(token)
    return client

def test_get_user_info(auth_client):
    response = auth_client.get("/user/info")
    assert response.status_code == 200
```

## 4. Mock 模式

隔离外部依赖：

```python
from unittest.mock import Mock, patch

def test_send_email():
    # Mock 邮件服务
    mock_email_service = Mock()
    mock_email_service.send.return_value = True
    
    with patch('services.email_service', mock_email_service):
        result = send_welcome_email("user@test.com")
        assert result == True
        mock_email_service.send.assert_called_once()
```

## 5. 数据驱动测试

从外部数据源加载测试数据：

```python
import json

# test_data.json
# [
#   {"input": {"username": "test"}, "expected": {"success": true}},
#   {"input": {"username": ""}, "expected": {"success": false, "error": "用户名不能为空"}}
# ]

def load_test_data(filename):
    with open(f"tests/data/{filename}") as f:
        return json.load(f)

@pytest.mark.parametrize("test_case", load_test_data("register_cases.json"))
def test_register_with_data(test_case):
    response = api.post("/auth/register", json=test_case["input"])
    assert response.json() == test_case["expected"]
```

## 6. 快照测试

验证数据结构不变：

```python
def test_api_response_structure(snapshot):
    response = api.get("/user/info")
    # 对比响应结构是否与之前一致
    assert response.json() == snapshot
```

## 7. 并发测试

测试并发场景：

```python
import threading

def test_concurrent_registration():
    results = []
    
    def register_user(i):
        response = api.post("/auth/register", json={
            "username": f"user_{i}",
            "email": f"user_{i}@test.com",
            "password": "123456"
        })
        results.append(response.status_code)
    
    # 并发注册 10 个用户
    threads = [threading.Thread(target=register_user, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # 验证所有请求都成功
    assert all(code == 200 for code in results)
```

## 8. 边界值测试

测试边界条件：

```python
@pytest.mark.parametrize("password,expected", [
    ("12345", False),    # 太短 (5字符)
    ("123456", True),    # 最小长度 (6字符)
    ("1234567890123456789012345678901", False),  # 太长 (31字符)
    ("123456789012345678901234567890", True),    # 最大长度 (30字符)
])
def test_password_length(password, expected):
    assert validate_password(password) == expected
```

## 9. 状态转换测试

测试状态机转换：

```python
def test_task_state_transitions():
    task = create_task("测试任务")
    
    # 初始状态: pending
    assert task.status == "pending"
    
    # pending -> in_progress
    task.start()
    assert task.status == "in_progress"
    
    # in_progress -> completed
    task.complete()
    assert task.status == "completed"
    
    # completed 不能回到 in_progress
    with pytest.raises(InvalidStateError):
        task.start()
```

## 10. 端到端测试模式

完整用户流程测试：

```python
def test_complete_user_journey():
    """测试完整用户旅程: 注册 -> 登录 -> 创建目标 -> 生成规划"""
    
    # 1. 注册
    register_response = api.post("/auth/register", json={
        "username": "journey_test",
        "email": "journey@test.com",
        "password": "123456"
    })
    assert register_response.status_code == 200
    token = register_response.json()["token"]
    
    # 2. 登录
    login_response = api.post("/auth/login", json={
        "username": "journey_test",
        "password": "123456"
    })
    assert login_response.status_code == 200
    
    # 3. 创建目标
    client = APIClient(token)
    goal_response = client.post("/goals", json={
        "title": "学习Python",
        "description": "3个月掌握Python编程"
    })
    assert goal_response.status_code == 200
    goal_id = goal_response.json()["id"]
    
    # 4. 生成规划
    plan_response = client.post(f"/goals/{goal_id}/generate-plan")
    assert plan_response.status_code == 200
    assert len(plan_response.json()["tasks"]) > 0
```
