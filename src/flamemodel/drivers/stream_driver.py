from .base_driver import BaseDriver


class StreamDriver(BaseDriver):
    def xadd(self, key: str, fields: dict, id: str = "*"):
        return self.adaptor.proxy.xadd(key, fields, id=id)

    def xread(self, streams: dict, count: int = None, block: int = None):
        return self.adaptor.proxy.xread(streams=streams, count=count, block=block)

    def xrange(self, key: str, start: str = "-", end: str = "+", count: int = None):
        return self.adaptor.proxy.xrange(key, start=start, end=end, count=count)

    def xdel(self, key: str, *ids):
        return self.adaptor.proxy.xdel(key, *ids)

    def xlen(self, key: str):
        return self.adaptor.proxy.xlen(key)
