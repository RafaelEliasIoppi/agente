from __future__ import annotations
import logging
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .base import NotifierBase
from ..models.record import ChangeEvent

logger = logging.getLogger(__name__)


class EmailNotifier(NotifierBase):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        sender: str,
        recipients: list[str],
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._sender = sender
        self._recipients = recipients

    def _build_html(self, event: ChangeEvent) -> str:
        return f"""
        <html><body>
        <h2>Evento de Monitoramento: {event.tipo}</h2>
        <table border="1" cellpadding="6" cellspacing="0">
          <tr><td><b>Tipo</b></td><td>{event.tipo}</td></tr>
          <tr><td><b>ID da Linha</b></td><td>{event.linha_id}</td></tr>
          <tr><td><b>Campo</b></td><td>{event.campo or "-"}</td></tr>
          <tr><td><b>Valor Anterior</b></td><td>{event.valor_antigo}</td></tr>
          <tr><td><b>Novo Valor</b></td><td>{event.valor_novo}</td></tr>
          <tr><td><b>Timestamp</b></td><td>{event.timestamp.isoformat()}</td></tr>
        </table>
        </body></html>
        """

    async def notify(self, event: ChangeEvent) -> None:
        if not self._recipients:
            return
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[Excel Agent] {event.tipo} — ID {event.linha_id}"
        msg["From"] = self._sender
        msg["To"] = ", ".join(self._recipients)
        msg.attach(MIMEText(self._build_html(event), "html", "utf-8"))
        try:
            await aiosmtplib.send(
                msg,
                hostname=self._host,
                port=self._port,
                username=self._username,
                password=self._password,
                start_tls=True,
            )
            logger.info(f"Email sent for event {event.tipo} id={event.linha_id}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
