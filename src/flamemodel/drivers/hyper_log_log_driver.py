from .base_driver import BaseDriver


class HyperLogLogDriver(BaseDriver):
    def pfadd(self, key: str, *elements):
        return self.adaptor.proxy.pfadd(key, *elements)

    def pfcount(self, key: str):
        return self.adaptor.proxy.pfcount(key)

    def pfmerge(self, destkey: str, *sourcekeys):
        return self.adaptor.proxy.pfmerge(destkey, *sourcekeys)
