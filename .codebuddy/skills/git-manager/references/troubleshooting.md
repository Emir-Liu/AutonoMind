# Git 常见问题解决指南

本文档汇总了 Git 使用中常见的问题及其解决方案。

## 目录

- [冲突解决](#冲突解决)
- [恢复误删提交](#恢复误删提交)
- [大文件处理](#大文件处理)
- [远程仓库问题](#远程仓库问题)
- [分支操作问题](#分支操作问题)
- [历史修改](#历史修改)
- [性能问题](#性能问题)

---

## 冲突解决

### 识别冲突

当 Git 无法自动合并时,会标记冲突文件:

```
CONFLICT (content): Merge conflict in src/app.py
```

冲突文件中会包含冲突标记:

```python
<<<<<<< HEAD
def hello():
    return "Hello World"
=======
def hello():
    return "Hello Universe"
>>>>>>> feature/new-greeting
```

### 解决冲突步骤

**1. 查看冲突状态:**
```bash
git status
```

**2. 编辑冲突文件,手动解决冲突:**
- 保留需要的代码
- 删除冲突标记 `<<<<<<<`, `=======`, `>>>>>>>`
- 确保代码逻辑正确

**3. 标记冲突已解决:**
```bash
git add <conflicted-file>
```

**4. 完成合并:**
```bash
git commit
```

### 冲突解决策略

#### 使用本方更改(放弃对方):
```bash
git checkout --ours <file>
git add <file>
```

#### 使用对方更改(放弃本方):
```bash
git checkout --theirs <file>
git add <file>
```

#### 交互式合并:
```bash
git mergetool
```

### 避免冲突

- **定期拉取**: 每天开始工作前拉取最新代码
- **小步提交**: 频繁提交减少冲突范围
- **及时合并**: 功能完成后尽快合并
- **沟通协调**: 多人修改同一文件时提前沟通

---

## 恢复误删提交

### 场景 1: 刚删除的提交,未推送到远程

**使用 git reflog 恢复:**

1. 查看引用日志:
   ```bash
   git reflog
   ```

   输出示例:
   ```
   a1b2c3d HEAD@{0}: commit: Add new feature
   e4f5g6h HEAD@{1}: commit: Fix bug
   ```

2. 恢复到指定提交:
   ```bash
   git reset --hard a1b2c3d
   ```

### 场景 2: 误用 git reset --hard 丢失提交

**恢复被硬重置的提交:**

1. 查看丢失的提交:
   ```bash
   git reflog
   ```

2. 恢复丢失的提交:
   ```bash
   git reset --hard <lost-commit-hash>
   ```

### 场景 3: 已推送到远程,需要恢复

**方案 A: 回退并强制推送(谨慎使用):**

```bash
git reset --hard <target-commit>
git push --force
```

**方案 B: 创建新提交撤销(推荐):**

```bash
git revert <commit-hash>
git push
```

### 场景 4: 误删分支

**恢复已删除的分支:**

1. 查找分支的最后一次提交:
   ```bash
   git reflog | grep "branch: Deleted from"
   ```

2. 重新创建分支:
   ```bash
   git checkout -b <branch-name> <commit-hash>
   ```

### 场景 5: 误删文件

**从历史恢复文件:**

```bash
# 查找文件所在的提交
git log --follow -- <file-path>

# 恢复文件
git checkout <commit-hash> -- <file-path>
git add <file-path>
```

---

## 大文件处理

### 识别大文件

**查找仓库中最大的文件:**
```bash
git rev-list --objects --all |
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' |
  awk '/^blob/ {print substr($0,6)}' |
  sort -nk2 |
  tail -n 10
```

**查看已提交的大文件:**
```bash
git rev-list --objects --all |
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' |
  awk '/^blob/ {if($2 > 1000000) print $0}' |
  sort -nk2
```

### 使用 Git LFS 管理大文件

**安装和初始化 Git LFS:**

```bash
# 安装 Git LFS
brew install git-lfs  # macOS
apt-get install git-lfs  # Linux

# 初始化
git lfs install

# 跟踪大文件类型
git lfs track "*.psd"
git lfs track "*.mp4"
git lfs track "*.zip"

# 提交 .gitattributes
git add .gitattributes
git commit -m "chore: enable git lfs"
```

### 从历史中移除大文件

**使用 BFG Repo-Cleaner(推荐):**

1. 下载 BFG: https://rtyley.github.io/bfg-repo-cleaner/

2. 删除大于 100M 的文件:
   ```bash
   java -jar bfg.jar --strip-blobs-bigger-than 100M repo.git
   ```

3. 删除特定文件:
   ```bash
   java -jar bfg.jar --delete-files large-file.zip repo.git
   ```

4. 清理和优化:
   ```bash
   cd repo.git
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   ```

**使用 git-filter-repo(新推荐):**

```bash
pip install git-filter-repo

# 删除特定文件
git filter-repo --path path/to/large/file --invert-paths

# 删除大于 50M 的文件
git filter-repo --strip-blobs-bigger-than 50M
```

### 减小仓库体积

```bash
# 垃圾回收,释放空间
git gc --aggressive

# 验证仓库
git fsck --full

# 重新打包
git repack -a -d --depth=250 --window=250
```

---

## 远程仓库问题

### 场景 1: 推送被拒绝(non-fast-forward)

**原因**: 远程有新的提交,本地没有

**解决方案**:

```bash
# 方案 A: 拉取并合并
git pull origin master

# 方案 B: 拉取并变基(推荐)
git pull --rebase origin master
```

### 场景 2: 无法连接远程仓库

**诊断网络问题:**

```bash
# 测试连接
ssh -T git@github.com  # GitHub
ssh -T git@gitlab.com  # GitLab

# 检查远程配置
git remote -v

# 更新远程 URL
git remote set-url origin <new-url>
```

**常见问题**:
- SSH 密钥未配置
- 防火墙阻止
- 网络连接问题
- 远程仓库不存在或无权限

### 场景 3: 认证失败

**使用 HTTPS 认证:**

```bash
# 使用 Personal Access Token
git remote set-url origin https://<token>@github.com/user/repo.git

# 或使用凭据存储
git config --global credential.helper store
git push  # 会提示输入用户名和密码,之后会记住
```

**使用 SSH 认证:**

```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 添加到 SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 复制公钥添加到 GitHub/GitLab
cat ~/.ssh/id_ed25519.pub

# 切换到 SSH URL
git remote set-url origin git@github.com:user/repo.git
```

### 场景 4: 远程分支不同步

**删除远程已删除的本地分支引用:**

```bash
git fetch -p
# 或
git remote prune origin
```

**查看远程分支:**

```bash
git branch -r
```

---

## 分支操作问题

### 场景 1: 切换分支时提示未提交的更改

**保留更改后切换:**

```bash
git stash
git checkout target-branch
git stash pop
```

**放弃更改后切换:**

```bash
git checkout -- .
git checkout target-branch
```

**提交更改后切换:**

```bash
git add .
git commit -m "WIP"
git checkout target-branch
```

### 场景 2: 分支命名错误

**重命名当前分支:**

```bash
git branch -m <new-name>
```

**重命名已推送的分支:**

```bash
# 重命名本地分支
git branch -m <old-name> <new-name>

# 删除远程分支
git push origin --delete <old-name>

# 推送新分支
git push origin <new-name>

# 关联新分支
git branch -u origin/<new-name> <new-name>
```

### 场景 3: 分支无法删除

**未合并分支:**

```bash
git branch -D <branch-name>  # 强制删除
```

**包含未推送的提交:**

```bash
# 先推送或创建备份分支
git push origin <branch-name>

# 然后删除
git branch -d <branch-name>
```

### 场景 4: 创建了错误的基础分支

**重新基于正确的分支:**

```bash
# 切换到目标基础分支
git checkout correct-branch

# 从当前提交创建新分支
git checkout -b new-feature

# 删除旧分支
git branch -D old-feature
```

---

## 历史修改

### 场景 1: 修改最后一次提交

**修改提交信息:**

```bash
git commit --amend
```

**添加遗漏的文件:**

```bash
git add forgotten-file
git commit --amend
```

### 场景 2: 修改历史提交

**交互式变基:**

```bash
# 变基最近的 3 个提交
git rebase -i HEAD~3
```

编辑器中:
- `pick` - 保留提交
- `reword` - 修改提交信息
- `edit` - 修改提交内容
- `squash` - 合并到前一个提交
- `drop` - 删除提交

### 场景 3: 合并多次提交

```bash
# 合并最近 3 次提交为 1 次
git reset --soft HEAD~3
git commit -m "Combined commit message"
```

或使用交互式变基将多次提交标记为 `squash`。

### 场景 4: 拆分提交

```bash
# 标记要拆分的提交为 edit
git rebase -i HEAD~3

# 在标记为 edit 的提交处,重置
git reset HEAD~1

# 分别提交
git add file1
git commit -m "First commit"
git add file2
git commit -m "Second commit"

# 继续变基
git rebase --continue
```

### 场景 5: 挑选特定提交

**将其他分支的提交应用到当前分支:**

```bash
git cherry-pick <commit-hash>
```

**挑选多个提交:**

```bash
git cherry-pick <commit1> <commit2> <commit3>
```

**选择范围:**

```bash
git cherry-pick <start-commit>^..<end-commit>
```

---

## 性能问题

### 场景 1: Git 操作很慢

**检查仓库大小:**

```bash
du -sh .git
```

**优化仓库:**

```bash
git gc --aggressive
git repack -a -d
```

### 场景 2: git status 慢

**禁用某些检查(暂时):**

```bash
git status --untracked-files=no
```

**检查是否有大量未跟踪文件:**

```bash
git status
```

**优化 .gitignore:**

添加更多模式到 `.gitignore` 减少未跟踪文件数量。

### 场景 3: git log 慢

**限制输出:**

```bash
git log --max-count=100
```

**使用更简单的格式:**

```bash
git log --oneline --graph --all
```

### 场景 4: 克隆速度慢

**浅克隆:**

```bash
git clone --depth 1 <repo-url>
```

**单分支克隆:**

```bash
git clone --branch <branch-name> --single-branch <repo-url>
```

**使用镜像克隆:**

```bash
git clone --mirror <repo-url>
```

---

## 杂项问题

### .gitignore 不生效

**已跟踪的文件不会被 .gitignore 忽略:**

```bash
# 从跟踪中移除但保留文件
git rm --cached <file>

# 提交删除
git commit -m "Stop tracking file"
```

### 显示奇怪的字符

**配置字符编码:**

```bash
git config --global core.quotePath false
git config --global gui.encoding utf-8
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
```

### 换行符问题

**配置自动转换:**

```bash
# Windows
git config --global core.autocrlf true

# Linux/Mac
git config --global core.autocrlf input

# 或统一使用 LF
git config --global core.eol lf
```

### 忘记配置用户信息

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 或仅为当前仓库配置
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

---

## 获取帮助

**Git 帮助命令:**

```bash
# 查看特定命令帮助
git <command> --help

# 快速参考
git help -g

# 搜索手册
git help --search <keyword>
```

**在线资源:**

- Git 官方文档: https://git-scm.com/doc
- GitHub Git 指南: https://guides.github.com/
- Stack Overflow: https://stackoverflow.com/questions/tagged/git

---

## 总结

遇到 Git 问题时:
1. 保持冷静,不要盲目执行命令
2. 查看错误信息,理解问题原因
3. 备份当前状态(创建备份分支)
4. 尝试解决方案,验证结果
5. 如无法解决,寻求帮助并提供详细信息

记住:大多数 Git 操作都可以撤销,只要你知道正确的命令。
