import unittest
from src.flamemodel.models import BaseRedisModel
from src.flamemodel.models.metadata import ModelMetadata, FieldMetaData
from src.flamemodel.core.key_builder import DefaultKeyBuilder
from src.flamemodel import fields


class TestPrimaryKeyGeneration(unittest.TestCase):
    """Test primary key generation using KeyBuilder"""

    def setUp(self):
        """Set up test environment"""
        # Create a key builder instance
        self.key_builder = DefaultKeyBuilder()
        
        # Set the key builder for all models
        BaseRedisModel.set_key_builder(self.key_builder)

    def test_class_level_primary_key_generation(self):
        """Test generating primary key at class level"""
        
        class User(BaseRedisModel):
            __redis_type__ = 'hash'
            __schema__ = 'User'
            id: int = fields(primary_key=True)
            name: str
        
        # Set model metadata
        User.__model_meta__ = ModelMetadata(
            pk_info={'id': FieldMetaData(primary_key=True)},
            indexes=[],
            unique_indexes=[],
            shard_tags=[]
        )
        
        # Test class-level key generation
        key = User.primary_key(pk=123)
        self.assertEqual(key, 'User:123')
        
    def test_class_level_primary_key_with_different_pk_values(self):
        """Test generating primary keys with different pk values"""
        
        class Product(BaseRedisModel):
            __redis_type__ = 'hash'
            __schema__ = 'Product'
            id: int = fields(primary_key=True)
            name: str
        
        Product.__model_meta__ = ModelMetadata(
            pk_info={'id': FieldMetaData(primary_key=True)},
            indexes=[],
            unique_indexes=[],
            shard_tags=[]
        )
        
        key1 = Product.primary_key(pk=1)
        key2 = Product.primary_key(pk=999)
        
        self.assertEqual(key1, 'Product:1')
        self.assertEqual(key2, 'Product:999')
        self.assertNotEqual(key1, key2)

    def test_primary_key_without_key_builder_raises_error(self):
        """Test that calling primary_key without key_builder raises error"""
        
        class Order(BaseRedisModel):
            __redis_type__ = 'hash'
            __schema__ = 'Order'
            id: int = fields(primary_key=True)
        
        # Clear the key builder
        Order.__key_builder__ = None
        Order.__model_meta__ = ModelMetadata(
            pk_info={'id': FieldMetaData(primary_key=True)},
            indexes=[],
            unique_indexes=[],
            shard_tags=[]
        )
        
        with self.assertRaises(RuntimeError) as context:
            Order.primary_key(pk=123)
        
        self.assertIn("KeyBuilder has not been set", str(context.exception))

    def test_primary_key_without_pk_raises_error(self):
        """Test that calling primary_key without pk parameter raises error"""
        
        class Cart(BaseRedisModel):
            __redis_type__ = 'hash'
            __schema__ = 'Cart'
            id: int = fields(primary_key=True)
        
        Cart.__model_meta__ = ModelMetadata(
            pk_info={'id': FieldMetaData(primary_key=True)},
            indexes=[],
            unique_indexes=[],
            shard_tags=[]
        )
        
        with self.assertRaises(ValueError) as context:
            Cart.primary_key()
        
        self.assertIn("pk parameter is required", str(context.exception))

    def test_custom_key_builder(self):
        """Test using a custom key builder with different delimiter"""
        
        custom_builder = DefaultKeyBuilder(delimiter='_')
        BaseRedisModel.set_key_builder(custom_builder)
        
        class Customer(BaseRedisModel):
            __redis_type__ = 'hash'
            __schema__ = 'Customer'
            id: int = fields(primary_key=True)
        
        Customer.__model_meta__ = ModelMetadata(
            pk_info={'id': FieldMetaData(primary_key=True)},
            indexes=[],
            unique_indexes=[],
            shard_tags=[]
        )
        
        key = Customer.primary_key(pk=456)
        self.assertEqual(key, 'Customer_456')


if __name__ == '__main__':
    unittest.main()
