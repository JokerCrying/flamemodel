from typing import Any, Tuple, Dict, Literal
from .redis_model import BaseRedisModel
from ..d_type import SelfInstance


class BitMap(BaseRedisModel):
    __redis_type__ = 'bitmap'

    @classmethod
    def count_by(cls, pk: Any) -> int:
        driver = cls.get_driver()
        key = cls.primary_key(pk)
        return driver.bitcount(key)

    @classmethod
    def get(cls, pk: Any) -> SelfInstance:
        driver = cls.get_driver()
        pk_field_info = cls.__model_meta__.pk_info
        pk_field_name = list(pk_field_info.keys())[0]
        primary_key = cls.primary_key(pk)
        result = {
            pk_field_name: pk
        }
        for field_name, offset in cls._bitmap_offset().items():
            result[field_name] = 1 if driver.getbit(primary_key, offset) else 0
        return cls.__serializer__.deserialize(result, cls)

    def bitmap(self) -> Tuple[int]:
        driver = self.get_driver()
        pk = self.get_primary_key()
        bits = []
        for _, offset in self._bitmap_offset().items():
            bits.append(
                1 if driver.getbit(pk, offset) else 0
            )
        return tuple(bits)

    def save(self) -> SelfInstance:
        driver = self.get_driver()
        pk = self.get_primary_key()
        for field_name, offset in self._bitmap_offset().items():
            value = getattr(self, field_name)
            driver.setbit(pk, offset, 1 if value else 0)
        return self

    def count(self) -> int:
        driver = self.get_driver()
        key = self.get_primary_key()
        return driver.bitcount(key)

    def and_(self, other: 'BitMap', dest_pk: Any) -> SelfInstance:
        dest_pk_key = self.primary_key(dest_pk)
        return self._bit_top(
            dest_pk_key, self.get_primary_key(),
            other.get_primary_key(), 'AND'
        )

    def or_(self, other: 'BitMap', dest_pk: Any) -> SelfInstance:
        dest_pk_key = self.primary_key(dest_pk)
        return self._bit_top(
            dest_pk_key, self.get_primary_key(),
            other.get_primary_key(), 'OR'
        )

    def xor(self, other: 'BitMap', dest_pk: Any) -> SelfInstance:
        dest_pk_key = self.primary_key(dest_pk)
        return self._bit_top(
            dest_pk_key, self.get_primary_key(),
            other.get_primary_key(), 'XOR'
        )

    def not_(self, other: 'BitMap', dest_pk: Any) -> SelfInstance:
        dest_pk_key = self.primary_key(dest_pk)
        return self._bit_top(
            dest_pk_key, self.get_primary_key(),
            other.get_primary_key(), 'NOT'
        )

    @classmethod
    def _bitmap_offset(cls) -> Dict[str, int]:
        result = {}
        for flag in cls.__model_meta__.flags:
            filed_name, field_meta = list(flag.items())[0]
            result[filed_name] = field_meta.flag
        return result

    @classmethod
    def _bit_top(
            cls,
            dest_pk: str,
            source_pk,
            target_pk: str,
            operate: Literal['AND', 'OR', 'NOT', 'XOR']
    ) -> SelfInstance:
        driver = cls.get_driver()
        driver.bittop(operate, dest_pk, source_pk, target_pk)
        return cls.get(dest_pk)

    def __iter__(self):
        return iter(self.bitmap())

    async def __aiter__(self):
        async for item in self.bitmap():
            yield item
