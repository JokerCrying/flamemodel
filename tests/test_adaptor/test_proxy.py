import unittest
from src.flamemodel.adaptor.proxy import Proxy
from redis import Redis


class TestProxy(unittest.TestCase):
    def setUp(self):
        self.proxy = Proxy(
            Redis,
            {
                'host': 'localhost',
                'port': 6379
            },
            {
                'decode_responses': True
            }
        )

    def test_proxy(self):
        self.proxy.set('a', 1)
        print(self.proxy.get('a'))
