from typing import Protocol, runtime_checkable, Any, Dict, TYPE_CHECKING, Type

if TYPE_CHECKING:
    from ...models import BaseRedisModel


@runtime_checkable
class SerializerProtocol(Protocol):
    def __init__(self, options: Dict[str, Any]):
        self.options = options

    def serialize(self, instance: 'BaseRedisModel') -> bytes | str | Dict[str, Any]:
        ...

    def deserialize(self, data: bytes | str | Dict[str, Any], model_class: Type['BaseRedisModel']) -> Any:
        ...
