---
name: file-manager
description: 专业的文件和目录管理专家，精通项目结构组织、文档分类、文件命名规范、目录维护。适用于项目文件整理、文档管理、目录结构优化等场景。
---

# 文件和目录管理技能

## 技能概述

本技能提供完整的文件和目录管理方法论，帮助维护清晰、可维护的项目结构。重点关注文档组织、目录结构、命名规范和文件生命周期管理。

## 使用场景

当满足以下任一条件时，应使用此技能：

- 需要整理项目文件结构
- 需要创建新的文档分类体系
- 需要制定文件命名规范
- 需要迁移或重组文件
- 需要建立文档索引和导航
- 需要维护文档的一致性
- 需要清理冗余或过时文件

---

## 一、项目目录结构规范

### 1.1 标准项目结构

```
LifeManager/
├── .codebuddy/              # 智能体配置（项目内部配置，不删除）
│   ├── agents/              # 智能体定义
│   ├── skills/              # 技能包
│   └── rules/               # 协作规则
│
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic schema
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── tests/              # 后端测试
│   ├── main.py             # 应用入口
│   └── requirements.txt    # 依赖列表
│
├── frontend/                # 前端代码
│   ├── pages/              # 页面组件
│   ├── components/         # 通用组件
│   ├── api/                # API调用
│   ├── store/              # 状态管理
│   └── utils/              # 工具函数
│
├── docs/                    # 项目文档
│   ├── phase1/             # 第一阶段文档（MVP）
│   ├── phase2/             # 第二阶段文档（增强功能）
│   ├── phase3/             # 第三阶段文档（多平台）
│   ├── management/         # 项目管理文档
│   ├── README.md           # 文档导航
│   └── project-rules.md    # 项目规则
│
├── tests/                   # 集成测试
│   ├── integration/        # 集成测试
│   ├── e2e/               # 端到端测试
│   └── TEST_REPORT.md      # 测试报告
│
├── reviews/                 # 代码审查记录
├── logs/                    # 日志文件
├── others/                  # 其他工具脚本
├── README.md                # 项目主文档
└── .gitignore              # Git忽略规则
```

### 1.2 目录命名规范

| 目录类型 | 命名风格 | 示例 | 说明 |
|---------|---------|------|------|
| 代码目录 | 全小写 | `backend/`, `frontend/` | 使用单数形式 |
| 测试目录 | 全小写 | `tests/`, `integration/` | 使用单数形式 |
| 文档目录 | 全小写 | `docs/`, `phase1/` | 使用单数形式 |
| 配置目录 | 全小写 | `.codebuddy/` | 以点开头表示隐藏 |

### 1.3 目录创建原则

- **扁平化优先**: 避免过深的目录层级（建议不超过3层）
- **职责单一**: 每个目录只负责一类内容
- **扩展性**: 预留未来扩展空间
- **可导航**: 目录名应清晰表达其内容

---

## 二、文件命名规范

### 2.1 文件命名风格

| 文件类型 | 命名风格 | 示例 | 说明 |
|---------|---------|------|------|
| 代码文件 | 小写+下划线 | `goal_service.py`, `user_schema.py` | Python使用snake_case |
| Vue文件 | 大驼峰 | `GoalList.vue`, `TaskItem.vue` | 组件名使用PascalCase |
| 配置文件 | 小写+连字符 | `pytest.ini`, `.env.example` | 使用kebab-case或点开头 |
| 文档文件 | 小写+连字符 | `project-rules.md`, `TEST_REPORT.md` | 使用kebab-case |
| 测试文件 | 小写+下划线 | `test_goal_flow.py` | 以`test_`开头 |

### 2.2 文件名最佳实践

#### ✅ 推荐的命名
```bash
# 后端文件
goal_service.py
user_schema.py
auth_router.py

# 前端文件
GoalList.vue
TaskItem.vue
authApi.js

# 文档文件
project-rules.md
TEST_REPORT.md
API接口文档.md

# 测试文件
test_api_flow.py
test_database.py
```

#### ❌ 避免的命名
```bash
# 混合风格（不一致）
GoalService.py (Python应该用snake_case)
goallist.vue (Vue应该用PascalCase)

# 中文命名（不利于跨平台）
用户服务.py
目标列表.vue

# 过于模糊的名字
utils.py (太通用，应具体化)
helper.py (没有说明功能)
```

### 2.3 文件前缀规范

| 前缀 | 用途 | 示例 |
|------|------|------|
| `test_` | 测试文件 | `test_goal_flow.py` |
| `__init__.py` | Python包初始化 | `app/__init__.py` |
| `_` | 私有模块 | `_internal.py` |

---

## 三、文档管理规范

### 3.1 文档分类体系

#### Phase文档（按开发阶段）
```
docs/
├── phase1/                 # MVP阶段
│   ├── 产品需求文档.md
│   ├── API接口文档.md
│   ├── 技术架构设计.md
│   ├── 后端开发指南.md
│   ├── 前端开发指南.md
│   └── UI设计文档.md
│
├── phase2/                 # 增强功能阶段
│   └── (未来添加)
│
└── phase3/                 # 多平台阶段
    └── (未来添加)
```

#### Management文档（项目管理）
```
docs/management/
├── PROJECT_KICKOFF.md      # 项目启动文档
├── PROJECT_PLAN.md         # 项目计划
├── PROJECT_DASHBOARD.md    # 项目仪表板
├── TASK_DECOMPOSITION_EXAMPLE.md  # 任务分解示例
└── TASK_DEPENDENCY_GRAPH.md        # 任务依赖关系图
```

