from typing import Union, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from src.flamemodel.models.redis_model import BaseRedisModel

ForeignFieldType = Union['BaseRedisModel', str]


class ForeignKey:
    def __init__(
            self,
            field: ForeignFieldType,
            relation: Literal['one', 'many'] = 'one',
            onupdate: Literal["cascade", "restrict", "setnull", "none"] = "none",
            ondelete: Literal["cascade", "restrict", "setnull", "none"] = "none",
    ):
        self.field = field
        self.foreign_type = relation
        self.onupdate = onupdate
        self.ondelete = ondelete
