from asyncio import Queue
from dataclasses import dataclass


@dataclass
class ActiveQueueItem:
    number: float
    list: float
    completion: float
    complete: bool = False

    def json(self):
        return {
            "number": self.number,
            "list": self.list,
            "completion": self.completion,
            "complete": self.complete,
        }


class ActiveQueue(Queue):
    def __init__(self) -> None:
        super().__init__()

    def update_last_complete(self, completion: float) -> None:
        if self.empty():
            return
        last_item = self.get_nowait()
        last_item.completion = completion

    async def completion(self, completion: float) -> None | Exception:
        if self.empty():
            raise RuntimeError("No active cues in the queue.")
        last_item = self.get_nowait()
        await self.put(
            ActiveQueueItem(
                number=last_item.number,
                list=last_item.list,
                completion=completion,
                complete=completion >= 100,
            )
        )

    @property
    def current(self) -> ActiveQueueItem | None:
        if self.empty():
            return None
        return self.get_nowait()

    @property
    def complete(self) -> bool:
        current = self.current
        if current is None:
            return False
        return current.complete
