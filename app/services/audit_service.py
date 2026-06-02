import asyncio
import json
import logging
from pathlib import Path

from app.schemas.audit import AuditEvent

logger = logging.getLogger(__name__)


class AuditService:
    def __init__(self, audit_log_path: Path) -> None:
        self.audit_log_path = audit_log_path
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()

    async def record(self, event: AuditEvent) -> None:
        payload = event.model_dump(mode="json")
        logger.info(json.dumps({"audit": payload}, ensure_ascii=False))
        line = json.dumps(payload, ensure_ascii=False)
        async with self._lock:
            await asyncio.to_thread(self._append_line, line)

    def _append_line(self, line: str) -> None:
        with self.audit_log_path.open("a", encoding="utf-8") as file:
            file.write(line + "\n")

