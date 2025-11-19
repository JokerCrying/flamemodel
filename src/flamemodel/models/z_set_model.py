from typing import Any, List as TypingList, Optional
from .redis_model import BaseRedisModel
from ..d_type import SelfInstance


class ZSet(BaseRedisModel):
    __redis_type__ = 'zset'
    
    @classmethod
    def _score_field(cls) -> str:
        score_fields = cls.__model_meta__.score_field
        if not score_fields:
            raise ValueError(f"Model {cls.__name__} has no score_field defined")
        return list(score_fields.keys())[0]
    
    @property
    def score_value(self) -> float:
        field_name = self._score_field()
        return float(getattr(self, field_name, 0.0))

    @classmethod
    def add(cls, pk: Any, *members: SelfInstance) -> int:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        mapping = {}
        for member in members:
            value = cls.__serializer__.serialize(member)
            score = member.score_value if hasattr(member, 'score_value') else 0.0
            mapping[value] = score
        return driver.zadd(pk_key, mapping)
    
    @classmethod
    def remove(cls, pk: Any, *members: SelfInstance) -> int:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        values = [cls.__serializer__.serialize(m) for m in members]
        return driver.zrem(pk_key, *values)
    
    @classmethod
    def get_score(cls, pk: Any, member: SelfInstance) -> Optional[float]:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        value = cls.__serializer__.serialize(member)
        return driver.zscore(pk_key, value)
    
    @classmethod
    def get_rank(cls, pk: Any, member: SelfInstance, reverse: bool = False) -> Optional[int]:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        value = cls.__serializer__.serialize(member)
        if reverse:
            return driver.zrevrank(pk_key, value)
        else:
            return driver.zrank(pk_key, value)
    
    @classmethod
    def range(cls, pk: Any, start: int, end: int, 
              withscores: bool = False, reverse: bool = False) -> TypingList[SelfInstance]:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        
        if reverse:
            results = driver.zrevrange(pk_key, start, end, withscores=withscores)
        else:
            results = driver.zrange(pk_key, start, end, withscores=withscores)
        
        if withscores:
            if results and isinstance(results, list):
                if len(results) > 0 and isinstance(results[0], tuple):
                    # 格式: [(member, score), ...]
                    return [
                        (cls.__serializer__.deserialize(r[0], cls), r[1])
                        for r in results
                    ]
                else:
                    # 格式: [member, score, member, score, ...]
                    return [
                        (cls.__serializer__.deserialize(results[i], cls), results[i + 1])
                        for i in range(0, len(results), 2)
                    ]
            return []
        else:
            return [cls.__serializer__.deserialize(r, cls) for r in results]
    
    @classmethod
    def top(cls, pk: Any, n: int, withscores: bool = False) -> TypingList[SelfInstance]:
        return cls.range(pk, 0, n - 1, withscores=withscores, reverse=True)
    
    @classmethod
    def bottom(cls, pk: Any, n: int, withscores: bool = False) -> TypingList[SelfInstance]:
        return cls.range(pk, 0, n - 1, withscores=withscores, reverse=False)
    
    @classmethod
    def size(cls, pk: Any) -> int:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        return driver.zcard(pk_key)
    
    @classmethod
    def count(cls, pk: Any, min_score: float = float('-inf'), 
              max_score: float = float('inf')) -> int:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        return driver.zcount(pk_key, min_score, max_score)
    
    @classmethod
    def range_by_score(cls, pk: Any, min_score: float, max_score: float,
                       withscores: bool = False, offset: int = 0, 
                       count: Optional[int] = None) -> TypingList[SelfInstance]:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        
        results = driver.zrangebyscore(pk_key, min_score, max_score, 
                                        withscores=withscores, offset=offset, count=count)
        
        if withscores:
            if results and isinstance(results, list):
                if len(results) > 0 and isinstance(results[0], tuple):
                    return [
                        (cls.__serializer__.deserialize(r[0], cls), r[1])
                        for r in results
                    ]
                else:
                    return [
                        (cls.__serializer__.deserialize(results[i], cls), results[i + 1])
                        for i in range(0, len(results), 2)
                    ]
            return []
        else:
            return [cls.__serializer__.deserialize(r, cls) for r in results]

    def save(self) -> int:
        pk_key = self.get_primary_key()
        driver = self.get_driver()
        value = self.__serializer__.serialize(self)
        score = self.score_value
        return driver.zadd(pk_key, {value: score})
    
    def remove_self(self) -> int:
        pk_key = self.get_primary_key()
        driver = self.get_driver()
        value = self.__serializer__.serialize(self)
        return driver.zrem(pk_key, value)
    
    def incr_score(self, amount: float = 1.0) -> float:
        pk_key = self.get_primary_key()
        driver = self.get_driver()
        value = self.__serializer__.serialize(self)
        new_score = driver.zincrby(pk_key, amount, value)
        field_name = self._score_field()
        setattr(self, field_name, new_score)
        return new_score
    
    def get_my_rank(self, reverse: bool = False) -> Optional[int]:
        pk, _ = self.pk_info()
        return self.get_rank(pk, self, reverse=reverse)

    @property
    def score(self) -> Optional[float]:
        pk, _ = self.pk_info()
        return self.get_score(pk, self)
    
    def exists(self) -> bool:
        return self.score is not None
