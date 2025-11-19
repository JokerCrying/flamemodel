from .base_driver import BaseDriver


class StringDriver(BaseDriver):
    def incr(self, key: str, amount: int = 1):
        return self.adaptor.proxy.incr(key, amount)

    def decr(self, key: str, amount: int = 1):
        return self.adaptor.proxy.decr(key, amount)

    def append(self, key: str, value: str):
        return self.adaptor.proxy.append(key, value)

    def get_range(self, key: str, start: int, end: int):
        return self.adaptor.proxy.getrange(key, start, end)

    def set_range(self, key: str, offset: int, value: str):
        return self.adaptor.proxy.setrange(key, offset, value)
