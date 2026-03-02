# Git 最佳实践

本文档汇总了 Git 使用中的最佳实践,帮助团队建立高效的版本控制流程。

## 目录

- [提交信息规范](#提交信息规范)
- [分支命名规范](#分支命名规范)
- [代码审查清单](#代码审查清单)
- [仓库维护](#仓库维护)
- [团队协作规范](#团队协作规范)
- [安全实践](#安全实践)

---

## 提交信息规范

### Conventional Commits 规范

推荐的提交信息格式:

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type 类型

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式(不影响功能)
- `refactor`: 重构(不是新功能也不是修复)
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具相关
- `ci`: CI/CD 配置

#### Scope 范围

简短的功能模块标识,如:
- `auth`: 认证模块
- `user`: 用户模块
- `api`: API 相关

#### Subject 主题

- 使用祈使句动词开头
- 不超过 50 字符
- 不以句号结尾

示例:
```
feat(auth): add OAuth2 login support

- Implement OAuth2 authentication flow
- Add Google and Facebook providers
- Update user model to store OAuth data

Closes #123
```

### 提交信息示例

**好的提交信息:**
```
fix(user): resolve login session timeout issue

Users were being logged out after 5 minutes instead of 24 hours.
Updated session cookie configuration in app.py.

Fixes #456
```

**不好的提交信息:**
```
fixed bug
update code
done
```

### 提交频率

- **小而频繁**: 每完成一个小的功能点就提交
- **原子性**: 一次提交只做一件事
- **可回滚**: 每个提交都应该可以独立回滚
- **测试通过**: 提交前确保测试通过

### 提交前检查

```bash
# 查看修改
git status
git diff

# 添加相关文件
git add .

# 提交
git commit -m "feat: add new feature"
```

---

## 分支命名规范

### 通用命名规则

- 使用小写字母
- 用连字符 `-` 分隔单词
- 前缀标识分支类型
- 包含描述性名称

### 分支类型前缀

| 前缀 | 用途 | 示例 |
|------|------|------|
| `feature/` | 新功能开发 | `feature/user-authentication` |
| `fix/` 或 `bugfix/` | Bug 修复 | `fix/login-error` |
| `hotfix/` | 生产环境紧急修复 | `hotfix/critical-security` |
| `release/` | 发布准备 | `release/v2.0.0` |
| `docs/` | 文档更新 | `docs/api-documentation` |
| `refactor/` | 代码重构 | `refactor/user-service` |
| `test/` | 测试相关 | `test/add-unit-tests` |
| `chore/` | 杂项工作 | `chore/update-dependencies` |
| `experiment/` | 实验性功能 | `feature/new-ui-experiment` |

### 分支命名示例

**好的命名:**
```
feature/user-profile-page
fix/memory-leak-in-cache
hotfix/security-vulnerability
release/v1.5.0
refactor/database-connection
docs/api-integration-guide
```

**不好的命名:**
```
new-feature
fix-stuff
test-branch
temp
xyz
```

### 分支生命周期

1. **创建**: 从合适的基础分支创建
2. **开发**: 在功能分支上进行开发
3. **测试**: 确保功能正常,测试通过
4. **合并**: 通过 Code Review 后合并
5. **删除**: 合并后删除已完成的分支

---

## 代码审查清单

### Pull Request/Merge Request 前检查

**功能检查:**
- [ ] 功能是否完整实现
- [ ] 是否有明显的 Bug
- [ ] 边界条件是否处理
- [ ] 错误处理是否完善

**代码质量:**
- [ ] 代码风格是否一致
- [ ] 命名是否清晰明确
- [ ] 是否有重复代码
- [ ] 函数/类职责是否单一

**测试检查:**
- [ ] 是否有单元测试
- [ ] 测试覆盖率是否足够
- [ ] 所有测试是否通过
- [ ] 是否有集成测试

**文档检查:**
- [ ] 提交信息是否清晰
- [ ] 是否有必要的注释
- [ ] README 或文档是否更新
- [ ] API 文档是否同步

**性能检查:**
- [ ] 是否有性能问题
- [ ] 是否引入了新的依赖
- [ ] 数据库查询是否优化
- [ ] 资源使用是否合理

**安全检查:**
- [ ] 是否有安全漏洞
- [ ] 敏感信息是否提交
- [ ] 用户输入是否验证
- [ ] 权限控制是否完善

### 代码审查流程

1. **发起 PR/MR**:
   - 清晰描述改动内容和目的
   - 关联相关 Issue
   - 添加必要的截图或演示

2. **审查者反馈**:
   - 提供具体、建设性的反馈
   - 使用代码审查工具的评论功能
   - 大问题 vs 小建议分类标注

3. **作者修改**:
   - 及时响应审查意见
   - 说明修改理由或讨论
   - 更新 PR 描述

4. **批准合并**:
   - 所有主要问题已解决
   - CI/CD 测试通过
   - 获得必要数量的批准

---

## 仓库维护

### .gitignore 配置

**基本原则:**
- 忽略编译产物
- 忽略依赖目录
- 忽略环境配置文件
- 忽略临时文件
- 忽略 IDE 配置

**Python 项目 .gitignore 示例:**
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# 测试
.pytest_cache/
.coverage
htmlcov/
.tox/

# 日志
*.log
logs/

# 数据库
*.db
*.sqlite

# 环境变量
.env
.env.local

# 操作系统
.DS_Store
Thumbs.db
```

**Node.js 项目 .gitignore 示例:**
```
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Production
/dist
/build

# IDE
.vscode/
.idea/
*.swp

# Environment
.env
.env.local

# OS
.DS_Store
Thumbs.db
```

### 仓库清理

**清理未跟踪文件:**
```bash
# 查看将被删除的文件
git clean -n

# 删除未跟踪的文件
git clean -f

# 删除未跟踪的文件和目录
git clean -fd
```

**清理 Git 历史(谨慎使用):**
```bash
# 使用 BFG 清理历史中的大文件
java -jar bfg.jar --strip-blobs-bigger-than 100M repo.git

# 使用 git filter-branch(不推荐,使用 BFG 或 git-filter-repo)
git filter-branch --tree-filter 'rm -f path/to/large/file' HEAD
```

### 仓库优化

```bash
# 垃圾回收,释放空间
git gc

# 验证仓库完整性
git fsck --full

# 重新打包仓库,优化性能
git repack -a -d --depth=250 --window=250
```

### 分支管理

**删除无用分支:**
```bash
# 删除已合并的本地分支
git branch --merged | grep -v "\*" | grep -v master | grep -v develop | xargs -n 1 git branch -d

# 删除远程已删除的本地分支引用
git fetch -p
```

**查看未合并分支:**
```bash
git branch --no-merged
```

---

## 团队协作规范

### 分支保护

**主分支保护规则:**
- 禁止直接推送到 `main/master`/`develop`
- 需要 Pull Request
- 至少 1-2 人批准
- CI/CD 测试必须通过
- 要求代码审查

### Pull Request 流程

1. **从主分支创建功能分支**
   ```bash
   git checkout develop
   git checkout -b feature/new-feature
   ```

2. **开发并提交**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

3. **推送并创建 PR**
   ```bash
   git push origin feature/new-feature
   ```

4. **代码审查**
   - 指定审查者
   - 回馈建议
   - 修改代码

5. **合并到主分支**
   - Squash and merge(推荐)或 Rebase and merge
   - 删除功能分支

### 冲突解决

**预防冲突:**
- 定期从主分支拉取最新代码
- 小而频繁的提交
- 及时合并功能分支
- 避免在功能分支上停留太久

**解决冲突步骤:**

1. 拉取最新代码
   ```bash
   git pull origin develop
   ```

2. 识别冲突文件
   ```bash
   git status
   ```

3. 编辑冲突文件,标记冲突标记 `<<<<<<<`, `=======`, `>>>>>>>`

4. 解决冲突后标记
   ```bash
   git add <conflicted-file>
   ```

5. 完成合并
   ```bash
   git commit
   ```

**使用变基减少冲突:**
```bash
# 在推送前变基
git pull --rebase origin develop
```

### Code Review 责任

**审查者:**
- 及时响应审查请求(24 小时内)
- 提供建设性反馈
- 专注于代码质量而非个人偏好
- 解释拒绝或要求修改的原因

**作者:**
- 清晰描述改动
- 积极响应反馈
- 解释设计决策
- 感谢审查者时间

---

## 安全实践

### 敏感信息保护

**绝对不要提交:**
- API 密钥和 Token
- 数据库密码
- 私钥和证书
- 用户隐私数据
- 配置文件中的敏感信息

**使用环境变量:**
```python
# .env (不提交)
API_KEY=your_api_key_here
DB_PASSWORD=your_password_here

# 代码中读取
import os
api_key = os.getenv("API_KEY")
```

**使用密钥管理服务:**
- HashiCorp Vault
- AWS Secrets Manager
- Google Secret Manager
- Azure Key Vault

### 分支权限

**权限级别:**
- **Read**: 只读,可以克隆和拉取
- **Write**: 可以推送和创建分支
- **Admin**: 可以管理仓库设置和删除分支

**建议配置:**
- 普通成员: Write
- 技术负责人: Admin
- 外部协作者: Read 或 Write

### 提交签名

**配置 GPG 签名:**
```bash
# 生成 GPG 密钥
gpg --full-generate-key

# 列出密钥
gpg --list-secret-keys --keyid-format LONG

# 配置 Git 使用 GPG
git config --global user.signingkey YOUR_KEY_ID
git config --global commit.gpgsign true
```

### 审计日志

**定期检查:**
- Git 仓库访问日志
- 敏感文件访问记录
- 异常的推送操作
- 分支删除记录

---

## 性能优化

### 大文件处理

**使用 Git LFS:**
```bash
# 安装 Git LFS
brew install git-lfs  # macOS
apt-get install git-lfs  # Linux

# 初始化 Git LFS
git lfs install

# 跟踪大文件
git lfs track "*.psd"
git lfs track "*.mp4"

# 提交 .gitattributes
git add .gitattributes
git add .
git commit -m "chore: enable git lfs"
```

### 浅克隆

**克隆最新代码,不需要完整历史:**
```bash
git clone --depth 1 <repo-url>
```

**单分支克隆:**
```bash
git clone --branch <branch-name> --single-branch <repo-url>
```

### Git 配置优化

```bash
# 启用并行操作
git config --global core.packedGitLimit 512m
git config --global core.packedGitWindowSize 32m

# 压缩历史
git config --global gc.auto 256
```

---

## 总结

遵循这些最佳实践可以显著提升团队的 Git 使用效率和代码质量。关键是一致性和持续改进,定期审查和优化团队的工作流程。
