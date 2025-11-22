from enum import Enum, auto
from typing import Any, Callable, List, Optional


class ExecutionMode(Enum):
    SINGLE = auto()
    SEQUENCE = auto()
    TRANSACTION = auto()


class Action:
    """
    A unified, composable object representing one or more Redis operations.
    It enforces correct usage based on the runtime_mode ('sync' or 'async').
    """

    def __init__(
            self,
            runtime_mode,
            args: Optional[tuple] = None,
            kwargs: Optional[dict] = None,
            handler: Optional[Callable[[Any], Any]] = None,
            sub_actions: Optional[List['Action']] = None,
            execution_mode: ExecutionMode = ExecutionMode.SINGLE,
            result_from_index: Optional[int] = -1
    ):
        self.runtime_mode = runtime_mode
        self._args = args or ()
        self._kwargs = kwargs or {}
        self._handler = handler
        self._sub_actions = sub_actions or []
        self._execution_mode = execution_mode
        self._result_from_index = result_from_index

    def __await__(self):
        if self.runtime_mode != 'async':
            raise RuntimeError(
                "Cannot 'await' an Action in 'sync' runtime mode. Use .run_sync() instead."
            )
        return self._execute_async().__await__()

    def run_sync(self) -> Any:
        """Explicitly run the action in synchronous mode."""
        if self.runtime_mode != 'sync':
            raise RuntimeError(
                "Cannot .run_sync() an Action in 'async' runtime mode. Use 'await' instead."
            )
        return self._execute_sync()

    def then(self, handler: Callable[[Any], Any]) -> 'Action':
        """Chain a post-processing function to this action."""
        new_action = self.clone()
        if self._handler:
            original_handler = self._handler

            def chained_handler(result):
                return handler(original_handler(result))

            new_action._handler = chained_handler
        else:
            new_action._handler = handler
        return new_action

    @classmethod
    def sequence(cls, actions: List['Action'], runtime_mode, result_from_index: int = -1) -> 'Action':
        """Create an action that executes a list of actions sequentially."""
        return cls(
            runtime_mode=runtime_mode,
            sub_actions=actions,
            execution_mode=ExecutionMode.SEQUENCE,
            result_from_index=result_from_index
        )

    @classmethod
    def transaction(cls, actions: List['Action'], runtime_mode) -> 'Action':
        """Create an action that executes a list of actions in a MULTI/EXEC block."""
        return cls(
            runtime_mode=runtime_mode,
            sub_actions=actions,
            execution_mode=ExecutionMode.TRANSACTION
        )

    def clone(self) -> 'Action':
        """Create a shallow copy of the action."""
        return Action(
            runtime_mode=self.runtime_mode,
            args=self._args,
            kwargs=self._kwargs,
            handler=self._handler,
            sub_actions=self._sub_actions,
            execution_mode=self._execution_mode,
            result_from_index=self._result_from_index
        )

    def _execute_sync(self) -> Any:
        """The core execution logic for sync mode."""
        return 1

    async def _execute_async(self) -> Any:
        """The core execution logic for async mode."""
        return 2


if __name__ == '__main__':
    import asyncio

    action = Action(
        'sync'
    )

    print(action)
