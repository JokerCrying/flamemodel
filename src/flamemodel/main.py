from .d_type import (
    Endpoint, DictAny, RuntimeMode
)
from .models import (
    BaseRedisModel,
    RedisModelRepository
)
from .adaptor.interface import RedisAdaptor
from .utils.symbol_by_name import symbol_by_name
from typing import Optional


class FlameModel:

    def __init__(
            self,
            runtime_mode: RuntimeMode,
            endpoint: Endpoint,
            connect_options: Optional[DictAny] = None,
            key_builder_cls: str = 'src.flamemodel.core.key_builder:DefaultKeyBuilder',
            key_builder_options: Optional[DictAny] = None,
            serializer_cls: str = 'src.flamemodel.core.serializer:DefaultSerializer',
            serializer_options: Optional[DictAny] = None
    ):
        self.runtime_mode = runtime_mode
        self.endpoint = endpoint
        self.connect_options = connect_options or {}
        self.redis_model_repository = RedisModelRepository()
        self.adaptor = RedisAdaptor(self.endpoint, self.connect_options, self.runtime_mode)
        self.key_builder_cls = symbol_by_name(key_builder_cls)
        self.key_builder_options = key_builder_options or {}
        self.serializer_cls = symbol_by_name(serializer_cls)
        self.serializer_options = serializer_options or {}
        # on init success
        self.on_init()

    def on_init(self):
        self._set_model_adaptor()
        self._set_model_key_builder()
        self._set_model_serializer()
        self._register_models()

    def _set_model_adaptor(self):
        BaseRedisModel.set_redis_adaptor(self.adaptor)

    def _register_models(self):
        bases_models = BaseRedisModel.__subclasses__()
        for bases_model in bases_models:
            for cls in bases_model.__subclasses__():
                model_name = cls.__schema__ or cls.__name__
                self.redis_model_repository.register_model(model_name, cls)

    def _set_model_key_builder(self):
        key_builder_instance = self.key_builder_cls(**self.key_builder_options)
        BaseRedisModel.set_key_builder(key_builder_instance)

    def _set_model_serializer(self):
        serializer_instance = self.serializer_cls(self.serializer_options)
        BaseRedisModel.set_serializer(serializer_instance)

    def __repr__(self):
        return f'<FlameModel runtime_mode={self.runtime_mode} endpoint={self.endpoint}>'

    def __str__(self):
        return repr(self)
