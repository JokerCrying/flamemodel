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


class JsonSchemaExtraTypeError(FlameModelException):
    def __init__(self, message, *, error_type):
        self.message = message
        self.error_type = error_type


class JsonSchemaExtraReservedFieldOccupiedError(FlameModelException):
    pass


class JsonSchemaExtraFieldsReservedFieldOccupiedError(FlameModelException):
    pass
