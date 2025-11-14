import unittest
from src.flamemodel import FlameModel
from src.flamemodel.models import BaseRedisModel
from src.flamemodel.models.fields import fields


class UserModel(BaseRedisModel):
    id: int = fields(primary_key=True)


class TestRepository(unittest.TestCase):
    def setUp(self):
        self.client = FlameModel(
            'sync',
            'redis://:@localhost:8888/0',
            {}
        )

    def test_init_subclass(self):
        repo_models = self.client.redis_model_repository._repo
        self.assertIn('UserModel', repo_models)
