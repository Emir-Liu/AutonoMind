"""
ID生成工具
提供UUID和业务ID的生成功能
"""
from uuid import uuid4


def generate_uuid() -> str:
    """
    生成UUID
    
    Returns:
        UUID字符串(带连字符)
    """
    return str(uuid4())


def generate_sop_extract_id() -> str:
    """
    生成SOP提取任务ID
    
    Returns:
        任务ID字符串
    """
    return generate_uuid()


def generate_sop_classify_id() -> str:
    """
    生成SOP分类任务ID
    
    Returns:
        任务ID字符串
    """
    return generate_uuid()


def generate_sop_validate_id() -> str:
    """
    生成SOP验证任务ID
    
    Returns:
        任务ID字符串
    """
    return generate_uuid()


# 扩展: 可以根据业务需要添加更多ID生成函数
def generate_task_id(prefix: str = '') -> str:
    """
    生成带前缀的任务ID
    
    Args:
        prefix: ID前缀(可选)
        
    Returns:
        任务ID字符串
    """
    uuid_str = generate_uuid().replace('-', '')
    return f"{prefix}_{uuid_str}" if prefix else uuid_str


# 使用示例
if __name__ == '__main__':
    print(f"UUID: {generate_uuid()}")
    print(f"SOP提取ID: {generate_sop_extract_id()}")
    print(f"SOP分类ID: {generate_sop_classify_id()}")
    print(f"SOP验证ID: {generate_sop_validate_id()}")
    print(f"带前缀ID: {generate_task_id('TASK')}")
