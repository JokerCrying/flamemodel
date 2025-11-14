from typing import (
    Protocol, runtime_checkable,
    TYPE_CHECKING, List,
    Any, Dict
)

if TYPE_CHECKING:
    from ...models import BaseRedisModel
    from ...models.metadata import FieldMetaData


@runtime_checkable
class KeyBuilderProtocol(Protocol):
    def primary_key(
            self,
            *,
            model: 'BaseRedisModel',
            shard_tags: List[str],
            pk: Any,
            pk_field_name: str,
            pk_field_info: Dict[str, 'FieldMetaData']
    ):
        pass

    def index_key(
            self,
            *,
            model: 'BaseRedisModel',
            shard_tags: List[str],
            index_fields: List[str],
            index_values: List[Any],
            pk: Any,
            index_fields_info: List[Dict[str, 'FieldMetaData']]
    ):
        pass

    def unique_key(
            self,
            *,
            model: 'BaseRedisModel',
            shard_tags: List[str],
            unique_fields: List[str],
            unique_values: List[Any],
            pk: Any,
            unique_fields_info: List[Dict[str, 'FieldMetaData']]
    ):
        pass
