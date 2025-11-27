from typing import Any, List as TypingList, Optional, Dict, Tuple
from .redis_model import BaseRedisModel
from ..d_type import SelfInstance


class Stream(BaseRedisModel):
    __redis_type__ = 'stream'

    @classmethod
    def _entry_id_field(cls) -> str:
        entry_id_fields = cls.__model_meta__.entry_field
        if not entry_id_fields:
            raise ValueError(f"Model {cls.__name__} has no entry_id_field defined")
        return list(entry_id_fields.keys())[0]

    @property
    def entry_id_value(self) -> str:
        field_name = self._entry_id_field()
        return getattr(self, field_name, "*")

    @classmethod
    def add_entry(cls, pk: Any, entry: SelfInstance, entry_value: str = "*") -> str:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        fields = cls._serialize_to_dict(entry)
        return driver.xadd(pk_key, fields, id=entry_value)

    @classmethod
    def read(cls, streams: Dict[Any, str], count: Optional[int] = None,
             block: Optional[int] = None) -> Dict[str, TypingList[Tuple[str, SelfInstance]]]:
        def _final_handler(x):
            parsed_results = {}
            if x:
                for stream_key, messages in x:
                    parsed_messages = [
                        (entry_id, cls._deserialize_from_dict(entry_id, fields))
                        for entry_id, fields in messages
                    ]
                    parsed_results[stream_key] = parsed_messages
            return parsed_results

        driver = cls.get_driver()
        stream_keys = {cls.primary_key(pk): start_id for pk, start_id in streams.items()}
        results = driver.xread(streams=stream_keys, count=count, block=block)
        return results.then(_final_handler)

    @classmethod
    def range(cls, pk: Any, start: str = "-", end: str = "+",
              count: Optional[int] = None) -> TypingList[Tuple[str, SelfInstance]]:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        results = driver.xrange(pk_key, start=start, end=end, count=count)
        return results.then(
            lambda x: [
                (entry_id, cls._deserialize_from_dict(entry_id, fields))
                for entry_id, fields in x
            ]
        )

    @classmethod
    def reverse_range(cls, pk: Any, end: str = "+", start: str = "-",
                      count: Optional[int] = None) -> TypingList[Tuple[str, SelfInstance]]:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        results = driver.xrevrange(pk_key, max=end, min=start, count=count)
        return results.then(
            lambda x: [
                (entry_id, cls._deserialize_from_dict(entry_id, fields))
                for entry_id, fields in x
            ]
        )

    @classmethod
    def delete_entries(cls, pk: Any, *entry_ids: str) -> int:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        return driver.xdel(pk_key, *entry_ids)

    @classmethod
    def length(cls, pk: Any) -> int:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        return driver.xlen(pk_key)

    @classmethod
    def trim(cls, pk: Any, max_length: int, approximate: bool = True) -> int:
        pk_key = cls.primary_key(pk)
        driver = cls.get_driver()
        return driver.xtrim(pk_key, maxlen=max_length, approximate=approximate)

    def save(self) -> str:
        return self.add()

    def add(self, entry_value: str = "*") -> str:
        def _final_handler(r):
            setattr(self, field_name, r)
            return r

        pk_key = self.get_primary_key()
        driver = self.get_driver()
        fields = self._serialize_to_dict(self)
        field_name = self._entry_id_field()
        return driver.xadd(pk_key, fields, id=entry_value).then(_final_handler)

    def remove(self) -> int:
        pk_key = self.get_primary_key()
        entry_id = self.entry_id_value
        if entry_id == "*":
            raise ValueError("Cannot delete entry with ID '*'. Entry must have a valid ID.")
        driver = self.get_driver()
        return driver.xdel(pk_key, entry_id)

    @classmethod
    def _serialize_to_dict(cls, instance: SelfInstance) -> Dict[str, Any]:
        fields = {}
        pk_field_name = list(cls.__model_meta__.pk_info.keys())[0]
        entry_id_field_name = cls._entry_id_field()
        for field_name in instance.model_fields.keys():
            if field_name in (pk_field_name, entry_id_field_name):
                continue
            value = getattr(instance, field_name)
            fields[field_name] = value
        return fields

    @classmethod
    def _deserialize_from_dict(cls, entry_id: str, fields: Dict[str, Any]) -> SelfInstance:
        data = {}
        entry_id_field_name = cls._entry_id_field()
        data[entry_id_field_name] = entry_id
        for field_name, value in fields.items():
            if isinstance(value, bytes):
                value = value.decode('utf-8')
            data[field_name] = cls.__serializer__.deserialize(value, cls)
        return cls(**data)  # type: ignore
