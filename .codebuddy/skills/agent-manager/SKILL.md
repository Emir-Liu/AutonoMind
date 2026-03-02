---
name: Agent管理专家
description: Agent/Skill/Rule全生命周期管理及生态系统管理技能包
version: 2.1.0
updatedAt: 2026-01-28
---

# Agent管理专家技能

## 概述

智能体生态系统管理技能包，涵盖Agent/Skill/Rule的全生命周期管理、关联关系管理、生态系统健康监控和持续进化。

## 核心能力

| 能力 | 说明 |
|------|------|
| Agent管理 | 创建、查看、更新、删除Agent |
| Skill管理 | 创建、查看、更新、删除Skill |
| Rule管理 | 创建、查看、更新、删除Rule |
| 关联管理 | Agent↔Skill↔Rule智能映射 |
| 生态管理 | 健康监控、架构优化 |
| 进化管理 | 经验收集、版本升级 |
| 知识优化 | 质量评估、内容去重 |

## 规范标准

### 命名规范
- **Agent**: `<domain>-<role>` → `python-backend-engineer`
- **Skill**: `<domain>-<specialist>` → `python-backend-developer`
- **Rule**: `<scope>_<purpose>_<type>.mdc` → `agent_butler.mdc`

### Skill目录结构
```
skill-name/
├── SKILL.md          # 技能说明(必需,导入提示词)
├── assets/           # 代码模板(仅引用,不导入)
├── references/       # 参考文档(导入提示词)
└── scripts/          # 脚本工具(可选)
```

### 版本规则
- `MAJOR`: 架构变更
- `MINOR`: 功能新增
- `PATCH`: Bug修复

## 使用示例

### 创建Agent
```python
from assets.agent_creator import AgentCreator

creator = AgentCreator(
    name="数据分析专家",
    role="data-analyst",
    skills=["python-backend-developer"],
    capabilities=["数据分析", "可视化"]
)
agent_path = creator.create_agent()
```

### 创建Skill
```python
from assets.skill_creator import SkillCreator

creator = SkillCreator(
    name="数据分析技能",
    domain="data-analysis"
)
skill_path = creator.create_skill()
```

### 创建Rule
```python
from assets.rule_creator import RuleCreator

creator = RuleCreator(
    name="代码质量规则",
    rule_type="must",
    scope="project"
)
rule_path = creator.create_rule()
```

### 生态系统管理
```python
from assets.ecosystem_manager import EcosystemManager

manager = EcosystemManager()
health = manager.assess_health()  # 评估健康度
report = manager.generate_report()  # 生成报告
manager.optimize()  # 优化生态
```

## 质量检查

- [ ] 命名符合规范
- [ ] 文件位置正确
- [ ] 内容结构完整
- [ ] 版本号已更新
- [ ] 关联关系清晰

## 适用场景

- ✅ 创建/管理Agent、Skill、Rule
- ✅ 管理关联关系网络
- ✅ 监控生态系统健康
- ✅ 收集执行经验
- ✅ 优化知识库
- ✅ 实现自我进化
