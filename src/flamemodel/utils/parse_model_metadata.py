from typing import TYPE_CHECKING, Dict, Type
from ..constant import PydanticPropertyField, FlameModelJsonSchemaKey
from ..exceptions import (
    TooManyPrimaryKeyError, HasNoPrimaryKeyError
)
from ..models.metadata import FieldMetaData, ModelMetadata

if TYPE_CHECKING:
    from ..models import BaseRedisModel

FieldsMetadataType = Dict[str, FieldMetaData]


def parse_model_metadata(model_instance: Type['BaseRedisModel']) -> ModelMetadata:
    model_json_schema = model_instance.model_json_schema()
    model_fields = model_json_schema[PydanticPropertyField]
    model_fields_metadata: FieldsMetadataType = {
        f: p[FlameModelJsonSchemaKey]
        for f, p in model_fields.items()
    }
    pk = None
    indexes = []
    shard_tags = []
    unique_indexes = []
    model_name = model_instance.__class__.__name__
    for field, metadata in model_fields_metadata.items():
        item = {field: metadata}
        if metadata.primary_key:
            if pk is not None:
                raise TooManyPrimaryKeyError(
                    f'has too many primary key in {model_name}'
                )
            pk = item
        if metadata.index:
            indexes.append(item)
        if metadata.shard_tag:
            shard_tags.append(field)
        if metadata.unique:
            unique_indexes.append(item)
    if pk is None:
        raise HasNoPrimaryKeyError(
            f"the model {model_name} should have one primary key."
        )
    return ModelMetadata(
        pk_info=pk,
        indexes=indexes,
        shard_tags=shard_tags,
        unique_indexes=unique_indexes
    )
