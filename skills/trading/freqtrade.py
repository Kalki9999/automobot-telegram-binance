from typing import Any, Dict

from skills.trading.adapter import ExecutionResult, TradingAdapter


class FreqtradeAdapter(TradingAdapter):
    """
    Freqtrade integration boundary.

    Phase 1:
    - No direct live execution.
    - No credentials handled here.
    - Organism actions are translated and audited.
    """

    def __init__(self, dry_run: bool = True) -> None:
        self.dry_run = dry_run

    def execute(
        self,
        operation: str,
        parameters: Dict[str, Any],
    ) -> ExecutionResult:

        if not self.dry_run:
            return ExecutionResult(
                success=False,
                status="BLOCKED",
                message="Live trading adapter is not enabled.",
                data={},
            )

        return ExecutionResult(
            success=True,
            status="DRY_RUN",
            message="Trading action accepted by the adapter in dry-run mode.",
            data={
                "operation": operation,
                "parameters": parameters,
            },
        )
