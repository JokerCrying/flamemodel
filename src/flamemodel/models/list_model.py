from .redis_model import BaseRedisModel
from ..d_type import SelfInstance
from typing import Literal, Any, List as TypingList


class List(BaseRedisModel):
    __redis_type__ = 'list'

    @classmethod
    def left_pop(cls, pk: Any) -> SelfInstance:
        return cls._pop(pk, 'left')

    @classmethod
    def right_pop(cls, pk: Any) -> SelfInstance:
        return cls._pop(pk, 'right')

    @classmethod
    def get(cls, pk: Any, index: int) -> SelfInstance:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        result = driver.lindex(pk_key, index)
        return result.then(
            lambda x: cls.__serializer__.deserialize(x, cls)
        )

    @classmethod
    def len(cls, pk: Any) -> int:
        driver = cls.get_driver()
        pk_key = cls.primary_key(pk)
        return driver.llen(pk_key)

    @classmethod
    def set(cls, pk: Any, index: int, value: SelfInstance):
        driver = cls.get_driver()
        pk_key = cls.primary_key(pk)
        value = cls.__serializer__.serialize(value)
        return driver.lset(pk_key, index, value)

    @classmethod
    def clear(cls, pk: Any):
        driver = cls.get_driver()
        pk_key = cls.primary_key(pk)
        return driver.ltrim(pk_key, 1, 0)

    @classmethod
    def all(cls, pk: Any):
        driver = cls.get_driver()
        pk_key = cls.primary_key(pk)
        return driver.lrange(pk_key, 0, -1).then(
            lambda x: [
                cls.__serializer__.deserialize(i, cls)
                for i in x
            ]
        )

    def remove_before(self):
        return self._remove_queue('before')

    def remove_after(self):
        return self._remove_queue('after')

    def remove_equals(self):
        return self._remove_queue('equals')

    def save(self) -> SelfInstance:
        return self.append()

    def append(self):
        return self._save('left')

    def prepend(self):
        return self._save('right')

    def length(self) -> int:
        pk, _ = self.pk_info()
        return self.len(pk)

    def range(self, start_index: int, end_index: int) -> TypingList[SelfInstance]:
        driver = self.get_driver()
        pk_key = self.get_primary_key()
        results = driver.lrange(pk_key, start_index, end_index)
        return results.then(
            lambda x: [
                self.__serializer__.deserialize(r, self.__class__)
                for r in x
            ]
        )

    def _save(self, pos: Literal['left', 'right']):
        pk = self.get_primary_key()
        value = self.__serializer__.serialize(self)
        driver = self.get_driver()
        if pos == 'left':
            return driver.lpush(pk, value)
        else:
            return driver.rpush(pk, value)

    def _remove_queue(self, pos: Literal['before', 'after', 'equals']):
        pk = self.get_primary_key()
        value = self.__serializer__.serialize(self)
        driver = self.get_driver()
        if pos == 'before':
            remove_tag = 1
        elif pos == 'after':
            remove_tag = -1
        else:
            remove_tag = 0
        return driver.lrem(pk, remove_tag, value)

    @classmethod
    def _pop(cls, pk: Any, pos: Literal['left', 'right']) -> SelfInstance:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        if pos == 'left':
            result = driver.lpop(pk_key)
        else:
            result = driver.rpop(pk_key)
        return result.then(
            lambda x: cls.__serializer__.deserialize(x, cls)
        )
