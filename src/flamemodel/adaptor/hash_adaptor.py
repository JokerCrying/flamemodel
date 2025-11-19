from typing import Union, Any, Optional, TypeVar, Mapping
from ..models import RedisModelRepository, Hash
from ..exceptions import AdapterTypeError

_HashModel = TypeVar('_HashModel', bound=Hash)


class HashAdaptor(Mapping):
    """adaptor dict/mapping operate like
        - model[key] = model
        - model[key]
        - model.get(key, Any)
        - del model[key]...

    :param model_type: Model type or Model name, its will find model in repo when it is string type.
    :param pk: hash model primary key
    """

    def __init__(
            self,
            model_type: Union[str, _HashModel],
            pk: Any
    ):
        if isinstance(model_type, str):
            repo = RedisModelRepository()
            self.model_type = repo.parse_model_string(model_type)['model_cls']
        else:
            self.model_type = model_type
        if not issubclass(self.model_type, Hash):
            raise AdapterTypeError(
                f"The model {self.model_type} is not Hash subclass.",
                cur_type=self.model_type,
                original_type=Hash
            )
        self.pk = pk

    def get(self, key, default: Any = None) -> Optional[_HashModel]:
        return self.model_type.get(self.pk, key) or default

    def __getitem__(self, item):
        result = self.get(item, None)
        if result is None:
            raise KeyError(item)
        return result

    def __len__(self):
        return len(self.keys())

    def __iter__(self):
        for i in self.keys():
            yield i

    async def __aiter__(self):
        async for i in self.keys():
            yield i

    def __contains__(self, item):
        try:
            self[item]
        except KeyError:
            return False
        return True

    def keys(self):
        return self.model_type.keys(self.pk)

    def values(self):
        return self.model_type.values(self.pk)
