import inspect
from enum import Enum, auto
from typing import Any, Callable, List, Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from ..adaptor.interface import RedisAdaptor

class ExecutionMode(Enum):
    SINGLE = auto()
    SEQUENCE = auto()
    TRANSACTION = auto()


class Action:
    def __init__(
            self,
            runtime_mode,
            executor: Optional[Callable] = None,
            command: Optional[str] = None,
            args: Optional[tuple] = None,
            kwargs: Optional[dict] = None,
            handler: Optional[Callable[[Any], Any]] = None,
            sub_actions: Optional[List['Action']] = None,
            execution_mode: ExecutionMode = ExecutionMode.SINGLE,
            result_from_index: Optional[int] = -1,
            client: Any = None,
            adaptor: 'RedisAdaptor' = None
    ):
        self.runtime_mode = runtime_mode
        self._executor = executor
        self._command = command
        self._args = args or ()
        self._kwargs = kwargs or {}
        self._handler = handler
        self._sub_actions = sub_actions or []
        self._execution_mode = execution_mode
        self._result_from_index = result_from_index
        self.client = client
        self._adaptor = adaptor
        if self.client is None and self._adaptor is not None:
            self.client = self._adaptor.proxy

    def with_client(self, client) -> 'Action':
        new = self.clone()
        new.client = client
        return new

    def with_adaptor(self, adaptor: 'RedisAdaptor') -> 'Action':
        new = self.clone()
        new._adaptor = adaptor
        new.client = adaptor.proxy
        return new

    def __await__(self):
        if self.runtime_mode != 'async':
            raise RuntimeError(
                "Cannot 'await' an Action in 'sync' runtime mode. Use .run_sync() instead."
            )
        return self._execute_async().__await__()

    def execute(self):
        if self.runtime_mode == 'sync':
            return self._execute_sync()
        return self._execute_async()

    def run_sync(self) -> Any:
        if self.runtime_mode != 'sync':
            raise RuntimeError(
                "Cannot .run_sync() an Action in 'async' runtime mode. Use 'await' instead."
            )
        return self._execute_sync()

    def then(self, handler: Callable[[Any], Any]) -> 'Action':
        new_action = self.clone()
        if new_action._handler:
            original_handler = new_action._handler
            def chained_handler(result):
                return handler(original_handler(result))
            new_action._handler = chained_handler
        else:
            new_action._handler = handler
        return new_action

    @classmethod
    def sequence(cls, actions: List['Action'], runtime_mode, result_from_index: int = -1, client: Any = None) -> 'Action':
        return cls(
            runtime_mode=runtime_mode,
            sub_actions=actions,
            execution_mode=ExecutionMode.SEQUENCE,
            result_from_index=result_from_index,
            client=client
        )

    @classmethod
    def transaction(cls, actions: List['Action'], runtime_mode, client: Any) -> 'Action':
        return cls(
            runtime_mode=runtime_mode,
            sub_actions=actions,
            execution_mode=ExecutionMode.TRANSACTION,
            client=client
        )

    def clone(self) -> 'Action':
        return Action(
            runtime_mode=self.runtime_mode,
            executor=self._executor,
            args=self._args,
            kwargs=self._kwargs,
            handler=self._handler,
            sub_actions=self._sub_actions,
            execution_mode=self._execution_mode,
            result_from_index=self._result_from_index,
            client=self.client
        )

    def _apply_handler(self, value: Any) -> Any:
        return self._handler(value) if self._handler else value

    def _execute_sync(self) -> Any:
        if self._execution_mode == ExecutionMode.SINGLE:
            if self.client is None and self._adaptor is not None:
                self.client = self._adaptor.proxy
            if self._executor:
                result = self._executor(self.client, *self._args, **self._kwargs)
            elif self._command:
                method = getattr(self.client, self._command)
                result = method(*self._args, **self._kwargs)
            else:
                result = None
            return self._apply_handler(result)
        if self._execution_mode == ExecutionMode.SEQUENCE:
            results = []
            for a in self._sub_actions:
                if self.client and getattr(a, 'client', None) is None:
                    a = a.with_client(self.client)
                results.append(a._execute_sync())
            if isinstance(self._result_from_index, int) and 0 <= self._result_from_index < len(results):
                agg = results[self._result_from_index]
            else:
                agg = results
            return self._apply_handler(agg)
        if self._execution_mode == ExecutionMode.TRANSACTION:
            if not self.client:
                if self._adaptor is not None:
                    self.client = self._adaptor.proxy
                else:
                    raise RuntimeError("Transaction requires a client.")
            pipe = self.client.pipeline(transaction=True)
            for a in self._sub_actions:
                if not (a._executor or a._command):
                    continue
                if a._executor:
                    a._executor(pipe, *a._args, **a._kwargs)
                else:
                    getattr(pipe, a._command)(*a._args, **a._kwargs)
            exec_result = pipe.execute()
            post = []
            i = 0
            for a in self._sub_actions:
                if a._executor or a._command:
                    r = exec_result[i]
                    post.append(a._handler(r) if a._handler else r)
                    i += 1
            if isinstance(self._result_from_index, int) and 0 <= self._result_from_index < len(post):
                agg = post[self._result_from_index]
            else:
                agg = post
            return self._apply_handler(agg)
        raise TypeError("execution mode not supported.")

    async def _execute_async(self) -> Any:
        if self._execution_mode == ExecutionMode.SINGLE:
            if self.client is None and self._adaptor is not None:
                self.client = self._adaptor.proxy
            if self._executor:
                res = self._executor(self.client, *self._args, **self._kwargs)
            elif self._command:
                method = getattr(self.client, self._command)
                res = method(*self._args, **self._kwargs)
            else:
                res = None
            if inspect.isawaitable(res):
                res = await res
            return self._apply_handler(res)
        if self._execution_mode == ExecutionMode.SEQUENCE:
            results = []
            for a in self._sub_actions:
                if self.client and getattr(a, 'client', None) is None:
                    a = a.with_client(self.client)
                results.append(await a._execute_async())
            if isinstance(self._result_from_index, int) and 0 <= self._result_from_index < len(results):
                agg = results[self._result_from_index]
            else:
                agg = results
            return self._apply_handler(agg)
        if self._execution_mode == ExecutionMode.TRANSACTION:
            if not self.client:
                if self._adaptor is not None:
                    self.client = self._adaptor.proxy
                else:
                    raise RuntimeError("Transaction requires a client.")
            pipe = self.client.pipeline(transaction=True)
            for a in self._sub_actions:
                if not (a._executor or a._command):
                    continue
                if a._executor:
                    a._executor(pipe, *a._args, **a._kwargs)
                else:
                    getattr(pipe, a._command)(*a._args, **a._kwargs)
            exec_result = await pipe.execute()
            post = []
            i = 0
            for a in self._sub_actions:
                if a._executor or a._command:
                    r = exec_result[i]
                    post.append(a._handler(r) if a._handler else r)
                    i += 1
            if isinstance(self._result_from_index, int) and 0 <= self._result_from_index < len(post):
                agg = post[self._result_from_index]
            else:
                agg = post
            return self._apply_handler(agg)
        raise TypeError("execution mode not supported.")