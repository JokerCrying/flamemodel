import unittest
from src.flamemodel import FlameModel
from src.flamemodel.models import BaseRedisModel
from src.flamemodel.models.fields import fields
from src.flamemodel.models.foreign import ForeignKey
from typing import Optional


class User(BaseRedisModel):
    __redis_type__ = 'string'

    id: int = fields(primary_key=True)
    tenant_id: int = fields(shard_tag=True)
    real_name: Optional[str] = fields()
    username: str = fields(unique=True)
    password: str = fields(min_length=8)
    phone_num: str = fields(unique=True)
    address: Optional[str] = fields(index=True)


class Profile(BaseRedisModel):
    __redis_type__ = 'string'

    id: int = fields(primary_key=True)
    user_id: int = fields(unique=True, foreign_key=ForeignKey('User.id', relation='one'))


class TestInitSubClass(unittest.TestCase):
    def setUp(self):
        self.client = FlameModel(
            'sync',
            'redis://:@localhost:6379/1'
        )

    def test_init_subclass(self):
        user_meta = User.__model_meta__
        profile_meta = Profile.__model_meta__
        self.assertNotEqual(user_meta, profile_meta)
