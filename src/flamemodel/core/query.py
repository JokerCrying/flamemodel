from typing import TYPE_CHECKING, Type, TypeVar, Generic, Optional, List
from ..models import BaseRedisModel
from ..exceptions import FieldNotFoundError

_T = TypeVar("_T", bound=BaseRedisModel)

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
        self.model_fields_set = set([
            i for i in self.model_cls.__model_meta__.fields
        ])
        self._query_param = {}

    def filter_by(self, **kwargs) -> 'Query[Type[_T]]':
        for k in kwargs:
            if k not in self.model_fields_set:
                raise FieldNotFoundError(
                    f"Can't create a query condition for the model {self.model_cls.__name__} "
                    f"because the field {k} doesn't exist.",
                    model_cls=self.model_cls,
                    field_name=k
                )
        self._query_param.update(kwargs)
        return self  # type: ignore

    def first(self) -> Optional[_T]:
        return self.model_cls.get(**self._query_param).execute()

    def all(self) -> List[_T]:
        pass

    def update(self, **kwargs):
        pass

    def delete(self):
        pass

    def remove(self):
        pass
