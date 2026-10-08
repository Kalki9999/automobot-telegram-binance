import json
import os
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List


class MemoryStore:
    """
    Small persistent event memory.

    This is intentionally simple initially.
    It can later be replaced with SQLite/vector memory.
    """

    def __init__(self, path: str = "runtime/organism_memory.json") -> None:
        self.path = path
        self._lock = threading.Lock()

        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        self.events: List[Dict[str, Any]] = self._load()

    def _load(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.path):
            return []

        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                data = json.load(handle)

            return data if isinstance(data, list) else []
        except (OSError, ValueError, TypeError):
            return []

    def remember(
        self,
        event_type: str,
        data: Dict[str, Any],
    ) -> None:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            "data": data,
        }

        with self._lock:
            self.events.append(event)

            # Keep initial memory bounded.
            self.events = self.events[-1000:]

            temporary = f"{self.path}.tmp"

            with open(temporary, "w", encoding="utf-8") as handle:
                json.dump(self.events, handle, indent=2)

            os.replace(temporary, self.path)

    def recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self.events[-limit:]
