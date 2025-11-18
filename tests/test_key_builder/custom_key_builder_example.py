"""
Example of implementing a custom KeyBuilder.

This example demonstrates how users can create their own KeyBuilder
by implementing the KeyBuilderProtocol.
"""

from typing import TYPE_CHECKING, List, Any, Dict, Optional, Literal
from src.flamemodel.core.key_builder import KeyBuilderProtocol

if TYPE_CHECKING:
    from src.flamemodel.models import BaseRedisModel
    from src.flamemodel.models.metadata import FieldMetaData


class CustomKeyBuilder(KeyBuilderProtocol):
    """Custom KeyBuilder with different naming conventions.
    
    This example uses a different format:
    - Uppercase model names
    - Underscore as delimiter
    - Different prefix conventions
    
    Examples:
        - Primary key: USER_123
        - Index: USER_INDEX_EMAIL_john@example.com
        - Foreign key: ORDER_123_FK_user
    """

    def __init__(self, delimiter: str = '_', uppercase: bool = True):
        self.delimiter = delimiter
        self.uppercase = uppercase

    def primary_key(
            self,
            *,
            model: 'BaseRedisModel',
            shard_tags: List[str],
            pk: Any,
            pk_field_name: str,
            pk_field_info: Dict[str, 'FieldMetaData']
    ) -> str:
        model_name = self._format_model_name(model)
        parts = [model_name]
        
        if shard_tags:
            parts.extend(shard_tags)
        
        parts.append(str(pk))
        return self.delimiter.join(parts)

    def index_key(
            self,
            *,
            model: 'BaseRedisModel',
            shard_tags: List[str],
            index_fields: List[str],
            index_values: List[Any],
            pk: Any,
            index_fields_info: List[Dict[str, 'FieldMetaData']]
    ) -> str:
        model_name = self._format_model_name(model)
        parts = [model_name, 'INDEX']
        
        if shard_tags:
            parts.extend(shard_tags)
        
        parts.extend(index_fields)
        parts.extend(str(v) for v in index_values)
        
        return self.delimiter.join(parts)

    def unique_key(
            self,
            *,
            model: 'BaseRedisModel',
            shard_tags: List[str],
            unique_fields: List[str],
            unique_values: List[Any],
            pk: Any,
            unique_fields_info: List[Dict[str, 'FieldMetaData']]
    ) -> str:
        model_name = self._format_model_name(model)
        parts = [model_name, 'UNIQUE']
        
        if shard_tags:
            parts.extend(shard_tags)
        
        parts.extend(unique_fields)
        parts.extend(str(v) for v in unique_values)
        
        return self.delimiter.join(parts)

    def foreign_key(
            self,
            *,
            model: 'BaseRedisModel',
            foreign_model: 'BaseRedisModel',
            field_name: str,
            pk: Any,
            foreign_pk: Any
    ) -> str:
        model_name = self._format_model_name(model)
        return self.delimiter.join([
            model_name,
            str(pk),
            'FK',
            field_name
        ])

    def relationship_key(
            self,
            *,
            model: 'BaseRedisModel',
            related_model: 'BaseRedisModel',
            relation_name: str,
            pk: Any,
            relation_type: Literal['one', 'many']
    ) -> str:
        model_name = self._format_model_name(model)
        return self.delimiter.join([
            model_name,
            str(pk),
            'REL',
            relation_name
        ])

    def backref_key(
            self,
            *,
            model: 'BaseRedisModel',
            source_model: 'BaseRedisModel',
            backref_name: str,
            pk: Any,
            source_pk: Any
    ) -> str:
        model_name = self._format_model_name(model)
        return self.delimiter.join([
            model_name,
            str(pk),
            'BACKREF',
            backref_name
        ])

    def hash_field_key(
            self,
            *,
            model: 'BaseRedisModel',
            pk: Any,
            field_name: str
    ) -> str:
        model_name = self._format_model_name(model)
        return self.delimiter.join([model_name, str(pk)])

    def model_collection_key(
            self,
            *,
            model: 'BaseRedisModel',
            shard_tags: Optional[List[str]] = None
    ) -> str:
        model_name = self._format_model_name(model)
        parts = [model_name]
        
        if shard_tags:
            parts.extend(shard_tags)
        
        parts.append('ALL')
        return self.delimiter.join(parts)

    def key_pattern(
            self,
            *,
            model: 'BaseRedisModel',
            pattern_type: Literal['primary', 'index', 'unique', 'foreign', 'relationship'],
            prefix: Optional[str] = None
    ) -> str:
        model_name = self._format_model_name(model)
        parts = [model_name]
        
        if prefix:
            parts.append(prefix)
        
        if pattern_type == 'index':
            parts.append('INDEX')
        elif pattern_type == 'unique':
            parts.append('UNIQUE')
        elif pattern_type == 'foreign':
            parts.extend(['*', 'FK'])
        elif pattern_type == 'relationship':
            parts.extend(['*', 'REL'])
        
        parts.append('*')
        return self.delimiter.join(parts)

    def format_shard_tags(self, shard_tags: List[str]) -> str:
        return self.delimiter.join(str(tag) for tag in shard_tags)

    def parse_key(self, key: str) -> Dict[str, Any]:
        parts = key.split(self.delimiter)
        result = {'model': parts[0]}
        
        if 'INDEX' in parts:
            result['type'] = 'index'
        elif 'UNIQUE' in parts:
            result['type'] = 'unique'
        elif 'FK' in parts:
            result['type'] = 'foreign'
            result['pk'] = parts[1] if len(parts) > 1 else None
        elif 'REL' in parts:
            result['type'] = 'relationship'
            result['pk'] = parts[1] if len(parts) > 1 else None
        elif 'BACKREF' in parts:
            result['type'] = 'backref'
            result['pk'] = parts[1] if len(parts) > 1 else None
        else:
            result['type'] = 'primary'
            result['pk'] = parts[-1] if len(parts) > 1 else None
        
        return result

    def get_namespace(self, model: 'BaseRedisModel') -> str:
        return self._format_model_name(model)

    def _format_model_name(self, model: 'BaseRedisModel') -> str:
        """Format model name based on configuration."""
        name = getattr(model, '__schema__', None) or model.__name__
        return name.upper() if self.uppercase else name


