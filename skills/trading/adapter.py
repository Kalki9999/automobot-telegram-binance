from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class ExecutionResult:
    success: bool
    status: str
    message: str
    data: Dict[str, Any]


class TradingAdapter:
    """
    Boundary between the organism and the trading engine.

    The organism does not know Freqtrade internals.
    The adapter translates organism actions into trading operations.
    """

    def execute(
        self,
        operation: str,
        parameters: Dict[str, Any],
    ) -> ExecutionResult:
        raise NotImplementedError
