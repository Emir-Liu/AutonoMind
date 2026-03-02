"""
时间操作工具类
提供计时器、时间格式化等通用功能
"""
import time
from datetime import datetime, UTC, timezone, timedelta
from typing import Optional


class Timer:
    """
    计时器类,用于计算代码执行耗时
    
    支持手动控制和上下文管理器两种使用方式
    """
    
    def __init__(self, auto_start: bool = True):
        """
        初始化计时器
        
        Args:
            auto_start: 是否自动开始计时,默认True
        """
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.elapsed_time: Optional[float] = None
        
        if auto_start:
            self.start()
    
    def start(self) -> None:
        """开始计时"""
        self.start_time = time.time()
        self.end_time = None
        self.elapsed_time = None
    
    def stop(self) -> float:
        """
        停止计时并返回耗时
        
        Returns:
            耗时(秒)
        """
        if self.start_time is None:
            raise RuntimeError("计时器未启动,请先调用start()方法")
        
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        return self.elapsed_time
    
    def get_start_time_str(self, fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
        """
        获取开始时间的格式化字符串
        
        Args:
            fmt: 时间格式
            
        Returns:
            格式化的时间字符串
        """
        if self.start_time is None:
            return "计时器未启动"
        return time.strftime(fmt, time.localtime(self.start_time))
    
    def get_end_time_str(self, fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
        """
        获取结束时间的格式化字符串
        
        Args:
            fmt: 时间格式
            
        Returns:
            格式化的时间字符串
        """
        if self.end_time is None:
            return "计时器未停止"
        return time.strftime(fmt, time.localtime(self.end_time))
    
    def get_elapsed_time(self) -> float:
        """
        获取耗时(秒)
        
        Returns:
            耗时(秒),如果计时未停止则返回当前已用时间
        """
        if self.start_time is None:
            return 0.0
        
        if self.elapsed_time is not None:
            return self.elapsed_time
        
        return time.time() - self.start_time
    
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.stop()
        return False
    
    def __repr__(self) -> str:
        """返回计时器的字符串表示"""
        return (
            f"Timer(start_time={self.get_start_time_str()}, "
            f"end_time={self.get_end_time_str()}, "
            f"elapsed_time={self.get_elapsed_time():.2f}s)"
        )


def get_iso_timestamp(
    dt: Optional[datetime] = None,
    precision: str = 'seconds'
) -> str:
    """
    获取标准ISO 8601格式时间戳
    
    Args:
        dt: datetime对象,为None则使用当前UTC时间
        precision: 精度 ('seconds', 'milliseconds', 'microseconds')
        
    Returns:
        ISO 8601格式的字符串
    """
    if dt is None:
        dt = datetime.now(UTC)
    
    # 确保是timezone-aware
    if dt.tzinfo is None:
        print(f'警告: 时间戳{dt}未携带时区信息')
    
    # 根据精度格式化
    if precision == 'seconds':
        fmt = '%Y-%m-%dT%H:%M:%S'
    elif precision == 'milliseconds':
        fmt = '%Y-%m-%dT%H:%M:%S.%f'[:-3]
    else:  # microseconds
        fmt = '%Y-%m-%dT%H:%M:%S.%f'
    
    # 生成基础字符串
    base_str = dt.strftime(fmt)
    
    # 判断时区
    if dt.utcoffset() == timedelta(0):
        return f"{base_str}Z"
    else:
        return dt.isoformat()


def get_utc_datetime() -> datetime:
    """
    获取当前UTC时间
    
    Returns:
        当前UTC时间对象
    """
    return datetime.now(UTC)


# 使用示例
if __name__ == '__main__':
    # 方式1: 手动控制
    timer = Timer()
    time.sleep(1)
    elapsed = timer.stop()
    print(f"耗时: {elapsed:.2f}秒")
    
    # 方式2: 上下文管理器
    with Timer() as t:
        time.sleep(2)
        print(f"运行中...")
    print(f"最终耗时: {t.get_elapsed_time():.2f}秒")
    
    # ISO时间戳
    iso_time = get_iso_timestamp()
    print(f'ISO时间: {iso_time}')
