"""
Custom serializer example.

This example demonstrates how to create a custom serializer by implementing the SerializerProtocol.
"""

import json
import pickle
from typing import Any, Dict, Type, TYPE_CHECKING
from src.flamemodel.core.serializer import SerializerProtocol

if TYPE_CHECKING:
    from src.flamemodel.models import BaseRedisModel


class PickleSerializer(SerializerProtocol):
    """A custom serializer that uses Pickle for serialization.

    Note: The data serialized by Pickle is not cross-language and is only applicable to Python.
    Safety issues should be noted when used in a production environment.
    
    Example:
        - Serialization: Serialize Python objects to bytes
        - Deserialization: Deserialize from bytes to a Python object
    """

    def __init__(self, options: Dict[str, Any] = None):
        """Initialize The Pickle Serializer
        
        Args:
            options: Configuration options
                - protocol: Pickle protocol version uses the latest version by default
        """
        super().__init__(options)
        self.options = options or {}
        self.protocol = self.options.get('protocol', pickle.HIGHEST_PROTOCOL)

    def serialize(self, instance: 'BaseRedisModel') -> bytes:
        """Serialize the model instance into bytes using Pickle.

        Args:
            instance: An instance object of BaseRedisModel

        Returns:
            The serialized byte data
        """
        data = instance.model_dump(mode='python')
        return pickle.dumps(data, protocol=self.protocol)

    def deserialize(self, data: bytes | str | Dict[str, Any], model_class: Type['BaseRedisModel']) -> 'BaseRedisModel':
        """Deserialize the Pickle data into a model instance.

        Args:
            data: Byte data serialized by Pickle
            model_class: Target model class

        Returns:
            Deserialized model instances

        Raises:
            TypeError: When the data type is not bytes
        """
        if isinstance(data, bytes):
            unpickled_data = pickle.loads(data)
            return model_class.model_validate(unpickled_data)
        else:
            raise TypeError(f"PickleSerializer only supports bytes type, received: {type(data)}")


class CompactJSONSerializer(SerializerProtocol):
    """Compact JSON serializer, eliminating unnecessary Spaces.

    This serializer generates compact JSON, saving storage space.

    Features
        - No indentation
        - No extra Spaces
        - Ensure ASCII encoding
    Automatically exclude None values
    """

    def __init__(self, options: Dict[str, Any] = None):
        """Initialize the compact JSON serializer.

        Args:
            options: Configuration options
                -ensure_ascii: Whether to ensure ASCII encoding, default True
                -exclude_none: Whether to exclude the None value, default True
                -sort_keys: Whether to sort keys, default False
        """
        super().__init__(options)
        self.options = options or {}
        self.ensure_ascii = self.options.get('ensure_ascii', True)
        self.exclude_none = self.options.get('exclude_none', True)
        self.sort_keys = self.options.get('sort_keys', False)

    def serialize(self, instance: 'BaseRedisModel') -> str:
        """Serialize the model instance into a compact JSON string.

        Args:
            instance: An instance object of BaseRedisModel

        Returns:
            Compact JSON string
        """
        data = instance.model_dump(
            mode='python',
            exclude_none=self.exclude_none
        )
        return json.dumps(
            data,
            ensure_ascii=self.ensure_ascii,
            separators=(',', ':'),  # compact format no spaces
            sort_keys=self.sort_keys
        )

    def deserialize(self, data: bytes | str | Dict[str, Any], model_class: Type['BaseRedisModel']) -> 'BaseRedisModel':
        """Deserialize from JSON data to model instances.

        Args:
            data: JSON string, byte, or dictionary
            model_class: Target model class

        Returns:
            Deserialized model instances
        """
        if isinstance(data, dict):
            return model_class.model_validate(data)
        elif isinstance(data, bytes):
            data_str = data.decode('utf-8')
            return model_class.model_validate_json(data_str)
        elif isinstance(data, str):
            return model_class.model_validate_json(data)
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")


