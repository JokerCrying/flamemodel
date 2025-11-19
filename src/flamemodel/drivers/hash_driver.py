from .base_driver import BaseDriver


class HashDriver(BaseDriver):
    def hset(self, key: str, field: str, value: str):
        return self.adaptor.proxy.hset(key, field, value)

    def hmset(self, key: str, mapping: dict):
        return self.adaptor.proxy.hset(key, mapping=mapping)

    def hget(self, key: str, field: str):
        return self.adaptor.proxy.hget(key, field)

    def hmget(self, key: str, fields: list):
        return self.adaptor.proxy.hmget(key, fields)

    def hdel(self, key: str, *fields):
        return self.adaptor.proxy.hdel(key, *fields)

    def hgetall(self, key: str):
        return self.adaptor.proxy.hgetall(key)

    def hexists(self, key: str, field: str):
        return self.adaptor.proxy.hexists(key, field)

    def hkeys(self, key: str):
        return self.adaptor.proxy.hkeys(key)

    def hvals(self, key: str):
        return self.adaptor.proxy.hvals(key)
