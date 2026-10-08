from dataclasses import dataclass

from organism.cognition.action import ActionContract
from organism.fear.evaluator import FearState


@dataclass(frozen=True)
class PermissionResult:
    allowed: bool
    reason: str


class PermissionGate:
    """
    Final authority before an external action.

    Cognition can propose.
    The permission gate decides whether execution is allowed.
    """

    def __init__(
        self,
        *,
        trading_enabled: bool = False,
        allow_withdrawals: bool = False,
        allow_futures: bool = False,
        max_fear_for_trading: float = 0.60,
    ):
        self.trading_enabled = trading_enabled
        self.allow_withdrawals = allow_withdrawals
        self.allow_futures = allow_futures
        self.max_fear_for_trading = max_fear_for_trading

    def evaluate(
        self,
        action: ActionContract,
        fear: FearState,
    ) -> PermissionResult:

        action.validate()

        if action.skill == "trading":

            if not self.trading_enabled:
                return PermissionResult(
                    False,
                    "Live trading is disabled."
                )

            if fear.level >= self.max_fear_for_trading:
                return PermissionResult(
                    False,
                    f"Fear level {fear.level:.2f} exceeds trading threshold."
                )

        if action.operation == "withdraw":
            if not self.allow_withdrawals:
                return PermissionResult(
                    False,
                    "Withdrawals are permanently disabled."
                )

        if action.operation in {"futures", "leverage"}:
            if not self.allow_futures:
                return PermissionResult(
                    False,
                    "Futures/leverage are disabled."
                )

        return PermissionResult(True, "Action permitted.")
