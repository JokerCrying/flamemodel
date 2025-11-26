from typing import TYPE_CHECKING, Type, TypeVar, Generic, Optional, List

_T = TypeVar("_T")

if TYPE_CHECKING:
    from ..main import FlameModel


class Query(Generic[_T]):
    def __init__(
            self,
            app: 'FlameModel',
            model_cls: Type[_T]
    ):
        self.app = app
        self.model_cls = model_cls
        self._query_param = {}

    def filter_by(self, **kwargs) -> 'Query[Type[_T]]':
        self._query_param.update(kwargs)
        return self  # type: ignore

    def first(self) -> Optional[_T]:
        pass

    def all(self) -> List[_T]:
        pass

    def update(self, **kwargs):
        pass

    def delete(self):
        pass

    def remove(self):
        pass
