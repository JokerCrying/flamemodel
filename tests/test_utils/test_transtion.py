import unittest
from src.flamemodel.main import FlameModel
from src.flamemodel.models import String
from src.flamemodel.models.fields import fields
from src.flamemodel.drivers.string_model_driver import StringDriver
from src.flamemodel.utils.action import Action


class User(String):
    __key_pattern__ = 'user:{id}'

    id: int = fields(primary_key=True)
    name: str = fields()
    age: int = fields()



class TestUserTransaction(unittest.TestCase):
    def setUp(self):
        self.fm = FlameModel(
            'async',
            'redis://:@localhost:6379/1'
        )
        self.string_driver = StringDriver(
            adaptor=self.fm.adaptor
        )

    def test_set(self):
        user = User(id=1, name='Jack', age=12)
        user.save()
        print(user.get_primary_key())

    def test_get(self):
        user = User.get(1)
        print(user)

    def test_transaction(self):
        import asyncio
        action1 = self.string_driver.get('User:1').then(
            lambda x: User.__serializer__.deserialize(x, User)
        )
        action2 = self.string_driver.get('User:2').then(
            lambda x: User.__serializer__.deserialize(x, User)
        )
        act = Action.transaction(
            [action1, action2],
            runtime_mode=self.fm.runtime_mode,
            client=self.fm.adaptor.proxy,
            result_from_index=0
        )
        proxy_result = asyncio.run(act.execute())
        print(proxy_result)
