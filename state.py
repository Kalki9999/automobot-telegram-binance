import json
import os
import threading
from dataclasses import dataclass, asdict


@dataclass
class RuntimeState:
    running: bool = True
    paused: bool = False


class StateStore:
    def __init__(self, path: str = "runtime/state.json") -> None:
        self.path = path
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.state = self._load()

    def _load(self) -> RuntimeState:
        if not os.path.exists(self.path):
            return RuntimeState()
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            return RuntimeState(
                running=bool(data.get("running", True)),
                paused=bool(data.get("paused", False)),
            )
        except (OSError, ValueError, TypeError):
            return RuntimeState()

    def save(self) -> None:
        with self._lock:
            tmp = f"{self.path}.tmp"
            with open(tmp, "w", encoding="utf-8") as handle:
                json.dump(asdict(self.state), handle, indent=2)
            os.replace(tmp, self.path)

    def set_running(self, value: bool) -> None:
        self.state.running = value
        self.save()

    def set_paused(self, value: bool) -> None:
        self.state.paused = value
        self.save()