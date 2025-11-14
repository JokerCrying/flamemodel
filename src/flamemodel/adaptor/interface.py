from ..d_type import (
    Endpoint, DictAny, RuntimeMode,
    RedisClientType, RedisClientInstance,
    RedisDataType
)
from ..utils.parse_endpoint import parse_endpoint
from ..utils.get_driver import get_driver
from .proxy import Proxy
from redis import Redis as SyncRedis, RedisCluster as SyncRedisCluster
from redis.asyncio import Redis as AsyncRedis, RedisCluster as AsyncRedisCluster

RedisClientTypeMap = {
    True: {
        'sync': SyncRedisCluster,
        'async': AsyncRedisCluster
    },
    False: {
        'sync': SyncRedis,
        'async': AsyncRedis
    }
}


class RedisAdaptor:
    def __init__(
            self,
            endpoint: Endpoint,
            connect_options: DictAny,
            runtime_mode: RuntimeMode
    ):
        self.url_kwargs, self.is_cluster = parse_endpoint(endpoint)
        self.connect_options = connect_options
        self.runtime_mode = runtime_mode
        self._proxy = self._init_proxy()

    def _init_proxy(self) -> RedisClientInstance:
        mode_map = RedisClientTypeMap[self.is_cluster]
        return Proxy(mode_map[self.runtime_mode], self.url_kwargs, self.connect_options)  # type: ignore

    def get_redis_driver(self, redis_type: RedisDataType):
        driver_cls = get_driver(redis_type)
        return driver_cls(self)

    @property
    def proxy(self):
        return self._proxy
