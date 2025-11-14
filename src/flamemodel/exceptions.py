class FlameModelException(Exception): pass


class UnknownEndpointTypeError(FlameModelException):
    def __init__(self, message, *, endpoint):
        self.message = message
        self.endpoint = endpoint


class UnknownRedisDataTypeError(FlameModelException):
    def __init__(self, message, *, input_type):
        self.message = message
        self.input_type = input_type


class RepeatedSetAdaptorError(FlameModelException):
    pass


class RepeatedSetModelMetadataError(FlameModelException):
    pass


class JsonSchemaExtraTypeError(FlameModelException):
    def __init__(self, message, *, error_type):
        self.message = message
        self.error_type = error_type


class JsonSchemaExtraReservedFieldOccupiedError(FlameModelException):
    pass


class ModelNotExistsError(FlameModelException):
    def __init__(self, message, *, model_type):
        self.message = message
        self.model_type = model_type


class FieldNotExistsError(FlameModelException):
    def __init__(self, message, *, field_name, fields):
        self.message = message
        self.field_name = field_name
        self.fields = fields


class KeyBuildError(FlameModelException):
    def __init__(self, message, *, template, values, on_error_key):
        self.message = message
        self.template = template
        self.values = values
        self.on_error_key = on_error_key


class TooManyPrimaryKeyError(FlameModelException):
    pass


class HasNoPrimaryKeyError(FlameModelException):
    pass
