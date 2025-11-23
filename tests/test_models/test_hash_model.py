import unittest
from typing import Optional
from src.flamemodel.main import FlameModel
from src.flamemodel.models import Hash
from src.flamemodel.models.fields import fields


class UserDataHash(Hash):
    __key_pattern__ = 'user-data:{id}'

    id: int = fields(primary_key=True)
    user_id: int = fields(hash_field=True)
    address: Optional[str] = fields(default=None)


class TestHashModel(unittest.TestCase):
    def setUp(self):
        self.fm = FlameModel(
            runtime_mode='async',
            endpoint='redis://:@localhost:6379/1'
        )

    def test_set(self):
        user = UserDataHash(
            id=1, user_id=1, address='你好'
        )
        user.save()

    def test_get(self):
        import asyncio
        print(asyncio.run(UserDataHash.get(1, 1)))
