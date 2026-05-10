from queue import Queue
import dataclasses


@dataclasses.dataclass
class ActiveQueueItem:
    number: float
    list: float
    completion: float
    complete: bool = False


class ActiveQueue(Queue):
    def __init__(self) -> None:
        super().__init__()

    def update_last_complete(self, completion: float) -> None:
        if self.empty():
            return
        last_item = self.queue[-1]
        last_item.completion = completion

    def completion(self, completion: float) -> None | Exception:
        if self.empty():
            raise RuntimeError("No active cues in the queue.")
        last_item = self.queue[-1]
        self.put(
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
        return self.queue[-1]

    @property
    def complete(self) -> bool:
        current = self.current
        if current is None:
            return False
        return current.complete
