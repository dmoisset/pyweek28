from dataclasses import dataclass
from typing import Callable, Sequence


@dataclass
class MenuItem:
    key: str
    label: str
    action: Callable[[], None]
    color: str = "#FFFFFF"
    subtitle: str = ""


@dataclass
class Menu:
    title: str
    subtitle: str
    entries: Sequence[MenuItem] = ()
    cancel: Callable[[], None] = lambda: None


def run(m: Menu) -> None:
    print(m.title)
    print(m.subtitle)
    print()
    for e in m.entries:
        print(f" [{e.key}] {e.label} ({e.subtitle})")
    while True:
        choice = input(">")
        if choice == "":
            m.cancel()  # type: ignore
            return
        for e in m.entries:
            if e.key == choice:
                e.action()  # type: ignore
                return
        print(f"No action for {choice!r}")
