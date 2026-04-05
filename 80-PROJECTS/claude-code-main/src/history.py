from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class HistoryEvent:
    title: str
    detail: str


@dataclass
class HistoryLog:
    events: list[HistoryEvent] = field(default_factory=list)

    def add(self, title: str, detail: str) -> None:
        self.events.append(HistoryEvent(title=title, detail=detail))
