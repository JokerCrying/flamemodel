import unittest
from typing import Optional
from src.flamemodel.core.serializer import DefaultSerializer, SerializerProtocol
from src.flamemodel.models import BaseRedisModel
from src.flamemodel.models.fields import fields
from pydantic import Field


class MockUser(BaseRedisModel):
    """Mock user model for testing"""
    __redis_type__ = 'hash'
    __key_pattern__ = 'User:{pk}'
    __schema__ = 'User'
    
    id: int = fields(primary_key=True)
    username: str
    email: str
    age: Optional[int] = None
    is_active: bool = True


class MockProduct(BaseRedisModel):
    """Mock product model for testing"""
    __redis_type__ = 'string'
    __key_pattern__ = 'Product:{pk}'
    __schema__ = 'Product'
    
    id: str = fields(primary_key=True)
    name: str
    price: float
    description: Optional[str] = None


class TestDefaultSerializer(unittest.TestCase):
    def setUp(self):
        """Setup before each test"""
        self.serializer = DefaultSerializer()
        self.user_data = {
            'id': 123,
            'username': 'johndoe',
            'email': 'john@example.com',
            'age': 30,
            'is_active': True
        }
        self.user_instance = MockUser(**self.user_data)

    def test_is_protocol_compliant(self):
        """Test that DefaultSerializer implements SerializerProtocol"""
        self.assertIsInstance(self.serializer, SerializerProtocol)

    def test_serialize_to_json_string(self):
        """Test serialization to JSON string (default mode)"""
        result = self.serializer.serialize(self.user_instance)
        
        self.assertIsInstance(result, str)
        self.assertIn('johndoe', result)
        self.assertIn('john@example.com', result)

    def test_serialize_to_json_bytes(self):
        """Test serialization to JSON bytes"""
        serializer = DefaultSerializer(options={'mode': 'json', 'as_bytes': True})
        result = serializer.serialize(self.user_instance)
        
        self.assertIsInstance(result, bytes)
        self.assertIn(b'johndoe', result)

    def test_serialize_to_dict(self):
        """Test serialization to dict (for Hash type)"""
        serializer = DefaultSerializer(options={'mode': 'dict'})
        result = serializer.serialize(self.user_instance)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['username'], 'johndoe')
        self.assertEqual(result['email'], 'john@example.com')
        self.assertEqual(result['age'], 30)

    def test_serialize_exclude_none(self):
        """Test serialization excluding None values"""
        user_with_none = MockUser(
            id=456,
            username='janedoe',
            email='jane@example.com',
            age=None  # None value
        )
        serializer = DefaultSerializer(options={'mode': 'dict', 'exclude_none': True})
        result = serializer.serialize(user_with_none)
        
        self.assertNotIn('age', result)
        self.assertIn('username', result)

    def test_serialize_exclude_unset(self):
        """Test serialization excluding unset fields"""
        # Don't set age when creating instance
        user_minimal = MockUser(
            id=789,
            username='bobsmith',
            email='bob@example.com'
        )
        serializer = DefaultSerializer(options={'mode': 'dict', 'exclude_unset': True})
        result = serializer.serialize(user_minimal)
        
        self.assertIn('username', result)
        self.assertNotIn('is_active', result)

    def test_serialize_exclude_defaults(self):
        """Test serialization excluding default values"""
        serializer = DefaultSerializer(options={'mode': 'dict', 'exclude_defaults': True})
        result = serializer.serialize(self.user_instance)
        
        # is_active has default value True and instance value is also True, should be excluded
        self.assertNotIn('is_active', result)

    def test_deserialize_from_dict(self):
        """Test deserialization from dict"""
        data = {
            'id': 999,
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 25,
            'is_active': False
        }
        result = self.serializer.deserialize(data, MockUser)
        
        self.assertIsInstance(result, MockUser)
        self.assertEqual(result.id, 999)
        self.assertEqual(result.username, 'testuser')
        self.assertEqual(result.email, 'test@example.com')
        self.assertEqual(result.age, 25)
        self.assertEqual(result.is_active, False)

    def test_deserialize_from_json_string(self):
        """Test deserialization from JSON string"""
        json_str = '{"id": 888, "username": "jsonuser", "email": "json@example.com", "age": 35, "is_active": true}'
        result = self.serializer.deserialize(json_str, MockUser)
        
        self.assertIsInstance(result, MockUser)
        self.assertEqual(result.id, 888)
        self.assertEqual(result.username, 'jsonuser')

    def test_deserialize_from_bytes(self):
        """Test deserialization from bytes"""
        json_bytes = b'{"id": 777, "username": "byteuser", "email": "byte@example.com", "age": 40, "is_active": true}'
        result = self.serializer.deserialize(json_bytes, MockUser)
        
        self.assertIsInstance(result, MockUser)
        self.assertEqual(result.id, 777)
        self.assertEqual(result.username, 'byteuser')

    def test_serialize_deserialize_roundtrip_json(self):
        """Test serialize-deserialize roundtrip in JSON mode"""
        serializer = DefaultSerializer(options={'mode': 'json'})
        
        # Serialize
        serialized = serializer.serialize(self.user_instance)
        # Deserialize
        deserialized = serializer.deserialize(serialized, MockUser)
        
        self.assertEqual(deserialized.id, self.user_instance.id)
        self.assertEqual(deserialized.username, self.user_instance.username)
        self.assertEqual(deserialized.email, self.user_instance.email)
        self.assertEqual(deserialized.age, self.user_instance.age)

    def test_serialize_deserialize_roundtrip_dict(self):
        """Test serialize-deserialize roundtrip in dict mode"""
        serializer = DefaultSerializer(options={'mode': 'dict'})
        
        # Serialize
        serialized = serializer.serialize(self.user_instance)
        # Deserialize
        deserialized = serializer.deserialize(serialized, MockUser)
        
        self.assertEqual(deserialized.id, self.user_instance.id)
        self.assertEqual(deserialized.username, self.user_instance.username)

    def test_serialize_deserialize_roundtrip_bytes(self):
        """Test serialize-deserialize roundtrip in bytes mode"""
        serializer = DefaultSerializer(options={'mode': 'json', 'as_bytes': True})
        
        # Serialize
        serialized = serializer.serialize(self.user_instance)
        # Deserialize
        deserialized = serializer.deserialize(serialized, MockUser)
        
        self.assertEqual(deserialized.id, self.user_instance.id)
        self.assertEqual(deserialized.username, self.user_instance.username)

    def test_serialize_with_invalid_mode(self):
        """Test using invalid serialization mode"""
        serializer = DefaultSerializer(options={'mode': 'invalid'})
        
        with self.assertRaises(ValueError) as context:
            serializer.serialize(self.user_instance)
        
        self.assertIn('Unsupported serialization modes', str(context.exception))

    def test_deserialize_with_invalid_type(self):
        """Test deserialization with invalid data type"""
        with self.assertRaises(TypeError) as context:
            self.serializer.deserialize(12345, MockUser)  # Integer not supported
        
        self.assertIn('Unsupported data types', str(context.exception))

    def test_serialize_product_model(self):
        """Test serialization of different model types"""
        product = MockProduct(
            id='PROD-001',
            name='Laptop',
            price=999.99,
            description='High-performance laptop'
        )
        
        serializer = DefaultSerializer(options={'mode': 'dict'})
        result = serializer.serialize(product)
        
        self.assertEqual(result['id'], 'PROD-001')
        self.assertEqual(result['name'], 'Laptop')
        self.assertEqual(result['price'], 999.99)

    def test_default_options(self):
        """Test default options"""
        serializer = DefaultSerializer()
        
        self.assertEqual(serializer.mode, 'json')
        self.assertEqual(serializer.by_alias, False)
        self.assertEqual(serializer.exclude_none, False)
        self.assertEqual(serializer.exclude_unset, False)
        self.assertEqual(serializer.exclude_defaults, False)
        self.assertEqual(serializer.as_bytes, False)

    def test_custom_options(self):
        """Test custom options"""
        options = {
            'mode': 'dict',
            'by_alias': True,
            'exclude_none': True,
            'exclude_unset': True,
            'exclude_defaults': True,
            'as_bytes': True
        }
        serializer = DefaultSerializer(options=options)
        
        self.assertEqual(serializer.mode, 'dict')
        self.assertEqual(serializer.by_alias, True)
        self.assertEqual(serializer.exclude_none, True)
        self.assertEqual(serializer.exclude_unset, True)
        self.assertEqual(serializer.exclude_defaults, True)
        self.assertEqual(serializer.as_bytes, True)

    def test_serialize_with_none_values(self):
        """Test serialization with None values"""
        user = MockUser(
            id=111,
            username='testuser',
            email='test@example.com',
            age=None
        )
        
        # Don't exclude None
        serializer = DefaultSerializer(options={'mode': 'dict'})
        result = serializer.serialize(user)
        self.assertIn('age', result)
        self.assertIsNone(result['age'])
        
        # Exclude None
        serializer_exclude = DefaultSerializer(options={'mode': 'dict', 'exclude_none': True})
        result_exclude = serializer_exclude.serialize(user)
        self.assertNotIn('age', result_exclude)


if __name__ == '__main__':
    unittest.main()
