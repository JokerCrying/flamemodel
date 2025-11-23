from ..utils.action import Action
from typing import Generic, Callable, TYPE_CHECKING, Any, Union
from ..d_type import RedisClientType, RedisClientInstance, RedisConnectKwargs, DictAny, RuntimeMode

if TYPE_CHECKING:
    from .interface import RedisAdaptor


class Proxy(Generic[RedisClientInstance]):
    def __init__(
            self,
            runtime_cls: RedisClientType,
            url_kwargs: RedisConnectKwargs,
            connect_kwargs: DictAny,
            runtime_mode: RuntimeMode,
            adaptor: 'RedisAdaptor'
    ):
        self.adaptor = adaptor
        self.runtime_mode = runtime_mode
        self.runtime_cls = runtime_cls
        self._final_kwargs = {
            **url_kwargs,
            **connect_kwargs
        }
        self._client: RedisClientInstance = runtime_cls(**self._final_kwargs)

    def __getattr__(self, item) -> Union[Action, Any]:
        if item in self.__dict__:
            return self.__dict__[item]
        redis_proxy = getattr(self._client, item)
        if not callable(redis_proxy):
            return redis_proxy
        return self._wrap_action(redis_proxy, item)

    def _wrap_action(self, function: Callable, command: str) -> Callable:
        def wrapper(*args, **kwargs):
            return Action(
                runtime_mode=self.runtime_mode,
                executor=function,
                args=args,
                kwargs=kwargs,
                execution_mode='single',
                adaptor=self.adaptor,
                command=command
            )

        return wrapper
