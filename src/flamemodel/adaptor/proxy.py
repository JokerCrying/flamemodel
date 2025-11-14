from typing import Generic
from ..d_type import RedisClientType, RedisClientInstance, RedisConnectKwargs, DictAny


class Proxy(Generic[RedisClientInstance]):
    def __init__(
            self,
            runtime_cls: RedisClientType,
            url_kwargs: RedisConnectKwargs,
            connect_kwargs: DictAny
    ):
        self.runtime_cls = runtime_cls
        self._final_kwargs = {
            **url_kwargs,
            **connect_kwargs
        }
        self._client: RedisClientInstance = runtime_cls(**self._final_kwargs)

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        return getattr(self._client, item)
