import json
from typing import Any, Dict, Type, TYPE_CHECKING
from .protocol import SerializerProtocol

if TYPE_CHECKING:
    from ...models import BaseRedisModel


class DefaultSerializer(SerializerProtocol):
    """默认序列化器实现，基于 Pydantic 2.0 的序列化能力。
    
    支持的序列化格式：
    - JSON 字符串（默认）
    - JSON 字节
    - 字典（用于 Hash 类型）
    
    Args:
        options: 序列化配置选项
            - mode: 序列化模式，'json' 或 'dict'，默认 'json'
            - by_alias: 是否使用字段别名，默认 False
            - exclude_none: 是否排除 None 值，默认 False
            - exclude_unset: 是否排除未设置的字段，默认 False
            - exclude_defaults: 是否排除默认值，默认 False
            - as_bytes: 是否返回字节格式（仅 json 模式），默认 False
    """
    
    def __init__(self, options: Dict[str, Any] = None):
        """初始化默认序列化器。
        
        Args:
            options: 序列化配置选项
        """
        super().__init__(options)
        self.options = options or {}
        self.mode = self.options.get('mode', 'json')  # 'json' 或 'dict'
        self.by_alias = self.options.get('by_alias', False)
        self.exclude_none = self.options.get('exclude_none', False)
        self.exclude_unset = self.options.get('exclude_unset', False)
        self.exclude_defaults = self.options.get('exclude_defaults', False)
        self.as_bytes = self.options.get('as_bytes', False)
    
    def serialize(self, instance: 'BaseRedisModel') -> bytes | str | Dict[str, Any]:
        """将模型实例序列化为 Redis 可存储的格式。
        
        Args:
            instance: BaseRedisModel 的实例对象
            
        Returns:
            序列化后的数据：
            - mode='json' 且 as_bytes=True: 返回 bytes
            - mode='json' 且 as_bytes=False: 返回 str (JSON 字符串)
            - mode='dict': 返回 Dict[str, Any]
            
        Raises:
            ValueError: 当 mode 不是 'json' 或 'dict' 时
        """
        if self.mode == 'dict':
            # 使用 Pydantic 的 model_dump 方法序列化为字典
            return instance.model_dump(
                by_alias=self.by_alias,
                exclude_none=self.exclude_none,
                exclude_unset=self.exclude_unset,
                exclude_defaults=self.exclude_defaults,
                mode='python'
            )
        elif self.mode == 'json':
            # 使用 Pydantic 的 model_dump_json 方法序列化为 JSON 字符串
            json_str = instance.model_dump_json(
                by_alias=self.by_alias,
                exclude_none=self.exclude_none,
                exclude_unset=self.exclude_unset,
                exclude_defaults=self.exclude_defaults
            )
            # 根据配置返回字节或字符串
            if self.as_bytes:
                return json_str.encode('utf-8')
            return json_str
        else:
            raise ValueError(f"Unsupported serialization modes: {self.mode}, please use 'json' or 'dict'")
    
    def deserialize(self, data: bytes | str | Dict[str, Any], model_class: Type['BaseRedisModel']) -> 'BaseRedisModel':
        """从 Redis 数据反序列化为模型实例。
        
        Args:
            data: 从 Redis 读取的原始数据
                - bytes: JSON 字节数据
                - str: JSON 字符串
                - Dict[str, Any]: 字典数据（来自 Hash）
            model_class: 目标模型类
            
        Returns:
            反序列化后的模型实例
            
        Raises:
            TypeError: 当数据类型不支持时
            ValueError: 当 JSON 解析失败时
        """
        if isinstance(data, dict):
            # 字典数据直接使用 Pydantic 的 model_validate 方法
            return model_class.model_validate(data)
        elif isinstance(data, bytes):
            # 字节数据先解码再使用 model_validate_json
            return model_class.model_validate_json(data.decode('utf-8'))
        elif isinstance(data, str):
            # 尝试作为 JSON 字符串解析
            try:
                # 使用 Pydantic 的 model_validate_json 方法
                return model_class.model_validate_json(data)
            except Exception:
                # 如果不是 JSON，尝试作为字典的字符串表示
                data_dict = json.loads(data)
                return model_class.model_validate(data_dict)
        else:
            raise TypeError(
                f"Unsupported data types: {type(data)}, "
                f"expectation bytes、str or Dict[str, Any]"
            )
