from typing import TypeVar, TYPE_CHECKING, Type, List
from .query import Query
from ..utils.action import Action
from ..models import BaseRedisModel

_T = TypeVar("_T", bound=BaseRedisModel)

if TYPE_CHECKING:
    from ..main import FlameModel


class Session:
    def __init__(
            self,
            app: 'FlameModel'
    ):
        self.app = app
        self._pending_task = []
        self._in_transaction = False

    def query(self, model_cls: Type[_T]) -> Query[Type[_T]]:
        return Query(
            app=self.app,
            model_cls=model_cls
        )  # type: ignore

    def add(self, model: _T):
        self._pending_task.append(model.save())

    def add_all(self, models: List[_T]):
        for model in models:
            self.add(model)

    def delete(self, model: _T):
        act = model.delete()
        if not self._in_transaction:
            return act
        self._pending_task.append(act)
        return None

    def commit(self):
        if not self._pending_task:
            return None
        if len(self._pending_task) == 1:
            action = self._pending_task[0]
        else:
            action = Action.transaction(
                self._pending_task,
                runtime_mode=self.app.runtime_mode,
                client=self.app.adaptor.proxy,
                result_from_index=None
            )
        return action.then(self.__on_commit_after).execute()

    def expire(self, model: _T, ttl: int = -1):
        act = model.expire(ttl)
        if not self._in_transaction:
            return act
        self._pending_task.append(act)
        return None

    @classmethod
    def ttl(cls, model: _T):
        return model.ttl()

    def begin(self):
        self._pending_task.clear()
        self._in_transaction = True
        return self

    def rollback(self):
        self._in_transaction = False
        self._pending_task.clear()

    def __on_commit_after(self, results):
        self.rollback()
        return results
