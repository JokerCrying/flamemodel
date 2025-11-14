from types import ModuleType
import sys

# field control reserved key, save to pydantic.Field argument json_schema_extra
FlameModelJsonSchemaKey = '_flame_model'

# model of string type or foreign key delimiter
StringModelDelimiter = '.'

# the field names in json schema extra used by pydantic for storage
PydanticPropertyField = 'properties'

# to use delimiter of redis key when build redis key
RedisKeyDelimiter = ':'


class _ReadOnlyModule(ModuleType):
    def __setattr__(self, key, value):
        raise ValueError(
            "Don't try to modify the value of a constant variable!"
        )

    def __delattr__(self, key):
        raise ValueError(
            "Don't try to delete the value of a constant variable!"
        )


_current_module = sys.modules[__name__]
read_only_module = _ReadOnlyModule(__name__)
read_only_module.__dict__.update(_current_module.__dict__)

sys.modules[__name__] = read_only_module
