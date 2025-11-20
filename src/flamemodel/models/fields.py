import uuid
import warnings
from ..d_type import PydanticFieldKwargs
from pydantic import Field, fields as pydantic_fields
from typing import Any, Unpack, Optional, Callable
from ..exceptions import (
    JsonSchemaExtraReservedFieldOccupiedError,
    JsonSchemaExtraTypeError
)
from ..constant import (
    FlameModelJsonSchemaKey
)
from .foreign import ForeignKey
from .metadata import FieldMetaData


def fields(
        *,
        primary_key: bool = False,
        primary_key_factory: Callable[[], Any] = None,
        shard_tag: bool = False,
        foreign_key: Optional[ForeignKey] = None,
        index: bool = False,
        unique: bool = False,
        serializer: Optional[Callable[[Any], str]] = None,
        deserializer: Optional[Callable[[str], Any]] = None,
        exclude_from_dump: bool = False,
        ignore_in_key: bool = False,
        hash_field: bool = False,
        score_field: bool = False,
        member_field: bool = False,
        lng_field: bool = False,
        lat_field: bool = False,
        flag: Optional[int] = None,
        entry: bool = None,
        **kwargs: Unpack[PydanticFieldKwargs],
) -> pydantic_fields.FieldInfo:
    if primary_key:
        if primary_key_factory is None:
            warnings.warn(
                f"The function `uuid.uuid4` will be automatically used as the primary key generator, "
                "use `fields(primary_key_factory=callable_func)` to set it, please.",
                UserWarning
            )
            primary_key_factory = uuid.uuid4
        kwargs['default_factory'] = primary_key_factory
    existing_json_schema_extra = kwargs.pop('json_schema_extra', None)
    fields_kwargs = FieldMetaData(
        primary_key=primary_key,
        shard_tag=shard_tag,
        foreign_key=foreign_key,
        index=index,
        unique=unique,
        serializer=serializer,
        deserializer=deserializer,
        exclude_from_dump=exclude_from_dump,
        ignore_in_key=ignore_in_key,
        primary_key_factory=primary_key_factory,
        hash_field=hash_field,
        score_field=score_field,
        member_field=member_field,
        lng_field=lng_field,
        lat_field=lat_field,
        flag=flag,
        entry=entry
    )
    param_normalized = param_normalize_json_schema_extra(
        existing_json_schema_extra=existing_json_schema_extra,
        fields_kwargs=fields_kwargs
    )
    return Field(json_schema_extra=param_normalized, **kwargs)


def _wrap_json_schema_extra_func(original_func, fields_kwargs: FieldMetaData):
    def _wrapper(schema: dict) -> None:
        original_func(schema)
        if FlameModelJsonSchemaKey in schema:
            raise JsonSchemaExtraReservedFieldOccupiedError(
                f'the reserved field `{FlameModelJsonSchemaKey}` has be occupied.'
            )
        schema[FlameModelJsonSchemaKey] = fields_kwargs

    return _wrapper


def _wrap_json_schema_extra_is_none(fields_kwargs: FieldMetaData):
    def _wrapper(schema: dict) -> None:
        schema[FlameModelJsonSchemaKey] = fields_kwargs

    return _wrapper


def _wrap_json_schema_extra_is_dict(existing_json_schema_extra):
    def _wrapper(schema: dict) -> None:
        schema.update(existing_json_schema_extra)

    return _wrapper


def param_normalize_json_schema_extra(existing_json_schema_extra, fields_kwargs: FieldMetaData):
    fields_kwargs_copy = fields_kwargs.light_copy()  # light copy, in case the data is tampered with
    if existing_json_schema_extra is None:
        result = _wrap_json_schema_extra_is_none(fields_kwargs_copy)
    elif isinstance(existing_json_schema_extra, dict):
        existing_json_schema_extra_call = _wrap_json_schema_extra_is_dict(existing_json_schema_extra)
        result = _wrap_json_schema_extra_func(
            original_func=existing_json_schema_extra_call,
            fields_kwargs=fields_kwargs_copy
        )
    elif callable(existing_json_schema_extra):
        result = _wrap_json_schema_extra_func(
            original_func=existing_json_schema_extra,
            fields_kwargs=fields_kwargs_copy
        )
    else:
        error_type = type(existing_json_schema_extra)
        raise JsonSchemaExtraTypeError(
            f'Pydantic field json_schema_extra only be '
            'dict type or None type or callable function, '
            f'got {error_type} now.',
            error_type=error_type
        )
    return result
