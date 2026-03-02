---
name: git-manager
description: 专业的Git仓库管理技能,包含版本控制、分支管理、协作工作流、冲突解决等Git操作知识和最佳实践。适用于代码版本管理、团队协作、发布流程等场景。
---

# Git Manager Skill

Git Manager 技能提供专业的 Git 版本控制管理能力,涵盖从基础操作到高级工作流的完整知识体系。

## 适用场景

当用户需求涉及以下内容时,应使用此技能:
- Git 版本控制操作(提交、推送、拉取等)
- 分支管理(创建、合并、删除等)
- 协作工作流(多团队开发、Code Review等)
- Git 配置优化
- 冲突解决
- 发布管理(标签、版本号等)
- 仓库维护和清理

## 核心工作流程

### 1. 仓库初始化与配置

在开始任何 Git 操作前,确保仓库配置正确:

- 检查 `git config --list` 验证配置
- 设置用户信息: `git config user.name` 和 `git config user.email`
- 创建 `.gitignore` 文件排除不必要的文件
- 初始化仓库: `git init` 或克隆: `git clone`

### 2. 日常开发工作流

遵循标准的三阶段工作流:

**工作区(Working Directory)**:
- 修改文件
- 创建新文件

**暂存区(Staging Area)**:
- `git add <file>` - 添加特定文件
- `git add .` - 添加所有修改
- `git add -p` - 交互式添加,查看每个变更

**本地仓库(Local Repository)**:
- `git commit -m "<message>"` - 提交暂存区内容
- 使用清晰的提交信息格式

### 3. 分支管理策略

**主分支约定**:
- `main/master` - 生产环境代码
- `develop` - 开发环境代码
- `feature/*` - 功能分支
- `hotfix/*` - 紧急修复分支
- `release/*` - 发布准备分支

**分支操作流程**:
1. 从 `develop` 创建 `feature` 分支: `git checkout -b feature/xxx develop`
2. 完成开发后,合并回 `develop`: `git merge feature/xxx`
3. 删除已合并分支: `git branch -d feature/xxx`

### 4. 协作工作流

**Pull Request 工作流**:
1. 推送分支到远程: `git push origin feature/xxx`
2. 创建 Pull Request/Merge Request
3. 请求代码审查
4. 根据反馈修改代码
5. 合并到目标分支
6. 删除远程和本地分支

**多人协作冲突解决**:
1. 先拉取最新代码: `git pull --rebase`
2. 解决冲突: 编辑冲突文件,标记解决
3. 继续变基或合并: `git rebase --continue` 或 `git commit`
4. 推送更新: `git push`

### 5. 发布管理

**版本标签管理**:
- 打标签: `git tag -a v1.0.0 -m "Release version 1.0.0"`
- 推送标签: `git push origin v1.0.0` 或 `git push origin --tags`
- 查看标签: `git tag -l`

**语义化版本**:
- 格式: `MAJOR.MINOR.PATCH`
- MAJOR: 不兼容的 API 变更
- MINOR: 向后兼容的功能新增
- PATCH: 向后兼容的问题修复

### 6. 常用操作参考

**状态查看**:
- `git status` - 查看工作区状态
- `git log` - 查看提交历史
- `git diff` - 查看未暂存的变更
- `git diff --staged` - 查看已暂存的变更

**撤销操作**:
- `git checkout -- <file>` - 撤销工作区修改
- `git reset HEAD <file>` - 取消暂存
- `git reset --soft HEAD~1` - 撤销最后一次提交,保留变更
- `git reset --hard HEAD~1` - 撤销最后一次提交,丢弃变更

**历史管理**:
- `git log --oneline --graph --all` - 图形化查看提交历史
- `git reflog` - 查看引用日志,可恢复误删的提交
- `git cherry-pick <commit>` - 选择性应用提交

## 使用可重用资源

### 脚本 (scripts/)

使用 `scripts/git_wrapper.py` 执行常见 Git 操作:
- 该脚本封装了常用 Git 命令,提供统一接口
- 适用于需要程序化执行 Git 操作的场景
- 支持错误处理和结果验证

### 参考资料 (references/)

- `references/workflows.md` - 详细的 Git 工作流说明
  - Git Flow 工作流
  - GitHub Flow 工作流
  - GitLab Flow 工作流

- `references/best_practices.md` - Git 最佳实践
  - 提交信息规范
  - 分支命名规范
  - 代码审查清单

- `references/troubleshooting.md` - 常见问题解决
  - 冲突解决策略
  - 恢复误删提交
  - 大文件处理

### 资产 (assets/)

- `assets/.gitignore_templates/` - 各种项目的 .gitignore 模板
  - Python 项目模板
  - Node.js 项目模板
  - Vue 项目模板
  - 通用 Web 项目模板

## 执行检查清单

在执行 Git 操作前,确认:
- [ ] 已配置正确的用户信息
- [ ] 当前分支正确
- [ ] 工作区状态清晰
- [ ] 已拉取最新代码(协作场景)
- [ ] 提交信息符合规范
- [ ] 敏感信息已忽略

执行完成后验证:
- [ ] 操作结果符合预期
- [ ] 远程仓库已同步
- [ ] 无遗留冲突
- [ ] 历史记录完整

## 注意事项

1. **永远不要**在 `main/master` 分支上直接提交
2. **永远不要**强制推送 `main/master` 分支: `git push --force`
3. 定期拉取最新代码,减少冲突
4. 遵循团队约定的分支策略
5. 保持提交历史清晰,避免过多的 `git commit --amend`
6. 大文件使用 Git LFS 管理
7. 敏感信息(密钥、密码)不要提交到仓库

## 错误处理

遇到 Git 错误时:
1. 查看详细错误信息: `git <command> --verbose`
2. 检查 `references/troubleshooting.md` 寻找解决方案
3. 使用 `git reflog` 查找历史状态
4. 必要时使用 `git reset` 或 `git revert` 恢复

## 进阶技巧

- 使用 Git Hooks 自动化流程(如提交前检查)
- 配置别名提高效率: `git config --global alias.st status`
- 使用子模块管理依赖
- 利用 Git Bisect 查找引入 bug 的提交
- 使用 Git Filter-branch 或 BFG 清理历史中的敏感信息
