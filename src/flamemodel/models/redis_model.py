from pydantic import BaseModel
from typing import ClassVar, Any, Optional
from ..adaptor.interface import RedisAdaptor
from ..exceptions import (
    RepeatedSetAdaptorError,
    RepeatedSetModelMetadataError
)
from ..d_type import SelfInstance, RedisDataType
from .metadata import ModelMetadata


class BaseRedisModel(BaseModel):
    __redis_type__: ClassVar[RedisDataType]
    __key_pattern__: ClassVar[str]
    __redis_adaptor__: ClassVar[Optional[RedisAdaptor]] = None
    __schema__: ClassVar[Optional[str]] = None
    __model_meta__: ClassVar[Optional[ModelMetadata]] = None

    @classmethod
    def set_redis_adaptor(cls, adaptor: RedisAdaptor):
        """Sets the RedisAdaptor instance for all BaseRedisModel subclasses."""
        cls.__redis_adaptor__ = adaptor

    @classmethod
    def get_driver(cls):
        if cls.__redis_adaptor__ is None:
            raise RuntimeError("RedisAdaptor has not been set. Call BaseRedisModel.set_redis_adaptor() first.")
        return cls.__redis_adaptor__.get_redis_driver(cls.__redis_type__)

    @classmethod
    def get(cls, pk: Any) -> SelfInstance:
        driver = cls.get_driver()
        return driver.get()

    def delete(self) -> None:
        raise NotImplementedError

    def expire(self, ttl: int) -> None:
        raise NotImplementedError

    def save(self) -> SelfInstance:
        raise NotImplementedError

    def __setitem__(self, key, value):
        if key == '__redis_adaptor__':
            if self.__redis_adaptor__ is not None and isinstance(self.__redis_adaptor__, RedisAdaptor):
                raise RepeatedSetAdaptorError("Don't repeat set __redis_adaptor__.")
        if key == '__model_meta__':
            if self.__model_meta__ is not None and isinstance(self.__model_meta__, ModelMetadata):
                raise RepeatedSetModelMetadataError("Don't repeat set __model_meta__.")
        super().__setitem__(key, value)

    def get_pk_value(self):
        pk_field = self.__model_meta__.pk_info
        pk_field_name = list(pk_field.keys()).pop()
        return getattr(self, pk_field_name)