# ===== Usage Example =====

if __name__ == '__main__':
    """
    Example usage in your FlameModel initialization:
    
    from flamemodel import FlameModel
    from custom_key_builder import CustomKeyBuilder
    
    # Initialize FlameModel with custom KeyBuilder
    client = FlameModel(
        runtime_mode='sync',
        endpoint='redis://localhost:6379/0',
        key_builder_cls='path.to.custom_key_builder:CustomKeyBuilder'
    )
    
    # Or pass an instance directly (if API supports it)
    custom_builder = CustomKeyBuilder(delimiter='_', uppercase=True)
    client = FlameModel(
        runtime_mode='sync',
        endpoint='redis://localhost:6379/0',
        key_builder=custom_builder
    )
    """
    
    # Demo the custom key builder
    from src.flamemodel.models import BaseRedisModel
    from src.flamemodel.models.metadata import FieldMetaData
    
    class User(BaseRedisModel):
        __redis_type__ = 'hash'
        __schema__ = 'User'
    
    builder = CustomKeyBuilder()
    
    # Generate various keys
    pk_key = builder.primary_key(
        model=User,
        shard_tags=[],
        pk=123,
        pk_field_name='id',
        pk_field_info={'id': FieldMetaData(primary_key=True)}
    )
    print(f"Primary Key: {pk_key}")  # USER_123
    
    idx_key = builder.index_key(
        model=User,
        shard_tags=[],
        index_fields=['email'],
        index_values=['john@example.com'],
        pk=123,
        index_fields_info=[{'email': FieldMetaData(index=True)}]
    )
    print(f"Index Key: {idx_key}")  # USER_INDEX_EMAIL_john@example.com
    
    fk_key = builder.foreign_key(
        model=User,
        foreign_model=User,
        field_name='manager_id',
        pk=123,
        foreign_pk=456
    )
    print(f"Foreign Key: {fk_key}")  # USER_123_FK_manager_id
