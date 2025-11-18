from typing import (
    Protocol, runtime_checkable,
    TYPE_CHECKING, List,
    Any, Dict, Optional, Literal
)

if TYPE_CHECKING:
    from ...models import BaseRedisModel
    from ...models.metadata import FieldMetaData


@runtime_checkable
class KeyBuilderProtocol(Protocol):
    """Protocol for building Redis keys for models, indexes, and relationships.
    
    All methods should return properly formatted Redis key strings.
    Users can implement this protocol to customize key generation strategies.
    """

    # ===== Primary Key Methods =====
    
    def primary_key(
            self,
            *,
            model: 'BaseRedisModel',
            shard_tags: List[str],
            pk: Any,
            pk_field_name: str,
            pk_field_info: Dict[str, 'FieldMetaData']
    ) -> str:
        """Build the primary key for a model instance.
        
        Args:
            model: The model class
            shard_tags: List of shard tag values for distributed keys
            pk: Primary key value
            pk_field_name: Name of the primary key field
            pk_field_info: Metadata of the primary key field
            
        Returns:
            Redis key string (e.g., 'User:123' or 'User:shard1:123')
        """
        ...

    # ===== Index Key Methods =====

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
        """Build an index key for querying by indexed fields.
        
        Args:
            model: The model class
            shard_tags: List of shard tag values
            index_fields: List of indexed field names
            index_values: Corresponding values for the indexed fields
            pk: Primary key value to store in the index
            index_fields_info: Metadata for each indexed field
            
        Returns:
            Redis index key string (e.g., 'User:idx:email:john@example.com')
        """
        ...

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
        """Build a unique constraint key.
        
        Args:
            model: The model class
            shard_tags: List of shard tag values
            unique_fields: List of unique field names
            unique_values: Corresponding values for the unique fields
            pk: Primary key value to store
            unique_fields_info: Metadata for each unique field
            
        Returns:
            Redis unique key string (e.g., 'User:uniq:username:johndoe')
        """
        ...

    # ===== Foreign Key & Relationship Methods =====

    def foreign_key(
            self,
            *,
            model: 'BaseRedisModel',
            foreign_model: 'BaseRedisModel',
            field_name: str,
            pk: Any,
            foreign_pk: Any
    ) -> str:
        """Build a foreign key reference.
        
        Args:
            model: The model class containing the foreign key
            foreign_model: The referenced model class
            field_name: Name of the foreign key field
            pk: Primary key of the current model instance
            foreign_pk: Primary key of the referenced model instance
            
        Returns:
            Redis foreign key string (e.g., 'Order:123:fk:user' -> 'User:456')
        """
        ...

    def relationship_key(
            self,
            *,
            model: 'BaseRedisModel',
            related_model: 'BaseRedisModel',
            relation_name: str,
            pk: Any,
            relation_type: Literal['one', 'many']
    ) -> str:
        """Build a relationship key for one-to-many or many-to-many relationships.
        
        Args:
            model: The model class
            related_model: The related model class
            relation_name: Name of the relationship
            pk: Primary key of the current model instance
            relation_type: Type of relationship ('one' or 'many')
            
        Returns:
            Redis relationship key (e.g., 'User:123:rel:orders' for one-to-many)
        """
        ...

    def backref_key(
            self,
            *,
            model: 'BaseRedisModel',
            source_model: 'BaseRedisModel',
            backref_name: str,
            pk: Any,
            source_pk: Any
    ) -> str:
        """Build a reverse reference key.
        
        Args:
            model: The model class
            source_model: The source model that references this model
            backref_name: Name of the back reference
            pk: Primary key of the current model instance
            source_pk: Primary key of the source model instance
            
        Returns:
            Redis backref key (e.g., 'User:123:backref:orders')
        """
        ...

    # ===== Hash Field Methods =====

    def hash_field_key(
            self,
            *,
            model: 'BaseRedisModel',
            pk: Any,
            field_name: str
    ) -> str:
        """Build the main hash key for storing model fields.
        
        Args:
            model: The model class
            pk: Primary key value
            field_name: Name of the hash field
            
        Returns:
            Redis hash key (e.g., 'User:123' for hash-based models)
        """
        ...

    # ===== Collection & Pattern Methods =====

    def model_collection_key(
            self,
            *,
            model: 'BaseRedisModel',
            shard_tags: Optional[List[str]] = None
    ) -> str:
        """Build a collection key for all instances of a model.
        
        Useful for maintaining a set of all primary keys.
        
        Args:
            model: The model class
            shard_tags: Optional shard tag values
            
        Returns:
            Redis collection key (e.g., 'User:all' or 'User:shard1:all')
        """
        ...

    def key_pattern(
            self,
            *,
            model: 'BaseRedisModel',
            pattern_type: Literal['primary', 'index', 'unique', 'foreign', 'relationship'],
            prefix: Optional[str] = None
    ) -> str:
        """Build a key pattern for scanning/matching keys.
        
        Args:
            model: The model class
            pattern_type: Type of key pattern to generate
            prefix: Optional prefix for the pattern
            
        Returns:
            Redis key pattern (e.g., 'User:*' or 'User:idx:*')
        """
        ...

    # ===== Utility Methods =====

    def format_shard_tags(
            self,
            shard_tags: List[str]
    ) -> str:
        """Format shard tags into a key segment.
        
        Args:
            shard_tags: List of shard tag values
            
        Returns:
            Formatted shard tag string (e.g., 'shard1' or 'us-west:prod')
        """
        ...

    def parse_key(
            self,
            key: str
    ) -> Dict[str, Any]:
        """Parse a Redis key to extract its components.
        
        Args:
            key: Redis key string
            
        Returns:
            Dictionary containing parsed components like model_name, pk, type, etc.
            Example: {'model': 'User', 'pk': '123', 'type': 'primary'}
        """
        ...

    def get_namespace(
            self,
            model: 'BaseRedisModel'
    ) -> str:
        """Get the namespace/prefix for a model.
        
        Args:
            model: The model class
            
        Returns:
            Namespace string (e.g., 'app:User' or just 'User')
        """
        ...
