from .base_driver import BaseDriver


class SetDriver(BaseDriver):
    def sadd(self, key: str, *members):
        return self.adaptor.proxy.sadd(key, *members)

    def srem(self, key: str, *members):
        return self.adaptor.proxy.srem(key, *members)

    def smembers(self, key: str):
        return self.adaptor.proxy.smembers(key)

    def sismember(self, key: str, member: str):
        return self.adaptor.proxy.sismember(key, member)

    def scard(self, key: str):
        return self.adaptor.proxy.scard(key)

    def spop(self, key: str):
        return self.adaptor.proxy.spop(key)

    def srandmember(self, key: str, count: int = 1):
        return self.adaptor.proxy.srandmember(key, count)

