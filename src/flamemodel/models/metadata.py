import copy
from .foreign import ForeignKey
from dataclasses import dataclass
from typing import Optional, Callable, Any, List, Dict, Tuple


class MetadataMinix:
    def light_copy(self):
        return copy.copy(self)

    def deep_copy(self):
        return copy.deepcopy(self)

    def __setitem__(self, key, value):
        raise ValueError(f"Don't try to modify value of ModelMetadata or FieldMetadata.")


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
    score_field: bool = False
    member_field: bool = False
    lng_field: bool = False
    lat_field: bool = False
    flag: Optional[int] = None
    entry: bool = False


@dataclass
class ModelMetadata(MetadataMinix):
    fields: Tuple[Dict[str, FieldMetaData]]
    pk_info: Dict[str, FieldMetaData]
    indexes: Tuple[Dict[str, FieldMetaData]]
    unique_indexes: Tuple[Dict[str, FieldMetaData]]
    shard_tags: Tuple[str]
    hash_field: Dict[str, FieldMetaData]
    score_field: Dict[str, FieldMetaData]
    member_field: Dict[str, FieldMetaData]
    lng_field: Dict[str, FieldMetaData]
    lat_field: Dict[str, FieldMetaData]
    flags: Tuple[Dict[str, FieldMetaData]]
    entry_field: Dict[str, FieldMetaData]
