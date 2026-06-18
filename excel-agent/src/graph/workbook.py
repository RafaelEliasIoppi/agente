from __future__ import annotations
import logging
from typing import Any
from .client import GraphClient

logger = logging.getLogger(__name__)


class WorkbookReader:
    def __init__(
        self,
        client: GraphClient,
        drive_id: str = "",
        item_id: str = "",
        workbook_name: str = "",
        table_name: str = "",
        key_column: str = "",
    ) -> None:
        self._client = client
        self._drive_id = drive_id
        self._item_id = item_id
        self._workbook_name = workbook_name
        self._table_name = table_name
        self._key_column = key_column
        self._base: str | None = None

    async def _resolve_drive_id(self) -> str:
        if self._drive_id:
            return self._drive_id
        drive = await self._client.get("/me/drive")
        self._drive_id = drive["id"]
        logger.info(f"Drive descoberto automaticamente: {self._drive_id}")
        return self._drive_id

    async def _resolve_item_id(self, drive_id: str) -> str:
        if self._item_id:
            return self._item_id
        if not self._workbook_name:
            raise RuntimeError("Informe WORKBOOK_ITEM_ID ou WORKBOOK_NAME no .env")
        # Busca o arquivo pelo nome no drive do usuário
        result = await self._client.get(
            f"/drives/{drive_id}/root/search(q='{self._workbook_name}')"
        )
        items = result.get("value", [])
        matches = [i for i in items if i.get("name", "").lower() == self._workbook_name.lower()]
        target = matches[0] if matches else (items[0] if items else None)
        if not target:
            raise RuntimeError(f"Planilha '{self._workbook_name}' não encontrada no OneDrive/SharePoint")
        self._item_id = target["id"]
        logger.info(f"Planilha encontrada: '{target['name']}' (id={self._item_id})")
        return self._item_id

    async def _get_base(self) -> str:
        if self._base is None:
            drive_id = await self._resolve_drive_id()
            item_id = await self._resolve_item_id(drive_id)
            self._base = f"/drives/{drive_id}/items/{item_id}/workbook"
        return self._base

    async def list_tables(self) -> list[str]:
        base = await self._get_base()
        data = await self._client.get(f"{base}/tables")
        return [t["name"] for t in data.get("value", [])]

    async def _read_from_table(self, base: str, table: str) -> list[dict[str, Any]]:
        data = await self._client.get(
            f"{base}/tables/{table}/rows", params={"$select": "values,index"}
        )
        header_data = await self._client.get(
            f"{base}/tables/{table}/headerRowRange", params={"$select": "values"}
        )
        headers: list[str] = header_data["values"][0]
        rows = []
        for row in data.get("value", []):
            values = row["values"][0]
            rows.append(dict(zip(headers, values)))
        logger.info(f"Lidos {len(rows)} registros da tabela '{table}'")
        return rows

    async def _read_from_worksheet(self, base: str) -> list[dict[str, Any]]:
        """Fallback: lê o range usado da primeira aba quando não há tabela formal."""
        sheets = await self._client.get(f"{base}/worksheets")
        sheet_list = sheets.get("value", [])
        if not sheet_list:
            return []
        sheet_name = sheet_list[0]["name"]
        used = await self._client.get(
            f"{base}/worksheets/{sheet_name}/usedRange", params={"$select": "values"}
        )
        values = used.get("values", [])
        if len(values) < 2:
            return []
        headers = [str(h) if h is not None else f"col_{i}" for i, h in enumerate(values[0])]
        rows = []
        for row_values in values[1:]:
            if all(v in (None, "") for v in row_values):
                continue
            rows.append({headers[i]: row_values[i] for i in range(min(len(headers), len(row_values)))})
        logger.info(f"Lidos {len(rows)} registros da aba '{sheet_name}' (usedRange)")
        return rows

    async def get_rows(self) -> list[dict[str, Any]]:
        base = await self._get_base()
        tables = await self.list_tables()
        if self._table_name:
            return await self._read_from_table(base, self._table_name)
        if tables:
            logger.info(f"Tabela detectada: '{tables[0]}'")
            return await self._read_from_table(base, tables[0])
        logger.info("Nenhuma tabela formal — lendo aba diretamente")
        return await self._read_from_worksheet(base)

    def detect_key_column(self, rows: list[dict[str, Any]]) -> str:
        if self._key_column:
            return self._key_column
        if not rows:
            return "__row_index__"
        for col in rows[0].keys():
            values = [r.get(col) for r in rows]
            if len(set(str(v) for v in values)) == len(values) and all(v for v in values):
                logger.info(f"Coluna-chave detectada automaticamente: '{col}'")
                return col
        return "__row_index__"
