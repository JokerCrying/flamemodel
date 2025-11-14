from ..d_type import SingletonMeta
from ..constant import (
    StringModelDelimiter,
    PydanticPropertyField,
    FlameModelJsonSchemaKey
)
from ..exceptions import (
    ModelNotExistsError,
    FieldNotExistsError
)
from ..utils.logger import logger
from typing import Dict, Type, TYPE_CHECKING
from ..utils.parse_model_metadata import parse_model_metadata

if TYPE_CHECKING:
    from .redis_model import BaseRedisModel
    from .fields import FieldMetaData


class RedisModelRepository(metaclass=SingletonMeta):
    def __init__(self):
        self._repo: Dict[str, Type['BaseRedisModel']] = {}

    def register_model(self, model_name: str, model_cls: Type['BaseRedisModel']):
        if model_name in self._repo:
            logger.warning(
                "The model name has been defined multiple times, "
                f"model_name={model_name}"
            )
        self._parse_model_metadata(model_cls)
        self._repo[model_name] = model_cls

    def parse_model_string(self, model_type: str):
        field_info = None
        if StringModelDelimiter in model_type:
            model_name, field = model_type.split(StringModelDelimiter, 1)
        else:
            model_name, field = (model_type, None)
        model_cls = self._get_model_with_string(model_name)
        if model_cls is None:
            raise ModelNotExistsError(
                "The model is not exists, check is it defined? "
                f"model={model_name} "
                f"original input={model_type}",
                model_type=model_name
            )
        if field:
            field_info = self._get_field_info(model_cls, field)
        return {
            'model_cls': model_cls,
            'field_info': field_info
        }

    def _get_model_with_string(self, model: str):
        return self._repo.get(model)

    @classmethod
    def _get_field_info(cls, model_cls: Type['BaseRedisModel'], field: str) -> 'FieldMetaData':
        model_json_schema = model_cls.model_json_schema()
        fields = model_json_schema[PydanticPropertyField]
        if field not in fields:
            raise FieldNotExistsError(
                f"The fields is not in model of {model_cls.__name__}, "
                "check is it defined, "
                f"field_name={field}",
                field_name=field,
                fields=fields
            )
        field_json_schema = fields[field]
        return field_json_schema[FlameModelJsonSchemaKey]

    @classmethod
    def _parse_model_metadata(cls, model_cls: Type['BaseRedisModel']):
        model_cls.__model_meta__ = parse_model_metadata(model_cls)
