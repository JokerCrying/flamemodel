from typing import Any, List, Dict
from .redis_model import BaseRedisModel
from ..d_type import SelfInstance


class Hash(BaseRedisModel):
    __redis_type__ = 'hash'

    @classmethod
    def get(cls, pk: Any, field: Any) -> SelfInstance:
        hash_field, _ = cls._hash_field()
        driver = cls.get_driver()
        pk_key = cls.primary_key(pk)
        act = driver.hget(pk_key, field)
        return act.then(
            lambda r: cls.__serializer__.deserialize(r, cls)
        ).execute()

    @classmethod
    def get_all(cls, pk: Any) -> List[SelfInstance]:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        result = driver.hgetall(pk_key)
        return [
            cls.__serializer__.deserialize(r, cls)
            for r in result
        ]

    @classmethod
    def keys(cls, pk: Any) -> List[str]:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        return driver.hkeys(pk_key)

    @classmethod
    def values(cls, pk: Any) -> List[SelfInstance]:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        result = driver.hvals(pk_key)
        return [
            cls.__serializer__.deserialize(r, cls)
            for r in result
        ]

    def exists(self, field: Any) -> bool:
        driver = self.get_driver()
        return driver.hexists(self.get_primary_key(), field)

    def hash_delete(self):
        _, value = self.hash_field
        driver = self.get_driver()
        pk = self.get_primary_key()
        return driver.hdel(pk, value)

    def save(self) -> SelfInstance:
        _, field = self.hash_field
        pk = self.get_primary_key()
        driver = self.get_driver()
        return driver.hset(pk, field, self.__serializer__.serialize(self)).execute()

    @classmethod
    def _hash_field(cls, value: Any = None):
        hash_fields = cls.__model_meta__.hash_field
        field_name = list(hash_fields.keys())[0]
        return field_name, value

    @property
    def hash_field(self):
        field_name, _ = self._hash_field()
        return field_name, getattr(self, field_name)
