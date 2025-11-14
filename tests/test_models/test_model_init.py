import unittest
from src.flamemodel import FlameModel
from src.flamemodel.models import BaseRedisModel


class TestInitModel(unittest.TestCase):
    def setUp(self):
        self.client = FlameModel(
            'sync',
            'redis://:@localhost/0',
            {}
        )

    def test_init(self):
        print(self.client)
        self.assertIsNotNone(self.client)

    def test_model_get_driver(self):
        class TestStringModel(BaseRedisModel):
            __redis_type__ = 'string'

        driver = TestStringModel.get_driver()
        print(driver.get('a'))
        self.assertIsNotNone(driver)
