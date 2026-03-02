"""
Git 封装工具 - 提供统一的 Git 操作接口
支持常用 Git 命令的封装、错误处理和结果验证
"""

import subprocess
import os
from typing import Optional, List, Dict, Tuple
from pathlib import Path


class GitWrapper:
    """Git 命令封装类"""

    def __init__(self, repo_path: str = None):
        """
        初始化 Git 封装工具

        Args:
            repo_path: Git 仓库路径,默认为当前目录
        """
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self._validate_git_repo()

    def _validate_git_repo(self):
        """验证当前目录是否为 Git 仓库"""
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            raise ValueError(f"'{self.repo_path}' 不是 Git 仓库")

    def _run_command(self, command: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
        """
        执行 Git 命令

        Args:
            command: Git 命令列表
            capture_output: 是否捕获输出

        Returns:
            (返回码, 标准输出, 错误输出)
        """
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                check=False
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return -1, "", str(e)

    def status(self) -> Dict:
        """
        获取仓库状态

        Returns:
            状态信息字典
        """
        returncode, stdout, stderr = self._run_command(["git", "status", "--porcelain"])
        if returncode != 0:
            return {"error": stderr}

        modified = []
        untracked = []
        staged = []

        for line in stdout.split('\n') if stdout else []:
            if not line:
                continue
            status, filepath = line[:2], line[3:]
            if status == "??":
                untracked.append(filepath)
            elif status in ["M ", "M"]:
                if status.startswith("M"):
                    staged.append(filepath)
                if status.endswith("M"):
                    modified.append(filepath)
            elif status == "A ":
                staged.append(filepath)
            elif status == "D ":
                staged.append(filepath)

        return {
            "modified": modified,
            "untracked": untracked,
            "staged": staged,
            "clean": len(modified) == 0 and len(untracked) == 0 and len(staged) == 0
        }

    def add(self, files: List[str] = None, all_files: bool = False) -> Tuple[bool, str]:
        """
        添加文件到暂存区

        Args:
            files: 文件列表
            all_files: 是否添加所有修改

        Returns:
            (是否成功, 消息)
        """
        if all_files:
            command = ["git", "add", "."]
        elif files:
            command = ["git", "add"] + files
        else:
            return False, "未指定文件或 all_files=True"

        returncode, stdout, stderr = self._run_command(command)
        if returncode != 0:
            return False, stderr or stdout
        return True, "文件已添加到暂存区"

    def commit(self, message: str, amend: bool = False) -> Tuple[bool, str]:
        """
        提交更改

        Args:
            message: 提交信息
            amend: 是否修改最后一次提交

        Returns:
            (是否成功, 消息)
        """
        command = ["git", "commit", "-m", message]
        if amend:
            command.append("--amend")

        returncode, stdout, stderr = self._run_command(command)
        if returncode != 0:
            return False, stderr or stdout
        return True, "提交成功"

    def push(self, remote: str = "origin", branch: str = None, force: bool = False) -> Tuple[bool, str]:
        """
        推送到远程仓库

        Args:
            remote: 远程仓库名称
            branch: 分支名称,默认为当前分支
            force: 是否强制推送

        Returns:
            (是否成功, 消息)
        """
        if not branch:
            returncode, branch_stdout, _ = self._run_command(["git", "branch", "--show-current"])
            branch = branch_stdout

        command = ["git", "push"]
        if force:
            command.append("--force")
        command.extend([remote, branch])

        returncode, stdout, stderr = self._run_command(command)
        if returncode != 0:
            return False, stderr or stdout
        return True, f"已推送 {remote}/{branch}"

    def pull(self, remote: str = "origin", branch: str = None, rebase: bool = False) -> Tuple[bool, str]:
        """
        从远程仓库拉取

        Args:
            remote: 远程仓库名称
            branch: 分支名称
            rebase: 是否使用变基方式拉取

        Returns:
            (是否成功, 消息)
        """
        if not branch:
            returncode, branch_stdout, _ = self._run_command(["git", "branch", "--show-current"])
            branch = branch_stdout

        command = ["git", "pull"]
        if rebase:
            command.append("--rebase")
        command.extend([remote, branch])

        returncode, stdout, stderr = self._run_command(command)
        if returncode != 0:
            return False, stderr or stdout
        return True, f"已从 {remote}/{branch} 拉取最新代码"

    def create_branch(self, branch_name: str, base_branch: str = None) -> Tuple[bool, str]:
        """
        创建新分支

        Args:
            branch_name: 新分支名称
            base_branch: 基础分支,默认为当前分支

        Returns:
            (是否成功, 消息)
        """
        command = ["git", "checkout", "-b", branch_name]
        if base_branch:
            command.extend([base_branch])

        returncode, stdout, stderr = self._run_command(command)
        if returncode != 0:
            return False, stderr or stdout
        return True, f"已创建并切换到分支 {branch_name}"

    def switch_branch(self, branch_name: str) -> Tuple[bool, str]:
        """
        切换分支

        Args:
            branch_name: 目标分支名称

        Returns:
            (是否成功, 消息)
        """
        command = ["git", "checkout", branch_name]

        returncode, stdout, stderr = self._run_command(command)
        if returncode != 0:
            return False, stderr or stdout
        return True, f"已切换到分支 {branch_name}"

    def merge_branch(self, branch_name: str) -> Tuple[bool, str]:
        """
        合并分支

        Args:
            branch_name: 要合并的分支名称

        Returns:
            (是否成功, 消息)
        """
        command = ["git", "merge", branch_name]

        returncode, stdout, stderr = self._run_command(command)
        if returncode != 0:
            return False, stderr or stdout
        return True, f"已合并分支 {branch_name}"

    def delete_branch(self, branch_name: str, force: bool = False) -> Tuple[bool, str]:
        """
        删除分支

        Args:
            branch_name: 分支名称
            force: 是否强制删除

        Returns:
            (是否成功, 消息)
        """
        command = ["git", "branch", "-d" if not force else "-D", branch_name]

        returncode, stdout, stderr = self._run_command(command)
        if returncode != 0:
            return False, stderr or stdout
        return True, f"已删除分支 {branch_name}"

    def create_tag(self, tag_name: str, message: str = None) -> Tuple[bool, str]:
        """
        创建标签

        Args:
            tag_name: 标签名称
            message: 标签说明

        Returns:
            (是否成功, 消息)
        """
        command = ["git", "tag", "-a", tag_name]
        if message:
            command.extend(["-m", message])

        returncode, stdout, stderr = self._run_command(command)
        if returncode != 0:
            return False, stderr or stdout
        return True, f"已创建标签 {tag_name}"

    def push_tag(self, tag_name: str = None) -> Tuple[bool, str]:
        """
        推送标签到远程

        Args:
            tag_name: 标签名称,如果为 None 则推送所有标签

        Returns:
            (是否成功, 消息)
        """
        if tag_name:
            command = ["git", "push", "origin", tag_name]
        else:
            command = ["git", "push", "origin", "--tags"]

        returncode, stdout, stderr = self._run_command(command)
        if returncode != 0:
            return False, stderr or stdout
        return True, "标签已推送"

    def log(self, max_count: int = 10, graph: bool = True) -> List[Dict]:
        """
        获取提交历史

        Args:
            max_count: 最大提交数量
            graph: 是否显示图形

        Returns:
            提交历史列表
        """
        command = ["git", "log", f"-{max_count}", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=iso"]
        if graph:
            command.extend(["--graph", "--all"])

        returncode, stdout, stderr = self._run_command(command)
        if returncode != 0:
            return []

        commits = []
        for line in stdout.split('\n') if stdout else []:
            if not line or line.startswith("*"):
                continue
            parts = line.split('|')
            if len(parts) >= 5:
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "email": parts[2],
                    "date": parts[3],
                    "message": parts[4]
                })

        return commits

    def current_branch(self) -> Optional[str]:
        """
        获取当前分支名称

        Returns:
            分支名称
        """
        returncode, stdout, stderr = self._run_command(["git", "branch", "--show-current"])
        if returncode != 0:
            return None
        return stdout

    def has_conflicts(self) -> bool:
        """
        检查是否有冲突

        Returns:
            是否有冲突
        """
        returncode, stdout, stderr = self._run_command(["git", "diff", "--name-only", "--diff-filter=U"])
        return returncode == 0 and len(stdout) > 0


# 使用示例
if __name__ == "__main__":
    # 初始化 Git 封装工具
    git = GitWrapper()

    # 获取仓库状态
    print("仓库状态:", git.status())

    # 查看当前分支
    print("当前分支:", git.current_branch())

    # 查看最近 5 条提交
    print("最近提交:", git.log(max_count=5))