class MsgPackSerializer(SerializerProtocol):
    """MessagePack serializer example (requires msgpack library installation).
    
    MessagePack is an efficient binary serialization format that is more compact than JSON.
    
    Install: pip install msgpack
    
    Features:
        - Binary format
        - Smaller than JSON
        - Faster than JSON
        - Cross-language support
    """

    def __init__(self, options: Dict[str, Any] = None):
        """Initialize MessagePack serializer.
        
        Args:
            options: Configuration options
                - use_bin_type: Whether to use bin type, default True
        """
        super().__init__(options)
        try:
            import msgpack
            self.msgpack = msgpack
        except ImportError:
            raise ImportError(
                "msgpack library is not installed. Please run: pip install msgpack"
            )

        self.options = options or {}
        self.use_bin_type = self.options.get('use_bin_type', True)

    def serialize(self, instance: 'BaseRedisModel') -> bytes:
        """Serialize model instance to bytes using MessagePack.
        
        Args:
            instance: BaseRedisModel instance object
            
        Returns:
            Byte data in MessagePack format
        """
        data = instance.model_dump(mode='python')
        return self.msgpack.packb(data, use_bin_type=self.use_bin_type)

    def deserialize(self, data: bytes | str | Dict[str, Any], model_class: Type['BaseRedisModel']) -> 'BaseRedisModel':
        """Deserialize from MessagePack data to model instance.
        
        Args:
            data: MessagePack byte data or dict
            model_class: Target model class
            
        Returns:
            Deserialized model instance
        """
        if isinstance(data, dict):
            return model_class.model_validate(data)
        elif isinstance(data, bytes):
            unpacked_data = self.msgpack.unpackb(data, raw=False)
            return model_class.model_validate(unpacked_data)
        else:
            raise TypeError(f"MsgPackSerializer supports bytes or dict, received: {type(data)}")


# ===== Usage Example =====

if __name__ == '__main__':
    """
    Example of using custom serializer in FlameModel:
    
    from flamemodel import FlameModel
    from custom_serializer_example import PickleSerializer, CompactJSONSerializer
    
    # Method 1: Initialize via class path
    client = FlameModel(
        runtime_mode='sync',
        endpoint='redis://localhost:6379/0',
        serializer_cls='path.to.custom_serializer:PickleSerializer'
    )
    
    # Method 2: Pass instance directly
    custom_serializer = CompactJSONSerializer(options={'sort_keys': True})
    client = FlameModel(
        runtime_mode='sync',
        endpoint='redis://localhost:6379/0',
        serializer=custom_serializer
    )
    """

    # Demonstrate the use of custom serializer
    from src.flamemodel.models import BaseRedisModel
    from src.flamemodel.models.fields import fields
    from typing import Optional


    class User(BaseRedisModel):
        __redis_type__ = 'hash'
        __schema__ = 'User'
        __key_pattern__ = 'User:{pk}'

        id: int = fields(primary_key=True)
        username: str
        email: str
        age: Optional[int] = None


    # Create user instance
    user = User(id=123, username='johndoe', email='john@example.com', age=30)

    # Test PickleSerializer
    print("=== PickleSerializer ===")
    pickle_serializer = PickleSerializer()
    pickled = pickle_serializer.serialize(user)
    print(f"Pickled (length): {len(pickled)} bytes")
    unpickled = pickle_serializer.deserialize(pickled, User)
    print(f"Unpickled: {unpickled.username}, {unpickled.email}")

    # Test CompactJSONSerializer
    print("\n=== CompactJSONSerializer ===")
    compact_serializer = CompactJSONSerializer()
    compact_json = compact_serializer.serialize(user)
    print(f"Compact JSON: {compact_json}")
    print(f"Length: {len(compact_json)} chars")
    restored = compact_serializer.deserialize(compact_json, User)
    print(f"Restored: {restored.username}, {restored.email}")

    # Compare with normal JSON
    import json

    normal_json = json.dumps(user.model_dump(), indent=2)
    print(f"\nNormal JSON length: {len(normal_json)} chars")
    print(f"Compact JSON length: {len(compact_json)} chars")
    print(f"Space saved: {len(normal_json) - len(compact_json)} chars")
