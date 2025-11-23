import inspect
from enum import Enum
from typing import Any, Callable, List, Optional, TYPE_CHECKING, Union, Literal

if TYPE_CHECKING:
    from ..adaptor.interface import RedisAdaptor

class ExecutionMode(Enum):
    SINGLE = 'single'
    SEQUENCE = 'sequence'
    TRANSACTION = 'transaction'


ExecutionModeType = Union[Literal['single', 'sequence', 'transaction'], ExecutionMode]

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
            execution_mode: ExecutionModeType = ExecutionMode.SINGLE,
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
        if isinstance(execution_mode, str):
            try:
                self._execution_mode = ExecutionMode(execution_mode)
            except ValueError:
                raise ValueError(
                    "Action execute mode type must be "
                    f"'single', 'sequence', 'transaction', got {execution_mode}"
                )
        else:
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
    def transaction(cls, actions: List['Action'], runtime_mode, client: Any, result_from_index: int = -1) -> 'Action':
        return cls(
            runtime_mode=runtime_mode,
            sub_actions=actions,
            execution_mode=ExecutionMode.TRANSACTION,
            client=client,
            result_from_index=result_from_index
        )

    def clone(self) -> 'Action':
        return Action(
            runtime_mode=self.runtime_mode,
            executor=self._executor,
            command=self._command,
            args=self._args,
            kwargs=self._kwargs,
            handler=self._handler,
            sub_actions=self._sub_actions,
            execution_mode=self._execution_mode,
            result_from_index=self._result_from_index,
            client=self.client,
            adaptor=self._adaptor
        )

    async def _apply_handler_async(self, value: Any) -> Any:
        if not self._handler:
            return value
        out = self._handler(value)
        if isinstance(out, Action):
            return await out._execute_async()
        if inspect.isawaitable(out):
            return await out
        return out

    def _apply_handler_sync(self, value: Any) -> Any:
        if not self._handler:
            return value
        out = self._handler(value)
        if isinstance(out, Action):
            return out._execute_sync()
        if inspect.isawaitable(out):
            raise RuntimeError("Handler returned awaitable in sync runtime mode")
        return out

    def _execute_sync(self) -> Any:
        if self._execution_mode == ExecutionMode.SINGLE:
            if self.client is None and self._adaptor is not None:
                self.client = self._adaptor.proxy
            if self._executor:
                result = self._executor(*self._args, **self._kwargs)
            elif self._command:
                method = getattr(self.client, self._command)
                result = method(*self._args, **self._kwargs)
            else:
                result = None
            if isinstance(result, Action):
                result = result._execute_sync()
            if inspect.isawaitable(result):
                raise RuntimeError("Executor returned awaitable in sync runtime mode")
            return self._apply_handler_sync(result)
        if self._execution_mode == ExecutionMode.SEQUENCE:
            results = []
            for a in self._sub_actions:
                if self.client and getattr(a, 'client', None) is None:
                    a = a.with_client(self.client)
                results.append(a._execute_sync())
            if isinstance(self._result_from_index, int) and -1 <= self._result_from_index < len(results):
                agg = results[self._result_from_index]
            else:
                agg = results
            return self._apply_handler_sync(agg)
        if self._execution_mode == ExecutionMode.TRANSACTION:
            if not self.client:
                if self._adaptor is not None:
                    self.client = self._adaptor.proxy
                else:
                    raise RuntimeError("Transaction requires a client.")
            pipe_proxy = self.client.pipeline(transaction=True)
            pipe = pipe_proxy.execute()
            for a in self._sub_actions:
                if not a._command:
                    raise RuntimeError("Action transaction mode only support command.")
                getattr(pipe, a._command)(*a._args, **a._kwargs)
            exec_result = pipe.execute()
            post = []
            i = 0
            for a in self._sub_actions:
                if a._command:
                    r = exec_result[i]
                    post.append(a._apply_handler_sync(r))
                    i += 1
            if isinstance(self._result_from_index, int) and -1 <= self._result_from_index < len(post):
                agg = post[self._result_from_index]
            else:
                agg = post
            return self._apply_handler_sync(agg)
        raise TypeError("execution mode not supported.")

    async def _execute_async(self) -> Any:
        if self._execution_mode == ExecutionMode.SINGLE:
            if self.client is None and self._adaptor is not None:
                self.client = self._adaptor.proxy
            if self._executor:
                res = self._executor(*self._args, **self._kwargs)
            elif self._command:
                method = getattr(self.client, self._command)
                res = method(*self._args, **self._kwargs)
            else:
                res = None
            if inspect.isawaitable(res):
                res = await res
            if isinstance(res, Action):
                res = await res._execute_async()
            return await self._apply_handler_async(res)
        if self._execution_mode == ExecutionMode.SEQUENCE:
            results = []
            for a in self._sub_actions:
                if self.client and getattr(a, 'client', None) is None:
                    a = a.with_client(self.client)
                results.append(await a._execute_async())
            if isinstance(self._result_from_index, int) and -1 <= self._result_from_index < len(results):
                agg = results[self._result_from_index]
            else:
                agg = results
            return await self._apply_handler_async(agg)
        if self._execution_mode == ExecutionMode.TRANSACTION:
            if not self.client:
                if self._adaptor is not None:
                    self.client = self._adaptor.proxy
                else:
                    raise RuntimeError("Transaction requires a client.")
            pipe_proxy = self.client.pipeline(transaction=True)
            pipe = await pipe_proxy.execute()
            for a in self._sub_actions:
                if not a._command:
                    raise RuntimeError("Action transaction mode only support command.")
                await getattr(pipe, a._command)(*a._args, **a._kwargs)
            exec_result = await pipe.execute()
            post = []
            i = 0
            for a in self._sub_actions:
                if a._executor or a._command:
                    r = exec_result[i]
                    post.append(await a._apply_handler_async(r))
                    i += 1
            if isinstance(self._result_from_index, int) and -1 <= self._result_from_index < len(post):
                agg = post[self._result_from_index]
            else:
                agg = post
            return await self._apply_handler_async(agg)
        raise TypeError("execution mode not supported.")