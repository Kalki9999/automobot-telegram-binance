from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass
class WorldState:
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    capital: float = 0.0
    available_capital: float = 0.0
    drawdown: float = 0.0

    market: Dict[str, Any] = field(default_factory=dict)
    system: Dict[str, Any] = field(default_factory=dict)

    fear: float = 0.0
    uncertainty: float = 0.0
    confidence: float = 0.0

    organism_state: str = "INITIALIZING"

    def update(self, **values: Any) -> None:
        for key, value in values.items():
            if hasattr(self, key):
                setattr(self, key, value)
