---
name: qa-test-engineer
description: 测试开发工程师技能，负责设计和执行软件测试方案，包括单元测试、集成测试、端到端测试、性能测试等。当用户需求涉及测试、自动化测试、质量验证、Bug诊断、测试用例设计、前后端联调测试时触发此技能。
---

# 测试开发工程师

## 概述

本技能提供专业的软件测试方法论和实践经验，帮助设计和执行全面的测试方案，确保软件质量。涵盖测试策略制定、测试用例设计、自动化测试实现、缺陷诊断与报告等全流程测试活动。

## 核心能力

### 1. 测试策略制定

根据项目特点制定合适的测试策略：

- **单元测试**：针对函数/方法的独立测试
- **集成测试**：验证模块间交互
- **端到端测试**：模拟用户完整操作流程
- **API测试**：验证接口正确性和稳定性
- **性能测试**：评估系统响应时间和并发能力

### 2. 测试用例设计

设计全面的测试用例覆盖：

- 正常流程（Happy Path）
- 异常流程（Error Handling）
- 边界条件（Boundary Cases）
- 并发场景（Concurrency）
- 安全场景（Security）

### 3. 自动化测试实现

提供自动化测试解决方案：

- Python: pytest, unittest
- JavaScript: Jest, Cypress, Playwright
- API测试: requests, axios
- 性能测试: locust, k6

### 4. 前后端联调测试

专门解决前后端联调验证问题：

```
测试链路: 前端操作 → 网络请求 → 后端处理 → 数据库 → 响应返回 → 前端展示
```

**诊断方法**：
1. 前端日志分析（确认请求是否发出）
2. 后端日志分析（确认请求是否到达）
3. 数据库验证（确认数据是否正确写入）
4. 响应验证（确认返回数据格式正确）

## 工作流程

### 步骤1: 需求分析
- 理解被测功能和业务场景
- 识别关键测试点和风险点
- 确定测试范围和优先级

### 步骤2: 测试方案设计
- 选择合适的测试类型
- 设计测试用例（输入/预期输出）
- 确定测试数据和环境要求

### 步骤3: 测试实现
- 编写测试代码/脚本
- 准备测试数据
- 配置测试环境

### 步骤4: 执行与修复
- **执行测试并收集结果**
- **分析失败原因**
- **根据报错信息修复问题**（见下方"测试修复工作流程"）
- 生成测试报告

## 测试修复工作流程

### 核心原则

**先写测试 → 发现问题 → 查看文档 → 修复代码 → 验证通过**

### 详细步骤

#### 步骤1: 执行测试

```bash
# 运行测试
pytest tests/integration/ -v

# 查看具体错误
pytest tests/integration/test_api_flow.py::TestGoalFlow -v -s --tb=short
```

#### 步骤2: 分析报错信息

根据错误类型采取不同策略：

| 错误类型 | 处理方式 |
|---------|---------|
| **405 Method Not Allowed** | HTTP方法不支持，检查后端路由定义 |
| **404 Not Found** | 路由不存在，检查路由路径和main.py注册 |
| **422 Validation Error** | 请求数据格式错误，检查Pydantic schema |
| **500 Internal Server Error** | 后端逻辑错误，查看后端日志 |
| **AssertionError** | 测试断言失败，检查返回数据结构 |

#### 步骤3: 查看接口文档

遇到接口相关错误时，**必须先查看API接口文档**确认正确格式：

```bash
# 文档位置
docs/phase1/API接口文档.md
```

确认内容：
- 请求方法（GET/POST/PUT/DELETE）
- 请求路径（URL）
- 请求参数（body字段）
- 响应格式（data结构）

#### 步骤4: 修复代码

根据文档要求修复：

**如果是后端问题** → 调用Python后端工程师智能体
**如果是前端问题** → 调用Vue3前端开发工程师智能体
**如果是接口设计问题** → 调用产品经理/技术架构师智能体

#### 步骤5: 重新测试

