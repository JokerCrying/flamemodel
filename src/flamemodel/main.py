from .d_type import (
    Endpoint, DictAny, RuntimeMode
)
from .models import (
    BaseRedisModel,
    RedisModelRepository
)
from .adaptor.interface import RedisAdaptor
from .utils.symbol_by_name import symbol_by_name
from typing import Optional, ClassVar


class FlameModel:
    __key_builder_cls__: ClassVar[str] = 'src.flamemodel.utils.key_builder:KeyBuilder'

    def __init__(
            self,
            runtime_mode: RuntimeMode,
            endpoint: Endpoint,
            connect_options: Optional[DictAny] = None
    ):
        self.runtime_mode = runtime_mode
        self.endpoint = endpoint
        self.connect_options = connect_options or {}
        self.connect_options['decode_responses'] = True
        self.redis_model_repository = RedisModelRepository()
        self.adaptor = RedisAdaptor(self.endpoint, self.connect_options, self.runtime_mode)
        self.key_builder_cls = symbol_by_name(self.__key_builder_cls__)
        # on init success
        self.on_init()

    def on_init(self):
        self._set_model_adaptor()
        self._register_models()

    def _set_model_adaptor(self):
        BaseRedisModel.set_redis_adaptor(self.adaptor)

    def _register_models(self):
        models = BaseRedisModel.__subclasses__()
        for cls in models:
            model_name = cls.__schema__ or cls.__name__
            self.redis_model_repository.register_model(model_name, cls)
