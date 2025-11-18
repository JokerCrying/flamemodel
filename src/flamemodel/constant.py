import sys
from .d_type import ReadOnlyModule

# field control reserved key, save to pydantic.Field argument json_schema_extra
FlameModelJsonSchemaKey = '_flame_model'

# model of string type or foreign key delimiter
StringModelDelimiter = '.'

# the field names in json schema extra used by pydantic for storage
PydanticPropertyField = 'properties'

# to use delimiter of redis key when build redis key
RedisKeyDelimiter = ':'


_current_module = sys.modules[__name__]
read_only_module = ReadOnlyModule(__name__)
read_only_module.__dict__.update(_current_module.__dict__)

sys.modules[__name__] = read_only_module