#### 规则文档（全局规范）
```
docs/
├── project-rules.md        # 项目规则（全局）
└── README.md               # 文档导航
```

### 3.2 文档命名约定

| 文档类型 | 命名格式 | 示例 |
|---------|---------|------|
| 项目规则 | `规则名称.md` | `project-rules.md` |
| 项目管理 | `项目_类别.md` (大写) | `PROJECT_PLAN.md` |
| 阶段文档 | `类型名称.md` (中文) | `API接口文档.md` |
| 测试报告 | `类型_REPORT.md` | `TEST_REPORT.md` |

### 3.3 文档内容结构

每个文档应包含：

```markdown
# 文档标题

**文档版本**: x.x.x  
**更新时间**: YYYY-MM-DD  
**维护人**: 角色名

---

## 概述
(简要说明文档目的和内容范围)

---

## 正文内容
(按章节组织)

---

## 附录
(相关链接、参考文档等)
```

---

## 四、文件迁移和重组流程

### 4.1 文件迁移步骤

```bash
1. 分析当前结构
   └── 使用 list_dir 查看目录结构
   
2. 识别问题
   └── 找出混乱、重复、位置不当的文件
   
3. 设计新结构
   └── 参考标准结构，设计重组方案
   
4. 创建新目录
   └── 使用 execute_command 创建目录
   
5. 移动文件
   └── 使用 execute_command 或直接更新路径
   
6. 更新引用
   └── 检查并更新README、文档中的路径引用
   
7. 验证结构
   └── 确认所有文件位置正确，引用有效
```

### 4.2 文件移动命令

```bash
# Windows
mkdir new_folder
move file.md new_folder\

# Unix/Linux
mkdir new_folder
mv file.md new_folder/
```

### 4.3 批量移动文件

```bash
# 移动多个文件到新目录
move file1.md new_folder\
move file2.md new_folder\
move file3.md new_folder\

# 或使用通配符
move *.md new_folder\
```

---

## 五、文档导航和索引

### 5.1 主README

根目录的`README.md`应包含：

```markdown
## 📖 文档导航

- [完整文档目录](docs/README.md)
- [MVP文档导航](docs/phase1/MVP_README.md)
- [快速开始](docs/phase1/MVP_GUIDE.md)
```

### 5.2 docs/README.md

docs目录的`README.md`应包含：

```markdown
## 文档结构

### Phase文档
- [Phase 1 - MVP](phase1/)
- [Phase 2 - 增强功能](phase2/)
- [Phase 3 - 多平台](phase3/)

### 项目管理
- [项目启动](management/PROJECT_KICKOFF.md)
- [项目计划](management/PROJECT_PLAN.md)
- [项目仪表板](management/PROJECT_DASHBOARD.md)

### 规范文档
- [项目规则](project-rules.md)
```

---

## 六、文件维护规则

### 6.1 文件更新

- **及时更新**: 代码变更后同步更新文档
- **版本标记**: 文档头部标注版本和更新时间
- **变更记录**: 重要变更记录在文档末尾

### 6.2 文件删除

删除文件前检查：

```bash
1. 确认文件不再被使用
   └── 使用 search_content 搜索引用
   
2. 检查是否有其他依赖
   └── 查看README、文档中的链接
   
3. 备份重要文件
   └── 特别是设计文档、架构文档
   
4. 安全删除
   └── 使用 delete_file 工具
```

### 6.3 冗余文件处理

识别并处理冗余文件：

| 文件类型 | 处理方式 |
|---------|---------|
| 重复文档 | 合并内容，保留最新的 |
| 过时文档 | 移动到 `archive/` 或删除 |
| 临时文件 | 删除（如 `test.db`, `*.log`） |
| 草稿文件 | 整理或删除 |

---

## 七、常见问题处理

### 7.1 文件混乱的典型表现

- ✗ 同类型文件分散在多个目录
- ✗ 文件命名不一致
- ✗ 目录层级过深或过浅
- ✗ 文档缺乏导航
- ✗ 链接引用失效

### 7.2 整理方案

```bash
1. 统一文件命名风格
   └── 参考"文件命名规范"
   
2. 按类型归类文件
   └── 参考标准项目结构
   
3. 创建文档索引
   └── 在各层目录创建README.md
   
4. 更新所有引用
   └── 确保链接正确
```

### 7.3 检查清单

整理后检查：

- [ ] 所有文件位置合理
- [ ] 命名符合规范
- [ ] 文档导航完整
- [ ] 引用链接有效
- [ ] 无冗余文件
- [ ] README.md更新

---

## 八、工具和命令

### 8.1 查看目录结构

```bash
# Windows
dir /b /s

# 列出目录内容（递归）
list_dir --target_directory="path"
```

### 8.2 搜索文件

```bash
# 按模式搜索文件
search_file --pattern="*.md" --recursive=true

# 搜索内容
search_content --pattern="关键词" --directory="path"
```

### 8.3 文件操作

```bash
# 创建目录
execute_command --command="mkdir new_folder"

# 移动文件
execute_command --command="move file.md new_folder\"

# 删除文件
delete_file --target_file="path/to/file.md"
```

---

## 附录：参考资源

### 最佳实践

- [Unix文件系统层次标准](https://refspecs.linuxfoundation.org/FHS_3.0/)
- [Python项目结构指南](https://docs.python-guide.org/writing/structure/)
- [Vue项目结构规范](https://vuejs.org/style-guide/)

### 工具

- `tree` - 生成目录树
- `find` - 查找文件
- `grep` - 搜索内容
