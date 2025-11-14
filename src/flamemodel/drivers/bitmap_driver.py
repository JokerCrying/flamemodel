from .base_driver import BaseDriver


class BitmapDriver(BaseDriver):
    def setbit(self, key: str, offset: int, value: int):
        return self.adaptor.proxy.setbit(key, offset, value)

    def getbit(self, key: str, offset: int):
        return self.adaptor.proxy.getbit(key, offset)

    def bitcount(self, key: str):
        return self.adaptor.proxy.bitcount(key)

    def bitop(self, operation: str, destkey: str, *keys):
        return self.adaptor.proxy.bitop(operation, destkey, *keys)
