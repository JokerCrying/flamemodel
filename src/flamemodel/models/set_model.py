from typing import Set as TypingSet, Any, List
from ..d_type import SelfInstance
from .redis_model import BaseRedisModel


class Set(BaseRedisModel):
    __redis_type__ = 'set'

    @classmethod
    def members(cls, pk: Any) -> TypingSet[SelfInstance]:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        results = driver.smembers(pk_key)
        return results.then(
            lambda x: [cls.__serializer__.deserialize(r, cls) for r in x]
        ).execute()

    @classmethod
    def contains(cls, pk: Any, member: SelfInstance) -> bool:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        value = cls.__serializer__.serialize(member)
        return driver.sismember(pk_key, value).execute()

    @classmethod
    def size(cls, pk: Any) -> int:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        return driver.scard(pk_key).execute()

    @classmethod
    def pop_random(cls, pk: Any) -> SelfInstance:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        result = driver.spop(pk_key)
        return result.then(
            lambda x: cls.__serializer__.deserialize(x, cls)
        ).execute()

    @classmethod
    def random(cls, pk: Any, count: int = 1) -> List[SelfInstance]:
        def _final_handler(rs):
            if isinstance(rs, list):
                return [cls.__serializer__.deserialize(r, cls) for r in rs]
            return [cls.__serializer__.deserialize(rs, cls)]

        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        results = driver.srandmember(pk_key, count)
        return results.then(_final_handler).execute()

    @classmethod
    def union(cls, *pks: Any) -> TypingSet[SelfInstance]:
        driver = cls.get_driver()
        keys = [cls.primary_key(pk) for pk in pks]
        results = driver.sunion(*keys)
        return results.then(
            lambda x: {cls.__serializer__.deserialize(r, cls) for r in x}
        ).execute()

    @classmethod
    def intersection(cls, *pks: Any) -> TypingSet[SelfInstance]:
        driver = cls.get_driver()
        keys = [cls.primary_key(pk) for pk in pks]
        results = driver.sinter(*keys)
        return results.then(
            lambda x: {cls.__serializer__.deserialize(r, cls) for r in x}
        ).execute()

    @classmethod
    def difference(cls, *pks: Any) -> TypingSet[SelfInstance]:
        driver = cls.get_driver()
        keys = [cls.primary_key(pk) for pk in pks]
        results = driver.sdiff(*keys)
        return results.then(
            lambda x: {cls.__serializer__.deserialize(r, cls) for r in x}
        ).execute()

    @classmethod
    def move(cls, member: SelfInstance, src_pk: Any, dest_pk: Any) -> bool:
        driver = cls.get_driver()
        src_key = cls.primary_key(src_pk)
        dest_key = cls.primary_key(dest_pk)
        value = cls.__serializer__.serialize(member)
        return driver.smove(src_key, dest_key, value).execute()

    def save(self) -> int:
        return self.add()

    def add(self) -> int:
        pk_key = self.get_primary_key()
        value = self.__serializer__.serialize(self)
        driver = self.get_driver()
        return driver.sadd(pk_key, value).execute()

    def remove(self) -> int:
        pk_key = self.get_primary_key()
        value = self.__serializer__.serialize(self)
        driver = self.get_driver()
        return driver.srem(pk_key, value).execute()

    def is_member(self) -> bool:
        pk_key = self.get_primary_key()
        value = self.__serializer__.serialize(self)
        driver = self.get_driver()
        return driver.sismember(pk_key, value).execute()
