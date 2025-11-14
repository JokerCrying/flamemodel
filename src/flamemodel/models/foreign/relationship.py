from typing import Union, Optional, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from ..redis_model import BaseRedisModel

ModelType = Union['BaseRedisModel', str]


class Relationship:
    def __init__(
            self,
            model: ModelType,
            backref: Optional[str] = None,
            relation: Literal['one', 'many'] = 'one'
    ):
        self.model = model
        self.backref = backref
        self.relation = relation
