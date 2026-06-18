from __future__ import annotations
from contextlib import asynccontextmanager
import asyncio
import logging
from fastapi import FastAPI
from ..config.settings import settings
from ..logs.logging_config import setup_logging
from ..graph.client import GraphClient
from ..graph.workbook import WorkbookReader
from ..repositories.snapshot_repo import SnapshotRepository
from ..repositories.history_repo import HistoryRepository
from ..services.monitor import MonitorService
from ..notifications.console import ConsoleNotifier
from ..notifications.email import EmailNotifier
from ..scheduler.scheduler import MonitorScheduler
from ..agents.excel_agent import ExcelAgent
from ..agents.tools import init_tools
from .routes import status as status_route
from .routes import dados as dados_route
from .routes import alteracoes as alteracoes_route
from .routes import registros as registros_route
from .routes import perguntar as perguntar_route

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(log_dir=settings.logs_dir)
    settings.snapshots_dir.mkdir(parents=True, exist_ok=True)
    settings.history_dir.mkdir(parents=True, exist_ok=True)

    graph_client = GraphClient(
        client_id=settings.azure_client_id,
        tenant_id=settings.azure_tenant_id,
        username=settings.ms_username,
        password=settings.ms_password,
    )
    workbook_reader = WorkbookReader(
        client=graph_client,
        drive_id=settings.sharepoint_drive_id,
        item_id=settings.workbook_item_id,
        table_name=settings.workbook_table_name,
        key_column=settings.workbook_key_column,
    )
    snapshot_repo = SnapshotRepository(settings.snapshots_dir)
    history_repo = HistoryRepository(settings.history_dir)

    notifiers = [ConsoleNotifier()]
    if settings.smtp_enabled:
        notifiers.append(EmailNotifier(
            host=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            sender=settings.smtp_from,
            recipients=settings.smtp_recipients,
        ))

    monitor = MonitorService(
        workbook_reader=workbook_reader,
        snapshot_repo=snapshot_repo,
        history_repo=history_repo,
        notifiers=notifiers,
        key_column=settings.workbook_key_column,
    )

    init_tools(snapshot_repo, history_repo)
    agent = ExcelAgent(model=settings.claude_model)

    status_route.init_router(monitor)
    dados_route.init_router(snapshot_repo)
    alteracoes_route.init_router(history_repo)
    registros_route.init_router(snapshot_repo)
    perguntar_route.init_router(agent)

    scheduler = MonitorScheduler(interval_seconds=settings.monitor_interval_seconds)
    scheduler.add_job(monitor.run_cycle)
    scheduler.start()

    await monitor.run_cycle()

    yield

    scheduler.shutdown()


app = FastAPI(
    title="Excel Agent API",
    description="Monitoramento e consulta de planilha Excel Online via Microsoft Graph API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(status_route.router)
app.include_router(dados_route.router)
app.include_router(alteracoes_route.router)
app.include_router(registros_route.router)
app.include_router(perguntar_route.router)
