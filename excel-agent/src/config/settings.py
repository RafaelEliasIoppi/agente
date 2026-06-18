from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Modo demo — roda sem nenhuma chave externa
    demo_mode: bool = Field(default=False, description="Roda com dados locais, sem Azure nem Anthropic")
    demo_data_path: Path = Field(default=Path("./demo_data/urgencia_renal.json"))

    # Azure / Microsoft Graph (opcionais em demo_mode)
    azure_client_id: str = Field(default="", description="Azure App Registration Client ID")
    azure_tenant_id: str = Field(default="", description="Azure Tenant ID")
    sharepoint_drive_id: str = Field(default="", description="SharePoint Drive ID (vazio = auto)")
    workbook_item_id: str = Field(default="", description="Workbook item ID (vazio = busca por nome)")
    workbook_name: str = Field(default="", description="Nome do arquivo para busca automática")
    workbook_table_name: str = Field(default="", description="Table name (empty = auto-detect first)")
    workbook_key_column: str = Field(default="", description="Key column name (empty = auto-detect)")

    # Anthropic / Claude (opcional em demo_mode)
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    claude_model: str = Field(default="claude-sonnet-4-6", description="Claude model ID")

    # SMTP Email
    smtp_enabled: bool = Field(default=False)
    smtp_host: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587)
    smtp_user: str = Field(default="")
    smtp_password: str = Field(default="")
    smtp_from: str = Field(default="")
    smtp_to: str = Field(default="", description="Comma-separated recipient list")

    # Monitoring
    monitor_interval_seconds: int = Field(default=300)

    # Storage
    data_dir: Path = Field(default=Path("./data"))
    token_cache_path: Path = Field(default=Path("./data/token_cache.json"))

    @property
    def snapshots_dir(self) -> Path:
        return self.data_dir / "snapshots"

    @property
    def history_dir(self) -> Path:
        return self.data_dir / "history"

    @property
    def logs_dir(self) -> Path:
        return self.data_dir / "logs"

    @property
    def smtp_recipients(self) -> list[str]:
        return [e.strip() for e in self.smtp_to.split(",") if e.strip()]


settings = Settings()
