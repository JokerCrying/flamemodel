from ..d_type import PydanticFieldKwargs
from pydantic import Field, AliasPath, AliasChoices, types, fields as pydantic_fields
from typing import TypedDict, Optional, Callable, Any, Literal, Unpack, Union
from ..exceptions import (
    JsonSchemaExtraFieldsReservedFieldOccupiedError,
    JsonSchemaExtraReservedFieldOccupiedError,
    JsonSchemaExtraTypeError
)

_FlameModelJsonSchemaKey = '_flame_model'


def fields(
        *,
        shard_tag: bool = True,
        **kwargs: Unpack[PydanticFieldKwargs],
) -> pydantic_fields.FieldInfo:
    existing_json_schema_extra = kwargs.pop('json_schema_extra', None)
    fields_kwargs = dict(
        shard_tag=shard_tag
    )
    param_normalized = param_normalize_json_schema_extra(
        existing_json_schema_extra=existing_json_schema_extra,
        fields_kwargs=fields_kwargs
    )
    # Create and return a pydantic.FieldInfo instance
    return Field(json_schema_extra=param_normalized, **kwargs)


def _wrap_json_schema_extra_func(original_func, fields_kwargs: dict):
    def _wrapper(schema: dict) -> None:
        original_func(schema)
        if _FlameModelJsonSchemaKey in schema:
            raise JsonSchemaExtraReservedFieldOccupiedError(
                f'the reserved field `{_FlameModelJsonSchemaKey}` has be occupied.'
            )
        schema[_FlameModelJsonSchemaKey] = fields_kwargs

    return _wrapper


def _wrap_json_schema_extra_is_none(fields_kwargs: dict):
    def _wrapper(schema: dict) -> None:
        schema[_FlameModelJsonSchemaKey] = fields_kwargs

    return _wrapper


def _wrap_json_schema_extra_is_dict(existing_json_schema_extra):
    def _wrapper(schema: dict) -> None:
        schema.update(existing_json_schema_extra)

    return _wrapper


def param_normalize_json_schema_extra(existing_json_schema_extra, fields_kwargs: dict):
    fields_kwargs_copy = fields_kwargs.copy()  # light copy, in case the data is tampered with
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
