from typing import Union, Any, Sequence, TypeVar, Type
from ..models import List, RedisModelRepository
from ..exceptions import AdapterTypeError

_ListModel = TypeVar('_ListModel', bound=List)


class ListAdaptor:
    """adaptor list operate like
        - len(model)
        - model[0]
        - model[1:2]

    :param model_type: Model type or Model name, its will find model in repo when it is string type.
    :param pk: list model primary key
    """

    def __init__(
            self,
            model_type: Union[str, Type[_ListModel]],
            pk: Any
    ):
        if isinstance(model_type, str):
            repo = RedisModelRepository()
            self.model_type = repo.parse_model_string(model_type)['model_cls']
        else:
            self.model_type = model_type
        if not issubclass(self.model_type, List):
            raise AdapterTypeError(
                f"The model {self.model_type} is not List subclass.",
                cur_type=self.model_type,
                original_type=List
            )
        self.pk = pk

    def append(self, value: _ListModel):
        return value.append()

    def pop(self, default=None):
        result = self.model_type.right_pop(self.pk)
        return result or default

    def clear(self):
        return self.model_type.clear(self.pk)

    def __len__(self):
        return self.model_type.len(self.pk)

    def __getitem__(self, item):
        result = self.model_type.get(self.pk, item)
        if not result:
            raise IndexError(item)
        return result

    def __setitem__(self, key, value: _ListModel):
        if not isinstance(value, self.model_type):
            raise TypeError(f"The value is not {self.model_type}'s subclass.")
        return self.model_type.set(self.pk, key, value)

    def __iter__(self):
        for item in self.model_type.all(self.pk):
            yield item

    async def __aiter__(self):
        async for item in self.model_type.all(self.pk):
            yield item
