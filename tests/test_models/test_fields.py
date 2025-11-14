import unittest
from src.flamemodel.constant import FlameModelJsonSchemaKey
from src.flamemodel.models.fields import fields
from src.flamemodel.models.redis_model import BaseRedisModel


def json_schema_extra_func(schema):
    schema['max_value'] = 100


class UserRedisModel(BaseRedisModel):
    __redis_type__ = 'string'
    __key_pattern__ = 'user:{id}'

    id: int = fields(
        json_schema_extra=json_schema_extra_func
    )


class TestFields(unittest.TestCase):
    def setUp(self):
        self.model_instance = UserRedisModel(id=1)

    def test_json_schema_extra(self):
        model_json_schema = self.model_instance.model_json_schema()
        fields_json_schema = model_json_schema['properties']
        id_json_schema = fields_json_schema['id']
        print('model json schema ->', model_json_schema)
        print('fields json schema ->', fields_json_schema)
        print('id fields schema ->', id_json_schema)
        self.assertIn(FlameModelJsonSchemaKey, id_json_schema.keys())
