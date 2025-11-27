from .redis_model import BaseRedisModel


class String(BaseRedisModel):
    __redis_type__ = 'string'

    def incr(self, amount: int = 1):
        driver = self.get_driver()
        pk = self.get_primary_key()
        return driver.incr(pk, amount)

    def decr(self, amount: int = 1):
        driver = self.get_driver()
        pk = self.get_primary_key()
        return driver.decr(pk, amount)
