import unittest
from src.flamemodel import FlameModel


class TestMakeDriver(unittest.TestCase):
    def setUp(self):
        self.client = FlameModel(
            'sync',
            'redis://:@localhost:6379/0',
            {}
        )

    def test_get_driver(self):
        string_driver = self.client.adaptor.get_redis_driver('string')
        print(string_driver)

    def test_driver_single(self):
        string_driver1 = self.client.adaptor.get_redis_driver('string')
        string_driver2 = self.client.adaptor.get_redis_driver('string')
        self.assertIs(id(string_driver1), id(string_driver2))
