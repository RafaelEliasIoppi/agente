from __future__ import annotations
import logging
from typing import Any
from .client import GraphClient

logger = logging.getLogger(__name__)


class WorkbookReader:
    def __init__(
        self,
        client: GraphClient,
        drive_id: str,
        item_id: str,
        table_name: str = "",
        key_column: str = "",
    ) -> None:
        self._client = client
        self._drive_id = drive_id
        self._item_id = item_id
        self._table_name = table_name
        self._key_column = key_column
        self._base = f"/drives/{drive_id}/items/{item_id}/workbook"

    async def list_tables(self) -> list[str]:
        data = await self._client.get(f"{self._base}/tables")
        return [t["name"] for t in data.get("value", [])]

    async def _resolve_table(self) -> str:
        if self._table_name:
            return self._table_name
        tables = await self.list_tables()
        if not tables:
            raise RuntimeError("No tables found in workbook")
        logger.info(f"Auto-detected table: {tables[0]}")
        return tables[0]

    async def get_rows(self) -> list[dict[str, Any]]:
        table = await self._resolve_table()
        data = await self._client.get(
            f"{self._base}/tables/{table}/rows",
            params={"$select": "values,index"},
        )
        header_data = await self._client.get(
            f"{self._base}/tables/{table}/headerRowRange",
            params={"$select": "values"},
        )
        headers: list[str] = header_data["values"][0]
        rows = []
        for row in data.get("value", []):
            values = row["values"][0]
            record = dict(zip(headers, values))
            rows.append(record)
        logger.debug(f"Fetched {len(rows)} rows from table '{table}'")
        return rows

    def detect_key_column(self, rows: list[dict[str, Any]]) -> str:
        if self._key_column:
            return self._key_column
        if not rows:
            return "__row_index__"
        for col in rows[0].keys():
            values = [r.get(col) for r in rows]
            if len(set(str(v) for v in values)) == len(values) and all(v for v in values):
                logger.info(f"Auto-detected key column: '{col}'")
                return col
        return "__row_index__"
