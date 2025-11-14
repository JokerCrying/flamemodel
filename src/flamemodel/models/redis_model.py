from typing import ClassVar, Any, Optional
from ..d_type import SelfInstance, RedisDataType
from pydantic import BaseModel
from ..adaptor.interface import RedisAdaptor
from ..exceptions import RepeatedSetAdaptorError


class BaseRedisModel(BaseModel):
    __redis_type__: ClassVar[RedisDataType]
    __key_pattern__: ClassVar[str]
    __redis_adaptor__: ClassVar[Optional[RedisAdaptor]] = None

    @classmethod
    def set_redis_adaptor(cls, adaptor: RedisAdaptor):
        """Sets the RedisAdaptor instance for all BaseRedisModel subclasses."""
        cls.__redis_adaptor__ = adaptor

    @classmethod
    def get_driver(cls):
        if cls._redis_adaptor_instance is None:
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
                raise RepeatedSetAdaptorError('Dont repeat set __redis_adaptor__.')
        super().__setitem__(key, value)
