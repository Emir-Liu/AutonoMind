"""
文件操作工具类
提供文件的保存、读取、JSON处理等通用功能
"""
import os
from typing import Any
import json


class FileOperator:
    """
    文件操作工具类，支持多种文件格式的保存和读取
    """
    
    @staticmethod
    def get_file_info(file_path: str) -> tuple[str, str, str]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            (文件名, 文件名不含扩展名, 扩展名)
        """
        filename = os.path.basename(file_path)
        name, dot_ext = os.path.splitext(filename)
        ext = dot_ext[1:].lower()
        return filename, name, ext
    
    @staticmethod
    def save_file(
        file_content: bytes | str | dict,
        file_path: str,
        file_name: str | None = None
    ) -> bool:
        """
        保存文件到本地
        
        Args:
            file_content: 文件内容(字节/字符串/字典)
            file_path: 文件保存路径
            file_name: 文件名(可选)
            
        Returns:
            保存成功返回True
        """
        content_type = 'dict'
        if isinstance(file_content, bytes):
            content_type = 'bytes'
        elif isinstance(file_content, str):
            content_type = 'str'
        
        try:
            full_path = os.path.join(file_path, file_name) if file_name else file_path
            os.makedirs(name=os.path.dirname(full_path), exist_ok=True)
            
            if content_type == 'bytes':
                with open(file=full_path, mode='wb') as f:
                    f.write(file_content)
            elif content_type == 'str':
                with open(file=full_path, mode='w', encoding='utf-8') as f:
                    f.write(file_content)
            elif content_type == 'dict':
                with open(file=full_path, mode='w', encoding='utf-8') as f:
                    json.dump(file_content, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False
    
    @staticmethod
    def read_file(
        file_path: str,
        file_name: str | None = None,
        byte: bool = True
    ) -> bytes | str | None:
        """
        从本地读取文件
        
        Args:
            file_path: 文件路径
            file_name: 文件名(可选)
            byte: 是否以字节模式读取(默认True)
            
        Returns:
            文件内容,失败返回None
        """
        try:
            full_path = os.path.join(file_path, file_name) if file_name else file_path
            if byte:
                with open(file=full_path, mode="rb") as f:
                    return f.read()
            else:
                with open(file=full_path, mode="r", encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    
    @staticmethod
    def read_json(
        file_path: str,
        file_name: str | None = None
    ) -> dict[Any, Any] | None:
        """
        读取JSON文件
        
        Args:
            file_path: 文件路径
            file_name: 文件名(可选)
            
        Returns:
            字典内容,失败返回None
        """
        try:
            full_path = os.path.join(file_path, file_name) if file_name else file_path
            with open(file=full_path, mode="r", encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    
    @staticmethod
    def get_file_extension(path: str) -> str:
        """
        获取文件扩展名
        
        Args:
            path: 文件路径
            
        Returns:
            扩展名(小写,不带点)
        """
        return os.path.splitext(path)[-1].lower()[1:]


# 使用示例
if __name__ == '__main__':
    # 保存文本文件
    FileOperator.save_file("Hello World", "./test.txt")
    
    # 保存JSON
    data = {"name": "test", "value": 123}
    FileOperator.save_file(data, "./test.json")
    
    # 读取文件
    content = FileOperator.read_file("./test.txt", byte=False)
    print(content)
    
    # 读取JSON
    json_data = FileOperator.read_json("./test.json")
    print(json_data)
