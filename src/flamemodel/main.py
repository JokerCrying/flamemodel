from .d_type import (
    Endpoint, DictAny, RuntimeMode
)
from .models import BaseRedisModel
from .adaptor.interface import RedisAdaptor
from typing import Optional


class FlameModel:
    def __init__(
            self,
            runtime_mode: RuntimeMode,
            endpoint: Endpoint,
            connect_options: Optional[DictAny] = None
    ):
        self.runtime_mode = runtime_mode
        self.endpoint = endpoint
        self.connect_options = connect_options or {}
        self.adaptor = RedisAdaptor(self.endpoint, self.connect_options, self.runtime_mode)
        BaseRedisModel.set_redis_adaptor(self.adaptor)