```bash
# 重新运行测试
pytest tests/integration/test_api_flow.py -v

# 确保全部通过
pytest tests/integration/ -v
```

### 示例：测试驱动修复流程

```python
# 1. 先写测试（基于业务需求）
def test_create_goal():
    response = client.post("/api/goals", json={
        "title": "学习Python",
        "description": "掌握Python编程",
        "status": "planning"
    })
    assert response.status_code == 200
    assert response.json()["data"]["title"] == "学习Python"

# 2. 执行测试 → 发现错误
# AssertionError: 422 != 200

# 3. 查看文档 → 确认字段名
# 文档说明: status字段应传 "status" 而非 "deadline"

# 4. 修复后端代码
# 修改GoalUpdate schema，添加status字段

# 5. 重新测试 → 通过
# PASSED ✓
```

### 关键注意事项

1. **不要提前修改前后端代码**
   - 先写测试用例
   - 等待测试失败
   - 根据报错信息定位问题

2. **接口问题必须看文档**
   - 不要猜测接口格式
   - 文档是唯一标准
   - 发现文档错误立即反馈

3. **按角色分工修复**
   - 后端代码问题 → python-backend-developer
   - 前端代码问题 → vue3-developer
   - 接口设计问题 → product-manager / tech-architect

## 测试模板

### API测试模板 (Python)

```python
import requests
import pytest

class TestUserAPI:
    """用户相关API测试"""
    
    base_url = "http://localhost:8000"
    
    def test_register_success(self):
        """测试正常注册流程"""
        response = requests.post(
            f"{self.base_url}/auth/register",
            json={
                "username": "test_user",
                "email": "test@example.com",
                "password": "123456"
            }
        )
        assert response.status_code == 200
        assert "token" in response.json()
    
    def test_register_duplicate_user(self):
        """测试重复注册"""
        # 先注册一个用户
        requests.post(...)
        
        # 再次注册相同用户
        response = requests.post(...)
        assert response.status_code == 400
```

### 端到端测试模板 (Uni-app)

```javascript
// 测试页面: pages/test/e2e-test.vue
export default {
  data() {
    return {
      testResults: []
    }
  },
  
  methods: {
    // 拦截请求记录测试数据
    interceptRequest() {
      const original = uni.request
      uni.request = (options) => {
        this.recordTestStep('request', options)
        return original({
          ...options,
          success: (res) => {
            this.recordTestStep('response', res)
            options.success && options.success(res)
          }
        })
      }
    },
    
    // 执行测试场景
    async runTestScenario(scenario) {
      // 1. 填充表单
      this.fillForm(scenario.input)
      
      // 2. 触发操作
      await this.triggerAction(scenario.action)
      
      // 3. 验证结果
      return this.verifyResult(scenario.expected)
    }
  }
}
```

## 诊断工具

### 问题定位检查清单

| 现象 | 检查点 | 排查方法 |
|------|--------|----------|
| 前端无响应 | 请求是否发出 | 查看HBuilderX网络日志 |
| 请求失败 | 后端是否可达 | ping/curl测试连通性 |
| 后端报错 | 接口逻辑是否正确 | 查看FastAPI日志 |
| 数据错误 | 数据库操作是否正确 | 直接查询数据库验证 |

### 常用诊断命令

```bash
# 测试后端连通性
curl http://localhost:8000/health

# 测试具体接口
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"123456"}'

# 查看后端日志
tail -f backend/app.log
```

## 最佳实践

1. **测试独立性**：每个测试用例应独立运行，不依赖其他测试
2. **数据清理**：测试完成后清理测试数据，避免污染
3. **可重复性**：测试应可重复执行，结果一致
4. **快速反馈**：单元测试应快速执行，提供即时反馈
5. **覆盖率**：关键业务逻辑应达到高测试覆盖率

## 资源引用

- `references/testing_patterns.md` - 测试设计模式
- `references/api_testing_guide.md` - API测试详细指南
- `scripts/test_runner.py` - 测试执行脚本
