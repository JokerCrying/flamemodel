from .. import drivers as drivers
from ..d_type import RedisDataType
from typing import Dict, Type
from ..exceptions import UnknownRedisDataTypeError

_RedisDataMap: Dict[RedisDataType, Type[drivers.BaseDriver]] = {
    'string': drivers.StringDriver,
    'list': drivers.ListDriver,
    'stream': drivers.StreamDriver,
    'geo': drivers.GeoDriver,
    'hash': drivers.HashDriver,
    'hyper_log_log': drivers.HyperLogLogDriver,
    'set': drivers.SetDriver,
    'zset': drivers.ZSetDriver,
    'bitmap': drivers.BitmapDriver
}


def get_driver(redis_type: RedisDataType) -> Type[drivers.BaseDriver]:
    if redis_type not in _RedisDataMap:
        redis_types = list(_RedisDataMap.keys())
        err_msg = f'unknown redis data type, it must be: {"/".join(redis_types)}'
        raise UnknownRedisDataTypeError(err_msg, input_type=redis_type)
    return _RedisDataMap[redis_type]
