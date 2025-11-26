"""
Pickle Serializer Example

This example demonstrates how to create and use a custom serializer using Python's pickle module
with the FlameModel framework.

The PickleSerializer provides a way to serialize model instances using Python's built-in pickle
module, which offers efficient binary serialization but is Python-specific.
"""

import asyncio
import os
import sys
from typing import Optional

# Add the src directory to the path so we can import flamemodel
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.flamemodel.models import BaseRedisModel
from src.flamemodel.models.fields import fields


class User(BaseRedisModel):
    """Example model representing a user."""
    __redis_type__ = 'hash'
    __schema__ = 'User'
    __key_pattern__ = 'User:{pk}'

    id: int = fields(primary_key=True)
    username: str
    email: str
    age: Optional[int] = None


class PickleSerializer:
    """A custom serializer that uses Pickle for serialization.

    Note: The data serialized by Pickle is not cross-language and is only applicable to Python.
    Safety issues should be noted when used in a production environment.
    
    Example:
        - Serialization: Serialize Python objects to bytes
        - Deserialization: Deserialize from bytes to a Python object
    """

    def __init__(self, options=None):
        """Initialize The Pickle Serializer
        
        Args:
            options: Configuration options
                - protocol: Pickle protocol version uses the latest version by default
        """
        import pickle
        self.pickle = pickle
        self.options = options or {}
        self.protocol = self.options.get('protocol', pickle.HIGHEST_PROTOCOL)

    def serialize(self, instance: BaseRedisModel) -> bytes:
        """Serialize the model instance into bytes using Pickle.

        Args:
            instance: An instance object of BaseRedisModel

        Returns:
            The serialized byte data
        """
        data = instance.model_dump(mode='python')
        return self.pickle.dumps(data, protocol=self.protocol)

    def deserialize(self, data: bytes, model_class) -> BaseRedisModel:
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
            unpickled_data = self.pickle.loads(data)
            return model_class.model_validate(unpickled_data)
        else:
            raise TypeError(f"PickleSerializer only supports bytes type, received: {type(data)}")


async def main():
    """Run the Pickle serializer example."""
    # Initialize FlameModel with custom serializer
    # In practice, you would use a real Redis instance
    # For this example, we'll show how to configure it
    print("Pickle Serializer Example")
    print("=" * 30)

    # Create a custom serializer instance
    custom_serializer = PickleSerializer()

    # Show how to initialize FlameModel with the custom serializer
    # Note: We're not connecting to Redis in this example to keep it simple
    print("1. Creating custom serializer instance:")
    print(f"   Created PickleSerializer with protocol {custom_serializer.protocol}")

    # Create a sample user model
    user = User(id=123, username='johndoe', email='john@example.com', age=30)
    print("\n2. Creating sample user model:")
    print(f"   User: {user.username}, Email: {user.email}, Age: {user.age}")

    # Serialize the user
    serialized_data = custom_serializer.serialize(user)
    print("\n3. Serializing user with Pickle:")
    print(f"   Serialized data length: {len(serialized_data)} bytes")

    # Deserialize the user
    deserialized_user = custom_serializer.deserialize(serialized_data, User)
    print("\n4. Deserializing user from Pickle:")
    print(f"   Deserialized user: {deserialized_user.username}, "
          f"Email: {deserialized_user.email}, Age: {deserialized_user.age}")

    # Verify the data is the same
    print("\n5. Verification:")
    print(f"   Username match: {user.username == deserialized_user.username}")
    print(f"   Email match: {user.email == deserialized_user.email}")
    print(f"   Age match: {user.age == deserialized_user.age}")

    # Show how to use with FlameModel (conceptual)
    print("\n6. Integration with FlameModel:")
    print("   # Initialize FlameModel with custom serializer")
    print("   # client = FlameModel(")
    print("   #     runtime_mode='async',")
    print("   #     endpoint='redis://localhost:6379/0',")
    print("   #     serializer=custom_serializer")
    print("   # )")

    print("\nExample completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
