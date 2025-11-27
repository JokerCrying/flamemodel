from typing import TYPE_CHECKING, List, Any, Dict, Optional, Literal, Type, Union
from ...constant import RedisKeyDelimiter
from .protocol import KeyBuilderProtocol

if TYPE_CHECKING:
    from ...models import BaseRedisModel
    from ...models.metadata import FieldMetaData


class DefaultKeyBuilder(KeyBuilderProtocol):
    """Default implementation of KeyBuilderProtocol.
    
    Uses a hierarchical key structure with colon (:) as delimiter.
    Format: ModelName:shard_tags:key_type:identifiers
    
    Examples:
        - Primary key: User:123
        - With shard: User:shard1:123
        - Index: User:idx:email:john@example.com
        - Foreign key: Order:123:fk:user
        - Relationship: User:123:rel:orders
    """

    def __init__(self, delimiter: str = RedisKeyDelimiter, namespace: Optional[str] = None):
        """Initialize the key builder.
        
        Args:
            delimiter: Character to separate key segments (default: ':')
            namespace: Optional global namespace prefix for all keys
        """
        self.delimiter = delimiter
        self.namespace = namespace

    def primary_key(
            self,
            *,
            model: 'BaseRedisModel',
            shard_tags: List[str],
            pk: Any,
            pk_field_name: str,
            pk_field_info: Dict[str, 'FieldMetaData']
    ) -> str:
        pattern = getattr(model, '__key_pattern__', None)
        if pattern and not shard_tags:
            placeholders = {'pk': pk, pk_field_name: pk}
            key = pattern.format(**placeholders)
            if self.namespace:
                return f"{self.namespace}{self.delimiter}{key}"
            return key
        parts = [self._get_model_name(model)]
        if shard_tags:
            parts.append(self.format_shard_tags(shard_tags))
        parts.append(str(pk))
        return self._join_parts(parts)

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
        """Build index key: ModelName[:shard_tags]:idx:field1[:field2...]:value1[:value2...]"""
        parts = [self._get_model_name(model)]

        if shard_tags:
            parts.append(self.format_shard_tags(shard_tags))

        parts.append('idx')

        # Add field names
        parts.extend(index_fields)

        # Add values
        parts.extend(str(val) for val in index_values)

        return self._join_parts(parts)

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
        """Build unique key: ModelName[:shard_tags]:uniq:field1[:field2...]:value1[:value2...]"""
        parts = [self._get_model_name(model)]

        if shard_tags:
            parts.append(self.format_shard_tags(shard_tags))

        parts.append('uniq')

        # Add field names
        parts.extend(unique_fields)

        # Add values
        parts.extend(str(val) for val in unique_values)

        return self._join_parts(parts)

    def foreign_key(
            self,
            *,
            model: 'BaseRedisModel',
            foreign_model: 'BaseRedisModel',
            field_name: str,
            pk: Any,
            foreign_pk: Any
    ) -> str:
        """Build foreign key: ModelName:pk:fk:field_name"""
        parts = [
            self._get_model_name(model),
            str(pk),
            'fk',
            field_name
        ]
        return self._join_parts(parts)

    def relationship_key(
            self,
            *,
            model: 'BaseRedisModel',
            related_model: 'BaseRedisModel',
            relation_name: str,
            pk: Any,
            relation_type: Literal['one', 'many']
    ) -> str:
        """Build relationship key: ModelName:pk:rel:relation_name"""
        parts = [
            self._get_model_name(model),
            str(pk),
            'rel',
            relation_name
        ]
        return self._join_parts(parts)

    def backref_key(
            self,
            *,
            model: 'BaseRedisModel',
            source_model: 'BaseRedisModel',
            backref_name: str,
            pk: Any,
            source_pk: Any
    ) -> str:
        """Build backref key: ModelName:pk:backref:backref_name"""
        parts = [
            self._get_model_name(model),
            str(pk),
            'backref',
            backref_name
        ]
        return self._join_parts(parts)

    def hash_field_key(
            self,
            *,
            model: 'BaseRedisModel',
            pk: Any,
            field_name: str
    ) -> str:
        pattern = getattr(model, '__key_pattern__', None)
        if pattern:
            pk_field_name = list(model.__model_meta__.pk_info.keys())[0]
            placeholders = {'pk': pk, pk_field_name: pk}
            key = pattern.format(**placeholders)
            if self.namespace:
                return f"{self.namespace}{self.delimiter}{key}"
            return key
        parts = [self._get_model_name(model), str(pk)]
        return self._join_parts(parts)

    def model_collection_key(
            self,
            *,
            model: 'BaseRedisModel',
            shard_tags: Optional[List[str]] = None
    ) -> str:
        """Build collection key: ModelName[:shard_tags]:all"""
        parts = [self._get_model_name(model)]

        if shard_tags:
            parts.append(self.format_shard_tags(shard_tags))

        parts.append('all')

        return self._join_parts(parts)

    def key_pattern(
            self,
            *,
            model: 'BaseRedisModel',
            pattern_type: Literal['primary', 'index', 'unique', 'foreign', 'relationship'],
            prefix: Optional[str] = None
    ) -> str:
        """Build key pattern for scanning: ModelName:pattern_type:*"""
        parts = [self._get_model_name(model)]

        if prefix:
            parts.append(prefix)

        if pattern_type == 'primary':
            parts.append('*')
        elif pattern_type == 'index':
            parts.extend(['idx', '*'])
        elif pattern_type == 'unique':
            parts.extend(['uniq', '*'])
        elif pattern_type == 'foreign':
            parts.extend(['*', 'fk', '*'])
        elif pattern_type == 'relationship':
            parts.extend(['*', 'rel', '*'])

        return self._join_parts(parts)

    def format_shard_tags(
            self,
            shard_tags: List[str]
    ) -> str:
        """Format shard tags: tag1.tag2.tag3 (uses dot for shard separation)"""
        return '.'.join(str(tag) for tag in shard_tags)

    def parse_key(
            self,
            key: str
    ) -> Dict[str, Any]:
        """Parse a Redis key into its components.
        
        Returns:
            Dict with keys: model, pk, type, fields (if applicable)
        """
        # Remove namespace if present
        if self.namespace and key.startswith(f"{self.namespace}{self.delimiter}"):
            key = key[len(self.namespace) + len(self.delimiter):]

        parts = key.split(self.delimiter)
        result = {'model': parts[0]}

        if len(parts) < 2:
            return result

        # Check for special key types
        if 'idx' in parts:
            idx_pos = parts.index('idx')
            result['type'] = 'index'
            result['pk'] = None  # Index keys don't directly contain pk
        elif 'uniq' in parts:
            uniq_pos = parts.index('uniq')
            result['type'] = 'unique'
            result['pk'] = None
        elif 'fk' in parts:
            fk_pos = parts.index('fk')
            result['type'] = 'foreign'
            result['pk'] = parts[1] if len(parts) > 1 else None
            result['field'] = parts[fk_pos + 1] if len(parts) > fk_pos + 1 else None
        elif 'rel' in parts:
            rel_pos = parts.index('rel')
            result['type'] = 'relationship'
            result['pk'] = parts[1] if len(parts) > 1 else None
            result['relation'] = parts[rel_pos + 1] if len(parts) > rel_pos + 1 else None
        elif 'backref' in parts:
            backref_pos = parts.index('backref')
            result['type'] = 'backref'
            result['pk'] = parts[1] if len(parts) > 1 else None
            result['backref'] = parts[backref_pos + 1] if len(parts) > backref_pos + 1 else None
        else:
            # Primary key format
            result['type'] = 'primary'
            result['pk'] = parts[-1]

        return result

    def get_namespace(
            self,
            model: 'BaseRedisModel'
    ) -> str:
        """Get the namespace for a model."""
        if self.namespace:
            return self.namespace
        # Check if model has custom schema
        return getattr(model, '__schema__', None) or model.__name__

    # ===== Private Helper Methods =====

    def _get_model_name(self, model: 'BaseRedisModel') -> str:
        """Extract model name from model class."""
        return getattr(model, '__schema__', None) or model.__name__

    def _join_parts(self, parts: List[str]) -> str:
        """Join key parts with delimiter and optional namespace."""
        key = self.delimiter.join(parts)
        if self.namespace:
            return f"{self.namespace}{self.delimiter}{key}"
        return key
