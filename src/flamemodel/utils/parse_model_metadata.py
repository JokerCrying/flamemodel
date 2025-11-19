from typing import TYPE_CHECKING, Dict, Type
from ..constant import PydanticPropertyField, FlameModelJsonSchemaKey
from ..exceptions import (
    TooManyPrimaryKeyError, HasNoPrimaryKeyError,
    TooManyHashFieldError, HasNoHashFieldError,
    TooManyScoreFieldFieldError, HasNoScoreFieldError,
    TooManyLatFieldFieldError, HasNoLatFieldError,
    TooManyLngFieldFieldError, HasNoLngFieldError,
    TooManyMemberFieldFieldError, HasNoMemberFieldError
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
    hash_field = None
    score_field = None
    member_field = None
    lng_field = None
    lat_field = None
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
        if model_instance.__redis_type__ == 'hash':
            if metadata.hash_field:
                if hash_field:
                    raise TooManyHashFieldError(
                        f"The model {model_name} has many hash field, "
                        "only one field can be hash field(hash)."
                    )
                hash_field = item
        if model_instance.__redis_type__ == 'zset':
            if metadata.score_field:
                if score_field:
                    raise TooManyScoreFieldFieldError(
                        f"The model {model_name} has many score field, "
                        f"only one field can be score field(zset)."
                    )
                score_field = item
        if model_instance.__redis_type__ == 'geo':
            if metadata.member_field:
                if member_field:
                    raise TooManyMemberFieldFieldError(
                        f"The model {model_name} has many member field, "
                        "only one field can be member field(geo)."
                    )
                member_field = item
            if metadata.lng_field:
                if lng_field:
                    raise TooManyLngFieldFieldError(
                        f"The model {model_name} has many lng field, "
                        "only one field can be lng field(geo)."
                    )
                lng_field = item
            if metadata.lat_field:
                if lat_field:
                    raise TooManyLatFieldFieldError(
                        f"The model {model_name} has many lat field, "
                        "only one field can be lat field(geo)."
                    )
                lat_field = item
    if pk is None:
        raise HasNoPrimaryKeyError(
            f"the model {model_name} should have one primary key."
        )
    if model_instance.__redis_type__ == 'hash':
        if hash_field is None:
            raise HasNoHashFieldError(
                f"The model {model_name} is Hash model type, "
                "but its has no hash field, "
                "use `fields(hash_field=True)` to mark it, please."
            )
    if model_instance.__redis_type__ == 'zset':
        if score_field is None:
            raise HasNoScoreFieldError(
                f"The model {model_name} is ZSet model type, "
                "but its has no score field, "
                "use `fields(score_fields=True)` to mark it, please."
            )
    if model_instance.__redis_type__ == 'geo':
        if member_field is None:
            raise HasNoMemberFieldError(
                f"The model {model_name} is Geo model type, "
                "but its has no member field, "
                "use `fields(member_field=True)` to mark it, please."
            )
        if lng_field is None:
            raise HasNoLngFieldError(
                f"The model {model_name} is Geo model type, "
                "but its has no lng field, "
                "use `fields(lng_field=True)` to mark it, please."
            )
        if lat_field is None:
            raise HasNoLatFieldError(
                f"The model {model_name} is Geo model type, "
                "but its has no lat field, "
                "use `fields(lat_field=True)` to mark it, please."
            )
    return ModelMetadata(
        pk_info=pk,
        indexes=indexes,
        shard_tags=shard_tags,
        unique_indexes=unique_indexes,
        hash_field=hash_field,
        score_field=score_field,
        member_field=member_field,
        lng_field=lng_field,
        lat_field=lat_field
    )
