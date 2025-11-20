import uuid
from typing import Any, List, Optional, Iterable
from .redis_model import BaseRedisModel
from ..d_type import SelfInstance


class HyperLogLog(BaseRedisModel):
    __redis_type__ = 'hyper_log_log'

    def add(self, *elements: Any) -> int:
        if not elements:
            return 0
        key = self.get_primary_key()
        driver = self.get_driver()
        # Convert elements to strings for Redis storage
        str_elements = [str(elem) for elem in elements]
        return driver.pfadd(key, *str_elements)

    def count(self) -> int:
        key = self.get_primary_key()
        driver = self.get_driver()
        return driver.pfcount(key)

    def merge_from(self, *other_instances: SelfInstance) -> int:
        if not other_instances:
            return 0
        dest_key = self.get_primary_key()
        source_keys = [inst.get_primary_key() for inst in other_instances]
        driver = self.get_driver()
        return driver.pfmerge(dest_key, *source_keys)

    def save(self) -> SelfInstance:
        raise NotImplementedError(
            "HyperLogLog does not support save() operation. "
            "Use add(*elements) to insert data."
        )

    def __len__(self) -> int:
        return self.count()

    def __iadd__(self, elements: Iterable[Any]) -> SelfInstance:
        if isinstance(elements, (list, tuple, set)):
            self.add(*elements)
        else:
            # Handle single element
            self.add(elements)
        return self

    @classmethod
    def add_to(cls, pk: Any, *elements: Any) -> int:
        if not elements:
            return 0
        key = cls.primary_key(pk)
        driver = cls.get_driver()
        str_elements = [str(elem) for elem in elements]
        return driver.pfadd(key, *str_elements)

    @classmethod
    def count_by(cls, pk: Any) -> int:
        key = cls.primary_key(pk)
        driver = cls.get_driver()
        return driver.pfcount(key)

    @classmethod
    def count_by_key(cls, key: str) -> int:
        driver = cls.get_driver()
        return driver.pfcount(key)

    @classmethod
    def merge_by_pks(
            cls,
            pks: List[Any],
            auto_cleanup: bool = True
    ) -> int:
        if not pks:
            return 0
        # Generate temporary key
        temp_key = f"temp:merge:{cls.__name__.lower()}:{uuid.uuid4().hex}"
        # Get source keys
        source_keys = [cls.primary_key(pk) for pk in pks]
        # Merge
        driver = cls.get_driver()
        driver.pfmerge(temp_key, *source_keys)
        # Count
        result = driver.pfcount(temp_key)
        # Cleanup if requested
        if auto_cleanup:
            driver.delete(temp_key)
        return result

    @classmethod
    def merge_to_key(
            cls,
            dest_key: str,
            pks: List[Any],
            expire_seconds: Optional[int] = None
    ) -> str:
        if not pks:
            return dest_key
        source_keys = [cls.primary_key(pk) for pk in pks]
        driver = cls.get_driver()
        # Merge
        driver.pfmerge(dest_key, *source_keys)
        # Set expiration if requested
        if expire_seconds:
            driver.expire(dest_key, expire_seconds)
        return dest_key

    @classmethod
    def merge_instances(
            cls,
            dest_pk: Any,
            *source_instances: SelfInstance
    ) -> int:
        if not source_instances:
            return 0
        dest_key = cls.primary_key(dest_pk)
        source_keys = [inst.get_primary_key() for inst in source_instances]
        driver = cls.get_driver()
        return driver.pfmerge(dest_key, *source_keys)

    @classmethod
    def union_count(cls, *pks: Any) -> int:
        return cls.merge_by_pks(list(pks), auto_cleanup=True)
