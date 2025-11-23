import unittest
from unittest.mock import MagicMock, AsyncMock
import asyncio
import time


# 假设 ExecutionMode 和 Action 类已经在文件中
from src.flamemodel.utils.action import ExecutionMode, Action

class MockRedisAdaptor:
    def __init__(self):
        self.proxy = MagicMock()


# 模拟的 executor 函数
def mock_executor(client, *args, **kwargs):
    time.sleep(0.1)
    return "Executed"


def mock_async_executor(client, *args, **kwargs):
    async def async_func():
        await asyncio.sleep(0.1)
        return "Async Executed"

    return async_func()


class ActionTest(unittest.TestCase):

    def setUp(self):
        # 初始化一些常用变量
        self.client = MagicMock()
        self.adaptor = MockRedisAdaptor()

    def test_single_action_sync(self):
        action = Action(
            runtime_mode='sync',
            executor=mock_executor,
            command=None,
            args=('arg1',),
            kwargs={},
            handler=None,
            sub_actions=None,
            execution_mode=ExecutionMode.SINGLE,
            client=self.client
        )

        result = action.execute()  # 执行同步动作
        self.assertEqual(result, "Executed")  # 验证执行结果是否正确

    def test_sequence_action_sync(self):
        # 创建一个顺序执行的 Action
        sub_action1 = Action(
            runtime_mode='sync',
            executor=mock_executor,
            command=None,
            args=('arg1',),
            kwargs={},
            handler=None,
            sub_actions=None,
            execution_mode=ExecutionMode.SINGLE,
            client=self.client
        )

        sub_action2 = Action(
            runtime_mode='sync',
            executor=mock_executor,
            command=None,
            args=('arg2',),
            kwargs={},
            handler=None,
            sub_actions=None,
            execution_mode=ExecutionMode.SINGLE,
            client=self.client
        )

        sequence_action = Action.sequence([sub_action1, sub_action2], runtime_mode='sync')

        result = sequence_action.execute()
        self.assertEqual(result, ["Executed", "Executed"])  # 验证顺序执行结果

    def test_transaction_action_sync(self):
        # 创建一个事务执行的 Action
        sub_action1 = Action(
            runtime_mode='sync',
            executor=mock_executor,
            command=None,
            args=('arg1',),
            kwargs={},
            handler=None,
            sub_actions=None,
            execution_mode=ExecutionMode.SINGLE,
            client=self.client
        )

        sub_action2 = Action(
            runtime_mode='sync',
            executor=mock_executor,
            command=None,
            args=('arg2',),
            kwargs={},
            handler=None,
            sub_actions=None,
            execution_mode=ExecutionMode.SINGLE,
            client=self.client
        )

        transaction_action = Action.transaction([sub_action1, sub_action2], runtime_mode='sync', client=self.client)

        result = transaction_action.execute()
        self.assertEqual(result, ["Executed", "Executed"])  # 验证事务执行结果

    def test_single_action_async(self):
        # 创建一个异步 Action
        action = Action(
            runtime_mode='async',
            executor=mock_async_executor,
            command=None,
            args=('arg1',),
            kwargs={},
            handler=None,
            sub_actions=None,
            execution_mode=ExecutionMode.SINGLE,
            client=self.client
        )

        result = asyncio.run(action.execute())  # 异步执行
        self.assertEqual(result, "Async Executed")  # 验证异步执行的结果

    def test_invalid_runtime_mode_sync(self):
        action = Action(
            runtime_mode='async',  # 这是一个异步运行模式
            executor=mock_executor,
            command=None,
            args=('arg1',),
            kwargs={},
            handler=None,
            sub_actions=None,
            execution_mode=ExecutionMode.SINGLE,
            client=self.client
        )
        with self.assertRaises(RuntimeError):
            action.run_sync()  # 如果运行模式是异步的，调用 `run_sync` 应该抛出异常

    async def test_invalid_runtime_mode_async(self):
        action = Action(
            runtime_mode='sync',  # 这是一个同步运行模式
            executor=mock_async_executor,
            command=None,
            args=('arg1',),
            kwargs={},
            handler=None,
            sub_actions=None,
            execution_mode=ExecutionMode.SINGLE,
            client=self.client
        )
        with self.assertRaises(RuntimeError):
            await action  # 如果运行模式是同步的，调用 `await` 应该抛出异常

    def test_then_chained_handler(self):
        # 创建一个带有链式处理的 Action
        action = Action(
            runtime_mode='sync',
            executor=mock_executor,
            command=None,
            args=('arg1',),
            kwargs={},
            handler=lambda result: result + " Processed",
            sub_actions=None,
            execution_mode=ExecutionMode.SINGLE,
            client=self.client
        )

        chained_action = action.then(lambda result: result + " Chained")

        result = chained_action.execute()
        self.assertEqual(result, "Executed Processed Chained")  # 验证链式调用是否生效


if __name__ == '__main__':
    unittest.main()
