from typing import TYPE_CHECKING
from ..d_type import SingletonMeta

if TYPE_CHECKING:
    from ..adaptor import RedisAdaptor


class BaseDriver(metaclass=SingletonMeta):
    def __init__(self, adaptor: 'RedisAdaptor'):
        self.adaptor = adaptor

    def commit(self, key: str, value: str):
        return self.adaptor.proxy.set(key, value)

    def delete(self, key: str):
        return self.adaptor.proxy.delete(key)

    def get(self, key: str):
        return self.adaptor.proxy.get(key)

    def expire(self, key: str, ttl: int):
        return self.adaptor.proxy.expire(key, ttl)

    def exists(self, key: str):
        return self.adaptor.proxy.exists(key)

    def ttl(self, key: str):
        return self.adaptor.proxy.ttl(key)

    def persist(self, key: str):
        return self.adaptor.proxy.persist(key)
