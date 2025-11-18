"""
Integration test demonstrating the primary_key() method usage with FlameModel.
"""
import unittest
from src.flamemodel import FlameModel, fields
from src.flamemodel.models import BaseRedisModel


class TestPrimaryKeyIntegration(unittest.TestCase):
    """Test primary key generation in a real FlameModel context"""

    def test_primary_key_with_flamemodel_initialization(self):
        """Test that primary_key works after FlameModel initialization"""
        
        # Define a model BEFORE initializing FlameModel
        class User(BaseRedisModel):
            __redis_type__ = 'hash'
            __schema__ = 'User'
            id: int = fields(primary_key=True)
            name: str
            email: str
        
        # Initialize FlameModel (this sets up the key_builder)
        client = FlameModel(
            runtime_mode='sync',
            endpoint='redis://localhost:6379/0',
            connect_options={}
        )
        
        # Now we can use primary_key() at class level
        key = User.primary_key(pk=123)
        self.assertEqual(key, 'User:123')
        
        # Test with different pk values
        key2 = User.primary_key(pk=456)
        self.assertEqual(key2, 'User:456')

    def test_custom_key_builder_with_flamemodel(self):
        """Test using custom key builder configuration"""
        
        class Product(BaseRedisModel):
            __redis_type__ = 'hash'
            __schema__ = 'Product'
            id: str = fields(primary_key=True)
            name: str
            price: float
        
        # Initialize FlameModel with custom key builder options
        client = FlameModel(
            runtime_mode='sync',
            endpoint='redis://localhost:6379/0',
            key_builder_cls='src.flamemodel.core.key_builder:DefaultKeyBuilder',
            key_builder_options={'delimiter': '_', 'namespace': 'myapp'}
        )
        
        # The key should use custom delimiter and namespace
        key = Product.primary_key(pk='prod-001')
        self.assertEqual(key, 'myapp_Product_prod-001')

    def test_instance_get_primary_key(self):
        """Test instance-level get_primary_key() method"""
        
        class Order(BaseRedisModel):
            __redis_type__ = 'hash'
            __schema__ = 'Order'
            id: int = fields(primary_key=True)
            customer_id: int
            total: float
        
        # Initialize FlameModel
        client = FlameModel(
            runtime_mode='sync',
            endpoint='redis://localhost:6379/0'
        )
        
        # Create an instance
        order = Order(id=999, customer_id=123, total=99.99)
        
        # Get primary key from instance
        key = order.get_primary_key()
        self.assertEqual(key, 'Order:999')


if __name__ == '__main__':
    # Note: These tests demonstrate the API usage but may fail without a running Redis instance
    # They show how the primary_key() method should be used
    unittest.main()
