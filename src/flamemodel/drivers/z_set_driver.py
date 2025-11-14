from .base_driver import BaseDriver


class ZSetDriver(BaseDriver):
    def zadd(self, key: str, mapping: dict):
        return self.adaptor.proxy.zadd(key, mapping)

    def zrem(self, key: str, *members):
        return self.adaptor.proxy.zrem(key, *members)

    def zscore(self, key: str, member: str):
        return self.adaptor.proxy.zscore(key, member)

    def zrange(self, key: str, start: int, end: int, withscores: bool = False):
        return self.adaptor.proxy.zrange(key, start, end, withscores=withscores)

    def zrevrange(self, key: str, start: int, end: int, withscores: bool = False):
        return self.adaptor.proxy.zrevrange(key, start, end, withscores=withscores)

    def zincrby(self, key: str, amount: float, member: str):
        return self.adaptor.proxy.zincrby(key, amount, member)

    def zrank(self, key: str, member: str):
        return self.adaptor.proxy.zrank(key, member)
