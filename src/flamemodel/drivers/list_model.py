from .base_driver import BaseDriver


class ListDriver(BaseDriver):
    def lpush(self, key: str, *values):
        return self.adaptor.proxy.lpush(key, *values)

    def rpush(self, key: str, *values):
        return self.adaptor.proxy.rpush(key, *values)

    def lpop(self, key: str):
        return self.adaptor.proxy.lpop(key)

    def rpop(self, key: str):
        return self.adaptor.proxy.rpop(key)

    def lrange(self, key: str, start: int, end: int):
        return self.adaptor.proxy.lrange(key, start, end)

    def llen(self, key: str):
        return self.adaptor.proxy.llen(key)

    def lindex(self, key: str, index: int):
        return self.adaptor.proxy.lindex(key, index)

    def lrem(self, key: str, count: int, value: str):
        return self.adaptor.proxy.lrem(key, count, value)
