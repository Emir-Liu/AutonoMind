"""
任务管理器模板
提供线程池任务管理和任务状态跟踪
"""

import time
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any, Optional
from enum import Enum


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskInfo:
    """任务信息类"""
    
    def __init__(self, task_id: str, future: Future):
        self.task_id = task_id
        self.future = future
        self.status = TaskStatus.PROCESSING
        self.created_at = time.time()
        self.completed_at: Optional[float] = None
        self.error: Optional[str] = None
    
    def mark_completed(self, result: Any = None):
        """标记任务完成"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = time.time()
        self.result = result
    
    def mark_failed(self, error: str):
        """标记任务失败"""
        self.status = TaskStatus.FAILED
        self.completed_at = time.time()
        self.error = error
    
    def get_elapsed_time(self) -> float:
        """获取耗时(秒)"""
        end_time = self.completed_at or time.time()
        return end_time - self.created_at


class TaskWorker:
    """任务工作器，管理线程池和任务执行"""
    
    def __init__(self, max_workers: int = 5):
        """初始化工作器
        
        Args:
            max_workers: 最大工作线程数
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: dict[str, TaskInfo] = {}
        self.running = True
    
    def submit_task(
        self,
        task_id: str,
        process_func: Callable,
        *args,
        **kwargs
    ) -> Future:
        """提交任务到线程池
        
        Args:
            task_id: 任务ID
            process_func: 处理函数
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            Future对象
        """
        if task_id in self.tasks:
            raise ValueError(f"任务ID已存在: {task_id}")
        
        future = self.executor.submit(process_func, *args, **kwargs)
        task_info = TaskInfo(task_id, future)
        self.tasks[task_id] = task_info
        
        # 添加完成回调
        future.add_done_callback(self._on_task_done(task_id))
        
        return future
    
    def _on_task_done(self, task_id: str):
        """任务完成回调"""
        def callback(future: Future):
            try:
                result = future.result()
                self.tasks[task_id].mark_completed(result)
            except Exception as e:
                self.tasks[task_id].mark_failed(str(e))
        return callback
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        task_info = self.tasks.get(task_id)
        return task_info.status if task_info else None
    
    def get_task_info(self, task_id: str) -> Optional[TaskInfo]:
        """获取任务详细信息"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> dict:
        """获取所有任务"""
        return self.tasks.copy()
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task_info = self.tasks.get(task_id)
        if task_info and not task_info.future.done():
            task_info.future.cancel()
            task_info.status = TaskStatus.CANCELLED
            task_info.completed_at = time.time()
            return True
        return False
    
    def shutdown(self, wait: bool = True):
        """关闭工作器
        
        Args:
            wait: 是否等待所有任务完成
        """
        self.running = False
        self.executor.shutdown(wait=wait)
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.shutdown(wait=True)


# 使用示例
if __name__ == "__main__":
    def process_data(data: str):
        time.sleep(2)
        return f"Processed: {data}"
    
    with TaskWorker(max_workers=3) as worker:
        # 提交任务
        task_ids = []
        for i in range(5):
            task_id = f"task_{i}"
            worker.submit_task(task_id, process_data, f"data_{i}")
            task_ids.append(task_id)
        
        # 查询任务状态
        time.sleep(1)
        for tid in task_ids:
            status = worker.get_task_status(tid)
            print(f"{tid}: {status.value}")
        
        # 等待所有任务完成
        time.sleep(3)
        
        # 获取任务信息
        for tid in task_ids:
            info = worker.get_task_info(tid)
            print(f"{tid} - 耗时: {info.get_elapsed_time():.2f}s")
