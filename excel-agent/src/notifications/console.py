from __future__ import annotations
import logging
from .base import NotifierBase
from ..models.record import ChangeEvent

logger = logging.getLogger(__name__)


class ConsoleNotifier(NotifierBase):
    async def notify(self, event: ChangeEvent) -> None:
        logger.info(
            "CHANGE_EVENT",
            extra={
                "event": event.model_dump(mode="json"),
            },
        )
        print(f"[{event.tipo}] id={event.linha_id} campo={event.campo} "
              f"old={event.valor_antigo!r} new={event.valor_novo!r}")
