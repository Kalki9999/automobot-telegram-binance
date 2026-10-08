from dataclasses import dataclass


@dataclass(frozen=True)
class FearState:
    level: float
    uncertainty: float
    drawdown: float
    recent_failure_rate: float

    @property
    def mode(self) -> str:
        if self.level >= 0.80:
            return "SURVIVAL"
        if self.level >= 0.60:
            return "DEFENSIVE"
        if self.level >= 0.40:
            return "CAUTIOUS"
        return "NORMAL"


def evaluate_fear(
    *,
    uncertainty: float,
    drawdown: float,
    recent_failure_rate: float,
) -> FearState:

    values = (
        max(0.0, min(1.0, uncertainty)),
        max(0.0, min(1.0, drawdown)),
        max(0.0, min(1.0, recent_failure_rate)),
    )

    level = (
        values[0] * 0.35
        + values[1] * 0.40
        + values[2] * 0.25
    )

    return FearState(
        level=round(level, 4),
        uncertainty=values[0],
        drawdown=values[1],
        recent_failure_rate=values[2],
    )
