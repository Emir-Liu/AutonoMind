"""
Redis Stream处理器
封装Redis Stream的常用操作,支持消息队列和消费者组模式

使用场景:
- 任务队列
- 消息队列
- 事件流处理
"""
import redis
from typing import Optional, Dict, Any, List, Tuple


class RedisStreamHandler:
    """Redis Stream 操作封装类"""
    
    def __init__(
        self,
        host: str,
        password: str = None,
        port: int = 6379,
        db: int = 0,
        decode_responses: bool = True
    ):
        """
        初始化 Redis 连接
        
        Args:
            host: Redis 服务器地址
            password: Redis 密码(可选)
            port: Redis 端口
            db: 数据库编号
            decode_responses: 是否解码响应
        """
        self.client = redis.Redis(
            host=host,
            password=password,
            port=port,
            db=db,
            decode_responses=decode_responses
        )
    
    def add_message(
        self,
        stream_key: str,
        data: Dict[str, Any]
    ) -> Optional[str]:
        """
        向 Stream 添加消息
        
        Args:
            stream_key: Stream 键名
            data: 消息数据字典
            
        Returns:
            消息 ID,失败返回 None
        """
        try:
            msg_id = self.client.xadd(stream_key, data)
            return msg_id
        except Exception as e:
            print(f'写入失败: {e}')
            return None
    
    def read_messages(
        self,
        stream_key: str,
        start_id: str = '0',
        count: int = 1,
        block_ms: int = 0
    ) -> List[Tuple[str, List[Tuple[str, Dict[str, str]]]]]:
        """
        从 Stream 读取消息
        
        Args:
            stream_key: Stream 键名
            start_id: 起始消息 ID ('0'从头读,'$'读最新的,具体ID从该位置读)
            count: 读取消息数量
            block_ms: 阻塞等待时间(毫秒),0表示不阻塞
            
        Returns:
            读取结果列表 [(stream, [(msg_id, fields), ...]), ...]
        """
        try:
            reply = self.client.xread(
                {stream_key: start_id},
                count=count,
                block=block_ms
            )
            return reply or []
        except Exception as e:
            print(f'读取失败: {e}')
            return []
    
    def read_messages_from_group(
        self,
        stream_key: str,
        consumer_group: str,
        consumer_name: str,
        count: int = 1,
        block_ms: int = 0
    ) -> List:
        """
        从消费者组读取消息(消费者组模式)
        
        Args:
            stream_key: Stream 键名
            consumer_group: 消费者组名称
            consumer_name: 消费者名称
            count: 读取消息数量
            block_ms: 阻塞等待时间(毫秒),0表示不阻塞
            
        Returns:
            读取结果列表 [(stream, [(msg_id, fields), ...]), ...]
        """
        try:
            reply = self.client.xreadgroup(
                groupname=consumer_group,
                consumername=consumer_name,
                streams={stream_key: '>'},  # '>' 表示只读取新消息
                count=count,
                block=block_ms
            )
            return reply or []
        except Exception as e:
            print(f'消费者组读取失败: {e}')
            return []
    
    def ack_message(
        self,
        stream_key: str,
        consumer_group: str,
        message_id: str
    ) -> int:
        """
        确认消息处理完成
        
        Args:
            stream_key: Stream 键名
            consumer_group: 消费者组名称
            message_id: 消息 ID
            
        Returns:
            成功确认的消息数量
        """
        try:
            return self.client.xack(stream_key, consumer_group, message_id)
        except Exception as e:
            print(f'确认消息失败: {e}')
            return 0
    
    def create_consumer_group(
        self,
        stream_key: str,
        group_name: str,
        mkstream: bool = True
    ) -> bool:
        """
        创建消费者组
        
        Args:
            stream_key: Stream 键名
            group_name: 消费者组名称
            mkstream: 如果Stream不存在是否自动创建
            
        Returns:
            创建成功返回True
        """
        try:
            self.client.xgroup_create(
                name=stream_key,
                groupname=group_name,
                id='0',
                mkstream=mkstream
            )
            return True
        except redis.ResponseError as e:
            if 'BUSYGROUP' in str(e):
                print(f'消费者组已存在: {group_name}')
                return True
            print(f'创建消费者组失败: {e}')
            return False
        except Exception as e:
            print(f'创建消费者组失败: {e}')
            return False
    
    def delete_all_messages(self, stream_key: str):
        """
        删除 Stream 所有消息
        
        Args:
            stream_key: Stream 键名
        """
        try:
            self.client.delete(stream_key)
        except Exception as e:
            print(f'删除消息失败: {e}')
    
    def close(self):
        """关闭 Redis 连接"""
        self.client.close()


# 使用示例
if __name__ == '__main__':
    # 创建处理器实例
    handler = RedisStreamHandler(
        host='localhost',
        password='your_password',
        port=6379,
        db=0
    )
    
    # 写入消息
    task_id = handler.add_message('task_stream', {
        'task_id': '123',
        'type': 'validate',
        'data': '{"conversation": "test"}'
    })
    print(f"消息ID: {task_id}")
    
    # 读取消息
    messages = handler.read_messages('task_stream', count=1, block_ms=5000)
    print(f"读取到 {len(messages)} 条消息")
    
    # 使用消费者组
    handler.create_consumer_group('task_stream', 'worker_group')
    group_messages = handler.read_messages_from_group(
        'task_stream',
        'worker_group',
        'consumer_1',
        count=1,
        block_ms=5000
    )
    
    # 关闭连接
    handler.close()
