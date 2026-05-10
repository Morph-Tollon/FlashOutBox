from queue import Queue
import dataclasses


@dataclasses.dataclass
class ActiveQueueItem:
    number: float
    list: float
    completion: float


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
                number=last_item.number, list=last_item.list, completion=completion
            )
        )

    @property
    def current(self) -> ActiveQueueItem | None:
        if self.empty():
            return None
        return self.queue[-1]
