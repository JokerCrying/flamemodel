import unittest
from src.flamemodel.core.key_builder import DefaultKeyBuilder, KeyBuilderProtocol
from src.flamemodel.models import BaseRedisModel
from src.flamemodel.models.metadata import FieldMetaData


class MockModel(BaseRedisModel):
    """Mock model for testing"""
    __redis_type__ = 'hash'
    __key_pattern__ = 'User:{pk}'
    __schema__ = 'User'


class TestDefaultKeyBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = DefaultKeyBuilder()
        self.model = MockModel

    def test_is_protocol_compliant(self):
        """Test that DefaultKeyBuilder implements KeyBuilderProtocol"""
        self.assertIsInstance(self.builder, KeyBuilderProtocol)

    def test_primary_key_without_shard(self):
        """Test primary key generation without sharding"""
        key = self.builder.primary_key(
            model=self.model,
            shard_tags=[],
            pk=123,
            pk_field_name='id',
            pk_field_info={'id': FieldMetaData(primary_key=True)}
        )
        self.assertEqual(key, 'User:123')

    def test_primary_key_with_shard(self):
        """Test primary key generation with sharding"""
        key = self.builder.primary_key(
            model=self.model,
            shard_tags=['us-west', 'prod'],
            pk=123,
            pk_field_name='id',
            pk_field_info={'id': FieldMetaData(primary_key=True)}
        )
        self.assertEqual(key, 'User:us-west.prod:123')

    def test_index_key(self):
        """Test index key generation"""
        key = self.builder.index_key(
            model=self.model,
            shard_tags=[],
            index_fields=['email'],
            index_values=['john@example.com'],
            pk=123,
            index_fields_info=[{'email': FieldMetaData(index=True)}]
        )
        self.assertEqual(key, 'User:idx:email:john@example.com')

    def test_composite_index_key(self):
        """Test composite index key generation"""
        key = self.builder.index_key(
            model=self.model,
            shard_tags=[],
            index_fields=['country', 'city'],
            index_values=['US', 'Seattle'],
            pk=123,
            index_fields_info=[
                {'country': FieldMetaData(index=True)},
                {'city': FieldMetaData(index=True)}
            ]
        )
        self.assertEqual(key, 'User:idx:country:city:US:Seattle')

    def test_unique_key(self):
        """Test unique constraint key generation"""
        key = self.builder.unique_key(
            model=self.model,
            shard_tags=[],
            unique_fields=['username'],
            unique_values=['johndoe'],
            pk=123,
            unique_fields_info=[{'username': FieldMetaData(unique=True)}]
        )
        self.assertEqual(key, 'User:uniq:username:johndoe')

    def test_foreign_key(self):
        """Test foreign key generation"""
        key = self.builder.foreign_key(
            model=self.model,
            foreign_model=MockModel,
            field_name='user_id',
            pk=123,
            foreign_pk=456
        )
        self.assertEqual(key, 'User:123:fk:user_id')

    def test_relationship_key(self):
        """Test relationship key generation"""
        key = self.builder.relationship_key(
            model=self.model,
            related_model=MockModel,
            relation_name='orders',
            pk=123,
            relation_type='many'
        )
        self.assertEqual(key, 'User:123:rel:orders')

    def test_backref_key(self):
        """Test backref key generation"""
        key = self.builder.backref_key(
            model=self.model,
            source_model=MockModel,
            backref_name='user',
            pk=123,
            source_pk=456
        )
        self.assertEqual(key, 'User:123:backref:user')

    def test_hash_field_key(self):
        """Test hash field key generation"""
        key = self.builder.hash_field_key(
            model=self.model,
            pk=123,
            field_name='email'
        )
        self.assertEqual(key, 'User:123')

    def test_model_collection_key(self):
        """Test model collection key generation"""
        key = self.builder.model_collection_key(
            model=self.model,
            shard_tags=None
        )
        self.assertEqual(key, 'User:all')

    def test_model_collection_key_with_shard(self):
        """Test model collection key with sharding"""
        key = self.builder.model_collection_key(
            model=self.model,
            shard_tags=['shard1']
        )
        self.assertEqual(key, 'User:shard1:all')

    def test_key_pattern_primary(self):
        """Test primary key pattern generation"""
        pattern = self.builder.key_pattern(
            model=self.model,
            pattern_type='primary'
        )
        self.assertEqual(pattern, 'User:*')

    def test_key_pattern_index(self):
        """Test index key pattern generation"""
        pattern = self.builder.key_pattern(
            model=self.model,
            pattern_type='index'
        )
        self.assertEqual(pattern, 'User:idx:*')

    def test_key_pattern_foreign(self):
        """Test foreign key pattern generation"""
        pattern = self.builder.key_pattern(
            model=self.model,
            pattern_type='foreign'
        )
        self.assertEqual(pattern, 'User:*:fk:*')

    def test_parse_primary_key(self):
        """Test parsing primary key"""
        result = self.builder.parse_key('User:123')
        self.assertEqual(result['model'], 'User')
        self.assertEqual(result['type'], 'primary')
        self.assertEqual(result['pk'], '123')

    def test_parse_index_key(self):
        """Test parsing index key"""
        result = self.builder.parse_key('User:idx:email:john@example.com')
        self.assertEqual(result['model'], 'User')
        self.assertEqual(result['type'], 'index')

    def test_parse_foreign_key(self):
        """Test parsing foreign key"""
        result = self.builder.parse_key('User:123:fk:user_id')
        self.assertEqual(result['model'], 'User')
        self.assertEqual(result['type'], 'foreign')
        self.assertEqual(result['pk'], '123')
        self.assertEqual(result['field'], 'user_id')

    def test_parse_relationship_key(self):
        """Test parsing relationship key"""
        result = self.builder.parse_key('User:123:rel:orders')
        self.assertEqual(result['model'], 'User')
        self.assertEqual(result['type'], 'relationship')
        self.assertEqual(result['pk'], '123')
        self.assertEqual(result['relation'], 'orders')

    def test_namespace_support(self):
        """Test namespace prefix support"""
        namespaced_builder = DefaultKeyBuilder(namespace='myapp')
        key = namespaced_builder.primary_key(
            model=self.model,
            shard_tags=[],
            pk=123,
            pk_field_name='id',
            pk_field_info={'id': FieldMetaData(primary_key=True)}
        )
        self.assertEqual(key, 'myapp:User:123')

    def test_custom_delimiter(self):
        """Test custom delimiter support"""
        custom_builder = DefaultKeyBuilder(delimiter='/')
        key = custom_builder.primary_key(
            model=self.model,
            shard_tags=[],
            pk=123,
            pk_field_name='id',
            pk_field_info={'id': FieldMetaData(primary_key=True)}
        )
        self.assertEqual(key, 'User/123')

    def test_format_shard_tags(self):
        """Test shard tag formatting"""
        tags = self.builder.format_shard_tags(['region1', 'env1', 'tenant1'])
        self.assertEqual(tags, 'region1.env1.tenant1')

    def test_get_namespace(self):
        """Test namespace retrieval"""
        namespace = self.builder.get_namespace(self.model)
        self.assertEqual(namespace, 'User')


if __name__ == '__main__':
    unittest.main()
