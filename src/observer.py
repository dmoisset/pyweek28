from typing import Any, Container, Dict, Iterable, Set, Tuple
from typing_extensions import Protocol

Message = Dict[Any, Any]


class EventList:
    events: Dict[int, Tuple["Observable", Message]]

    def __init__(self) -> None:
        self.events = {}

    def new_event(self, object: "Observable", message: Message) -> None:
        oid = id(object)
        _, merged_message = self.events.get(oid, (None, {}))
        merged_message.update(message)
        self.events[oid] = (object, merged_message)

    def dispatch(self) -> None:
        # Make a copy to avoid re-entrance, just in case some handler
        # calls dispatch (it shouldn't!)
        evs = self.events.copy()
        self.events = {}
        for obj, msg in evs.values():
            for target in obj.observers:
                target.notify(obj, msg)


_events = EventList()


def dispatch_events() -> None:
    _events.dispatch()


class Observer(Protocol):
    def notify(self, obj: "Observable", msg: Message) -> None:
        ...


class Observable:
    observers: Set[Observer]

    OBSERVABLE_FIELDS: Container[str] = ()
    OBSERVABLE_PROPERTIES: Dict[str, Iterable[str]] = {}

    def __init__(self) -> None:
        self.observers = set()

    def register(self, observer: Observer) -> None:
        self.observers.add(observer)

    def unregister(self, observer: Observer) -> None:
        self.observers.remove(observer)

    def request_notify(self, msg: Message) -> None:
        if not self.observers:
            # This check is not required, but avoids storing a message that will not be used
            return
        _events.new_event(self, msg)

    def __setattr__(self, name: str, value: Any) -> None:
        if name not in self.OBSERVABLE_FIELDS:
            # This attribute is not interesting, do the usual
            super().__setattr__(name, value)
            return

        message = {name: {"new": value}}
        if hasattr(self, name):
            message[name]["old"] = getattr(self, name)
        super().__setattr__(name, value)
        self.request_notify(message)
        for p in self.OBSERVABLE_PROPERTIES.get(name, ()):
            self.request_notify({p: "changed"})


__all__ = ["dispatch_events", "Observable", "Observer"]
