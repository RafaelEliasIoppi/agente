from __future__ import annotations
from abc import ABC, abstractmethod
from ..models.record import ChangeEvent


class NotifierBase(ABC):
    @abstractmethod
    async def notify(self, event: ChangeEvent) -> None:
        ...
