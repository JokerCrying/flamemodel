from .base_driver import BaseDriver


class StreamDriver(BaseDriver):
    def xadd(self, key: str, fields: dict, id: str = "*"):
        return self.adaptor.proxy.xadd(key, fields, id=id)

    def xread(self, streams: dict, count: int = None, block: int = None):
        return self.adaptor.proxy.xread(streams=streams, count=count, block=block)

    def xrange(self, key: str, start: str = "-", end: str = "+", count: int = None):
        return self.adaptor.proxy.xrange(key, min=start, max=end, count=count)

    def xdel(self, key: str, *ids):
        return self.adaptor.proxy.xdel(key, *ids)

    def xlen(self, key: str):
        return self.adaptor.proxy.xlen(key)

    def xrevrange(self, key: str, max: str = "+", min: str = "-",
                  count: int = None):
        return self.adaptor.proxy.xrevrange(key, max=max, min=min, count=count)

    def xtrim(self, key: str, maxlen: int, approximate: bool = True):
        return self.adaptor.proxy.xtrim(key, maxlen=maxlen, approximate=approximate)
