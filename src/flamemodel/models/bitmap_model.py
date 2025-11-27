from typing import Any, Tuple, Dict, Literal
from .redis_model import BaseRedisModel
from ..d_type import SelfInstance
from ..utils.action import Action


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
        acts = []
        for field_name, offset in cls._bitmap_offset().items():
            acts.append(
                driver.getbit(primary_key, offset).then(
                    lambda x, fn=field_name: (fn, 1 if x else 0)
                )
            )
        return Action.sequence(
            acts,
            runtime_mode=cls.__redis_adaptor__.runtime_mode,
            result_from_index=None
        ).then(
            lambda pairs: cls.__serializer__.deserialize(
                dict(pairs) | {pk_field_name: pk}, cls
            )
        )

    def bitmap(self) -> Tuple[int]:
        driver = self.get_driver()
        pk = self.get_primary_key()
        acts = []
        for _, offset in self._bitmap_offset().items():
            acts.append(
                driver.getbit(pk, offset).then(
                    lambda x: 1 if x else 0
                )
            )
        return Action.sequence(
            acts,
            runtime_mode=self.__redis_adaptor__.runtime_mode,
            result_from_index=None,
        ).then(tuple)

    def save(self) -> SelfInstance:
        driver = self.get_driver()
        pk = self.get_primary_key()
        acts = []
        for field_name, offset in self._bitmap_offset().items():
            value = getattr(self, field_name)
            acts.append(
                driver.setbit(pk, offset, 1 if value else 0)
            )
        return Action.sequence(
            acts,
            runtime_mode=self.__redis_adaptor__.runtime_mode,
            result_from_index=None
        )

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
        runtime_mode = cls.__redis_adaptor__.runtime_mode
        if operate == 'NOT':
            bitop_act = driver.bitop('NOT', dest_pk, source_pk)
        else:
            bitop_act = driver.bitop(operate, dest_pk, source_pk, target_pk)
        pk_field_name = list(cls.__model_meta__.pk_info.keys())[0]
        parsed = cls.__key_builder__.parse_key(dest_pk)
        pk_value = parsed.get('pk')
        acts = []
        for field_name, offset in cls._bitmap_offset().items():
            acts.append(
                driver.getbit(dest_pk, offset).then(
                    lambda x, fn=field_name: (fn, 1 if x else 0)
                )
            )
        read_act = Action.sequence(
            acts,
            runtime_mode=runtime_mode,
            result_from_index=None
        ).then(
            lambda pairs: cls.__serializer__.deserialize(
                dict(pairs) | {pk_field_name: pk_value}, cls
            )
        )
        return Action.sequence(
            [bitop_act, read_act],
            runtime_mode=runtime_mode,
            result_from_index=1
        )
