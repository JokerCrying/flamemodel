import copy
from dataclasses import dataclass
from typing import Optional, Callable, Any, List, Dict
from .foreign import ForeignKey


class MetadataMinix:
    def light_copy(self):
        return copy.copy(self)

    def deep_copy(self):
        return copy.deepcopy(self)


@dataclass
class FieldMetaData(MetadataMinix):
    primary_key: bool = False
    primary_key_factory: Callable[[], Any] = None
    shard_tag: bool = False
    foreign_key: Optional[ForeignKey] = None
    index: bool = False
    unique: bool = False
    serializer: Optional[Callable[[Any], str]] = None
    deserializer: Optional[Callable[[str], Any]] = None
    exclude_from_dump: bool = False
    ignore_in_key: bool = False
    hash_field: bool = False


@dataclass
class ModelMetadata(MetadataMinix):
    pk_info: Dict[str, FieldMetaData]
    indexes: List[Dict[str, FieldMetaData]]
    unique_indexes: List[Dict[str, FieldMetaData]]
    shard_tags: List[str]
