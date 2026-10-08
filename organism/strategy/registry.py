from dataclasses import dataclass, field
from typing import Dict


@dataclass
class StrategyRecord:
    name: str
    trades: int = 0
    wins: int = 0
    losses: int = 0
    net_profit: float = 0.0
    active: bool = True
    confidence: float = 0.0
    notes: list[str] = field(default_factory=list)

    @property
    def win_rate(self) -> float:
        if self.trades == 0:
            return 0.0

        return self.wins / self.trades

    @property
    def expectancy(self) -> float:
        if self.trades == 0:
            return 0.0

        return self.net_profit / self.trades


class StrategyRegistry:
    """
    Persistent conceptual registry of strategy performance.

    A strategy earns trust through evidence.
    It does not become trusted because an LLM says it is good.
    """

    def __init__(self) -> None:
        self.strategies: Dict[str, StrategyRecord] = {}

    def register(self, name: str) -> StrategyRecord:
        if name not in self.strategies:
            self.strategies[name] = StrategyRecord(name=name)

        return self.strategies[name]

    def record_result(
        self,
        name: str,
        *,
        profit: float,
    ) -> StrategyRecord:

        strategy = self.register(name)

        strategy.trades += 1
        strategy.net_profit += profit

        if profit > 0:
            strategy.wins += 1
        elif profit < 0:
            strategy.losses += 1

        strategy.confidence = self._calculate_confidence(strategy)

        return strategy

    def _calculate_confidence(
        self,
        strategy: StrategyRecord,
    ) -> float:

        if strategy.trades == 0:
            return 0.0

        # Evidence grows with sample size.
        sample_factor = min(
            1.0,
            strategy.trades / 50.0,
        )

        # Positive expectancy contributes to trust.
        expectancy_factor = max(
            0.0,
            min(
                1.0,
                0.5 + strategy.expectancy,
            ),
        )

        return round(
            sample_factor * expectancy_factor,
            4,
        )

    def should_retire(
        self,
        name: str,
        *,
        minimum_trades: int = 30,
        minimum_confidence: float = 0.20,
    ) -> bool:

        strategy = self.strategies[name]

        if strategy.trades < minimum_trades:
            return False

        return strategy.confidence < minimum_confidence

    def retire(self, name: str, reason: str) -> None:
        strategy = self.strategies[name]
        strategy.active = False
        strategy.notes.append(reason)

    def active_strategies(self) -> list[StrategyRecord]:
        return [
            strategy
            for strategy in self.strategies.values()
            if strategy.active
        ]
