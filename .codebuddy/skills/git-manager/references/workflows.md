# Git 工作流详解

本文档详细说明三种主流的 Git 工作流程。

## 目录

- [Git Flow 工作流](#git-flow-工作流)
- [GitHub Flow 工作流](#github-flow-工作流)
- [GitLab Flow 工作流](#gitlab-flow-工作流)
- [选择合适的工作流](#选择合适的工作流)

---

## Git Flow 工作流

Git Flow 是 Vincent Driessen 提出的一种分支模型,适用于具有预定发布周期的项目。

### 分支结构

```
master     ──► 生产环境(稳定版本)
  ↓
develop    ──► 开发主分支(最新开发进度)
  ↓
  ├─ feature/*  ──► 功能分支
  ├─ release/*  ──► 发布准备分支
  └─ hotfix/*   ──► 紧急修复分支
```

### 工作流程

#### 1. 功能开发 (Feature)

从 `develop` 创建功能分支:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/user-authentication
```

开发完成后合并回 `develop`:

```bash
git checkout develop
git merge feature/user-authentication
git branch -d feature/user-authentication
git push origin develop
```

#### 2. 发布准备 (Release)

当 `develop` 分支准备好发布时,创建 `release` 分支:

```bash
git checkout develop
git checkout -b release/1.0.0

# 在 release 分支上进行最后测试和修复
# 修复 bug,更新版本号等

# 完成后合并到 master 和 develop
git checkout master
git merge release/1.0.0
git tag -a v1.0.0 -m "Release version 1.0.0"

git checkout develop
git merge release/1.0.0

git branch -d release/1.0.0
```

#### 3. 紧急修复 (Hotfix)

生产环境出现紧急 bug,从 `master` 创建修复分支:

```bash
git checkout master
git checkout -b hotfix/critical-bug-fix

# 修复 bug

# 合并到 master 和 develop
git checkout master
git merge hotfix/critical-bug-fix
git tag -a v1.0.1 -m "Hotfix version 1.0.1"

git checkout develop
git merge hotfix/critical-bug-fix

git branch -d hotfix/critical-bug-fix
```

### 优点

- 明确的分支角色和命名规范
- 支持并行的功能开发
- 支持计划内的发布和紧急修复
- 发布版本和开发进度分离

### 缺点

- 分支复杂,学习成本较高
- 对于持续部署的项目可能过于繁琐
- 需要维护多个长期分支

---

## GitHub Flow 工作流

GitHub Flow 是 GitHub 推荐的简单工作流,适用于持续部署项目。

### 分支结构

```
main/master  ──► 生产环境(始终可部署)
  ↓
  feature/*  ──► 功能分支(从 main 创建)
```

### 工作流程

#### 1. 创建功能分支

从 `main` 创建功能分支:

```bash
git checkout main
git pull origin main
git checkout -b feature/new-dashboard
```

#### 2. 提交更改

常规的提交:

```bash
git add .
git commit -m "Add new dashboard layout"
```

#### 3. 推送并创建 Pull Request

```bash
git push origin feature/new-dashboard
```

在 GitHub 上创建 Pull Request。

#### 4. 代码审查

团队成员审查代码,提出建议,进行讨论。

#### 5. 合并到 main

通过审查后,合并到 `main`:

```bash
git checkout main
git pull origin main
git merge feature/new-dashboard
git branch -d feature/new-dashboard
```

#### 6. 部署

`main` 分支合并后自动部署到生产环境。

### 优点

- 简单直接,易于理解
- 适合持续部署
- Pull Request 流程促进代码审查
- 减少分支管理开销

### 缺点

- 不支持多个发布版本并行
- 对发布周期管理较弱
- 需要完善的 CI/CD 支持

---

## GitLab Flow 工作流

GitLab Flow 结合了 Git Flow 和 GitHub Flow 的优点,支持环境分支。

### 分支结构

```
master     ──► 生产环境
  ↓
develop    ──► 预发布环境(可选)
  ↓
  ↓
staging    ──► 测试环境(可选)
  ↓
feature/*  ──► 功能分支
```

### 工作流程

#### 1. 功能开发

从 `master` 或 `develop` 创建功能分支:

```bash
git checkout master
git checkout -b feature/new-feature

# 开发完成后,创建 Merge Request 到 develop
git push origin feature/new-feature
```

#### 2. 环境分支流程

```
feature/new-feature
  ↓ Merge Request
develop
  ↓ 自动部署到预发布
  ↓ Merge Request
staging
  ↓ 自动部署到测试
  ↓ Merge Request
master
  ↓ 自动部署到生产
```

每个环境分支都有对应的部署环境,合并后自动触发部署。

#### 3. 紧急修复

从 `master` 创建修复分支:

```bash
git checkout master
git checkout -b hotfix/production-bug

# 修复后直接合并到 master
git merge hotfix/production-bug
git tag -a v1.0.1 -m "Hotfix"
```

同时将修复合并回 `develop` 和其他环境分支。

### 优点

- 灵活,可根据项目需要配置
- 支持多环境部署流程
- 结合了 Git Flow 和 GitHub Flow 的优点
- 适合 DevOps 场景

### 缺点

- 配置相对复杂
- 需要完善的 CI/CD 管道
- 环境分支管理需要规范

---

## 选择合适的工作流

### Git Flow 适用于:

- 有明确发布周期的项目(如 2-3 个月一个大版本)
- 需要同时维护多个生产版本
- 大型企业应用
- 传统软件发布模式

### GitHub Flow 适用于:

- 持续部署的项目(如 SaaS 产品)
- Web 应用
- 小型团队
- 需要快速迭代的初创项目

### GitLab Flow 适用于:

- 需要多环境测试的项目
- 微服务架构
- DevOps 环境
- 需要 CI/CD 自动化部署

### 决策因素

1. **团队规模**: 小团队用 GitHub Flow,大团队用 Git Flow
2. **发布频率**: 持续部署用 GitHub Flow,周期发布用 Git Flow
3. **环境复杂度**: 多环境用 GitLab Flow
4. **CI/CD 成熟度**: 成熟用 GitHub/GitLab Flow,不成熟用 Git Flow

### 混合策略

可以根据项目特点自定义工作流:

- 主分支用 GitHub Flow
- 大版本用 Git Flow 的 release 分支
- 多环境部署用 GitLab Flow 的环境分支

---

## 工作流最佳实践

无论选择哪种工作流,都应遵循以下原则:

1. **保持主分支稳定**: main/master 分支应始终可部署
2. **小而频繁的提交**: 避免大而全的提交
3. **代码审查**: 所有更改都应经过审查
4. **自动化测试**: CI/CD 管道中包含测试
5. **分支保护**: 保护主分支,避免直接推送
6. **清晰的提交信息**: 遵循提交信息规范
7. **及时删除已完成分支**: 保持仓库整洁
8. **定期同步**: 定期从主分支拉取最新代码

---

## 工具支持

### Git Flow 工具

```bash
# 安装 git-flow
brew install git-flow-avh  # macOS
apt-get install git-flow   # Ubuntu

# 初始化
git flow init

# 功能分支
git flow feature start feature-name
git flow feature finish feature-name

# 发布分支
git flow release start 1.0.0
git flow release finish 1.0.0

# 修复分支
git flow hotfix start hotfix-name
git flow hotfix finish hotfix-name
```

### GitHub/GitLab 平台集成

- **GitHub**: Pull Request, Branch Protection, Actions
- **GitLab**: Merge Request, Protected Branches, CI/CD Pipelines
- **Gitee**: Pull Request, 分支保护, DevOps

---

## 总结

选择合适的工作流是项目成功的重要因素。根据团队规模、发布频率、环境复杂度等因素选择最适合的工作流,并结合实际情况进行定制化调整。关键是一致性和团队共识。
