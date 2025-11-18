import re
import sys
import typing as _t
import annotated_types
from types import ModuleType
from pydantic.config import JsonDict
from pydantic.fields import FieldInfo, Deprecated
from pydantic import AliasChoices, AliasPath, types
from redis import Redis as SyncRedis, RedisCluster as SyncRedisCluster
from redis.asyncio import Redis as AsyncRedis, RedisCluster as AsyncRedisCluster

if sys.version_info > (3, 10):
    SelfInstance = _t.Self
else:
    SelfInstance = _t.Any


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class ReadOnlyModule(ModuleType):
    def __setattr__(self, key, value):
        raise ValueError(
            "Don't try to modify the value of a constant variable!"
        )

    def __delattr__(self, key):
        raise ValueError(
            "Don't try to delete the value of a constant variable!"
        )


class ClusterModeType(_t.TypedDict, total=False):
    host: str
    port: int


class RedisConnectKwargs(_t.TypedDict, total=False):
    username: str
    password: str
    host: str
    port: int
    db: int
    path: str


class PydanticFieldKwargs(_t.TypedDict, total=False):
    default: Ellipsis
    alias: _t.Optional[str]
    alias_priority: int | None
    validation_alias: str | AliasPath | AliasChoices | None
    serialization_alias: str | None
    title: str | None
    field_title_generator: _t.Callable[[str, FieldInfo], str] | None
    description: str | None
    examples: list[_t.Any] | None
    exclude: bool | None
    exclude_if: _t.Callable[[_t.Any], bool] | None
    discriminator: str | types.Discriminator | None
    deprecated: Deprecated | str | bool | None
    json_schema_extra: JsonDict | _t.Callable[[JsonDict], None] | None
    frozen: bool | None
    validate_default: bool | None
    repr: bool
    init: bool | None
    init_var: bool | None
    kw_only: bool | None
    pattern: str | re.Pattern[str] | None
    strict: bool | None
    coerce_numbers_to_str: bool | None
    gt: annotated_types.SupportsGt | None
    ge: annotated_types.SupportsGe | None
    lt: annotated_types.SupportsLt | None
    le: annotated_types.SupportsLe | None
    multiple_of: float | None
    allow_inf_nan: bool | None
    max_digits: int | None
    decimal_places: int | None
    min_length: int | None
    max_length: int | None
    union_mode: _t.Literal['smart', 'left_to_right']
    fail_fast: bool | None
    default_factory: _t.Callable[[], _t.Any]


Endpoint = _t.Union[
    str,  # url
    RedisConnectKwargs,  # connection kwargs
    _t.List[ClusterModeType],  # cluster
]

RuntimeMode = _t.Literal['sync', 'async']

RedisClientInstance = _t.TypeVar('RedisClientInstance', SyncRedis, AsyncRedis, AsyncRedisCluster, SyncRedisCluster)

RedisClientType = _t.Type[RedisClientInstance]

DictAny = _t.Dict[str, _t.Any]

RedisDataType = _t.Literal[
    'string', 'list', 'hash', 'stream', 'hyper_log_log',
    'set', 'zset', 'geo', 'bitmap'
]
