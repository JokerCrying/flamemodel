import inspect
from enum import Enum
from typing import Any, Callable, List, Optional, TYPE_CHECKING, Union, Literal

if TYPE_CHECKING:
    from ..adaptor.interface import RedisAdaptor

class ExecutionMode(Enum):
    """
    Enumeration for different execution modes of an Action.
    
    Attributes:
        SINGLE: Represents a single action execution.
        SEQUENCE: Represents a sequence of actions executed in order.
        TRANSACTION: Represents a set of actions executed within a transaction (e.g., Redis pipeline).
    """
    SINGLE = 'single'
    SEQUENCE = 'sequence'
    TRANSACTION = 'transaction'


ExecutionModeType = Union[Literal['single', 'sequence', 'transaction'], ExecutionMode]

class Action:
    """
    Represents an action or a unit of work that can be executed synchronously or asynchronously.
    
    This class encapsulates the logic for executing commands, functions, or sequences of actions,
    handling results, and managing execution context (like clients or adaptors).
    """
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
        """
        Initialize an Action instance.

        Args:
            runtime_mode (str): The runtime mode ('sync' or 'async').
            executor (Optional[Callable]): A callable to be executed.
            command (Optional[str]): The name of the command to execute on the client.
            args (Optional[tuple]): Positional arguments for the executor or command.
            kwargs (Optional[dict]): Keyword arguments for the executor or command.
            handler (Optional[Callable[[Any], Any]]): A callback function to process the result.
            sub_actions (Optional[List['Action']]): A list of sub-actions for SEQUENCE or TRANSACTION modes.
            execution_mode (ExecutionModeType): The mode of execution (SINGLE, SEQUENCE, or TRANSACTION).
            result_from_index (Optional[int]): The index of the result to return when executing multiple actions. 
                                              Defaults to -1 (the last result).
            client (Any): The client instance (e.g., Redis client) to execute commands on.
            adaptor (RedisAdaptor): The adaptor instance providing the client.
        """
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
        """
        Create a new Action instance with the specified client.

        Args:
            client: The new client instance to use.

        Returns:
            Action: A new Action instance with the updated client.
        """
        new = self.clone()
        new.client = client
        return new

    def with_adaptor(self, adaptor: 'RedisAdaptor') -> 'Action':
        """
        Create a new Action instance with the specified adaptor.

        Args:
            adaptor (RedisAdaptor): The new adaptor instance to use.

        Returns:
            Action: A new Action instance with the updated adaptor and client from the adaptor.
        """
        new = self.clone()
        new._adaptor = adaptor
        new.client = adaptor.proxy
        return new

    def execute(self):
        """
        Execute the action based on the configured runtime mode.

        Returns:
            Any: The result of the execution (awaitable if async, value if sync).
        """
        if self.runtime_mode == 'sync':
            return self._execute_sync()
        return self._execute_async()

    def run_sync(self) -> Any:
        """
        Execute the action synchronously.

        Returns:
            Any: The result of the synchronous execution.

        Raises:
            RuntimeError: If called in 'async' runtime mode.
        """
        if self.runtime_mode != 'sync':
            raise RuntimeError(
                "Cannot .run_sync() an Action in 'async' runtime mode. Use 'await' instead."
            )
        return self._execute_sync()

    def then(self, handler: Callable[[Any], Any]) -> 'Action':
        """
        Chain a handler to process the result of this action.

        Args:
            handler (Callable[[Any], Any]): The function to apply to the result.

        Returns:
            Action: A new Action instance with the chained handler.
        """
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
        """
        Create an Action that executes a list of actions sequentially.

        Args:
            actions (List[Action]): The list of actions to execute.
            runtime_mode: The runtime mode ('sync' or 'async').
            result_from_index (int): The index of the result to return. Defaults to -1.
            client (Any): Optional client to use for the sequence.

        Returns:
            Action: An Action configured for sequence execution.
        """
        return cls(
            runtime_mode=runtime_mode,
            sub_actions=actions,
            execution_mode=ExecutionMode.SEQUENCE,
            result_from_index=result_from_index,
            client=client
        )

    @classmethod
    def transaction(cls, actions: List['Action'], runtime_mode, client: Any, result_from_index: int = -1) -> 'Action':
        """
        Create an Action that executes a list of actions as a transaction.

        Args:
            actions (List[Action]): The list of actions to execute.
            runtime_mode: The runtime mode ('sync' or 'async').
            client (Any): The client to execute the transaction on (must support pipelines).
            result_from_index (int): The index of the result to return. Defaults to -1.

        Returns:
            Action: An Action configured for transaction execution.
        """
        return cls(
            runtime_mode=runtime_mode,
            sub_actions=actions,
            execution_mode=ExecutionMode.TRANSACTION,
            client=client,
            result_from_index=result_from_index
        )

    def clone(self) -> 'Action':
        """
        Create a copy of this Action.

        Returns:
            Action: A new Action instance with the same configuration.
        """
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
        """
        Apply the result handler asynchronously.

        Args:
            value (Any): The result to process.

        Returns:
            Any: The processed result.
        """
        if not self._handler:
            return value
        out = self._handler(value)
        if isinstance(out, Action):
            return await out._execute_async()
        if inspect.isawaitable(out):
            return await out
        return out

    def _apply_handler_sync(self, value: Any) -> Any:
        """
        Apply the result handler synchronously.

        Args:
            value (Any): The result to process.

        Returns:
            Any: The processed result.

        Raises:
            RuntimeError: If the handler returns an awaitable in sync mode.
        """
        if not self._handler:
            return value
        out = self._handler(value)
        if isinstance(out, Action):
            return out._execute_sync()
        if inspect.isawaitable(out):
            raise RuntimeError("Handler returned awaitable in sync runtime mode")
        return out

    def _execute_sync(self) -> Any:
        """
        Internal method to execute the action synchronously.

        Returns:
            Any: The result of the execution.
        """
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
        """
        Internal method to execute the action asynchronously.

        Returns:
            Any: The result of the execution.
        """
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
