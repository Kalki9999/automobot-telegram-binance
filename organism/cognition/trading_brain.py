from dataclasses import dataclass


@dataclass(frozen=True)
class TradingDecision:
    action: str
    confidence: float
    score: float
    reason: str


class TradingBrain:
    """Deterministic trading cognition used by the Freqtrade strategy."""

    def decide(
        self,
        *,
        close: float,
        ema20: float,
        ema50: float,
        ema200: float,
        rsi: float,
        adx: float,
        atr_pct: float,
        volume: float,
        volume_mean: float,
        in_position: bool = False,
    ) -> TradingDecision:

        score = 0.0
        reasons = []

        if close > ema200:
            score += 0.20
            reasons.append("above EMA200")

        if ema20 > ema50:
            score += 0.20
            reasons.append("EMA20 above EMA50")

        if 52 < rsi < 68:
            score += 0.15
            reasons.append("RSI momentum")

        if adx > 20:
            score += 0.15
            reasons.append("ADX trend")

        if volume > volume_mean > 0:
            score += 0.15
            reasons.append("volume confirmation")

        if atr_pct > 0.001:
            score += 0.15
            reasons.append("sufficient volatility")

        score = round(min(1.0, score), 4)

        if not in_position and score >= 0.70:
            return TradingDecision(
                action="BUY",
                confidence=score,
                score=score,
                reason=", ".join(reasons),
            )

        bearish = 0

        if ema20 < ema50:
            bearish += 1

        if rsi < 42:
            bearish += 1

        if in_position and bearish >= 2:
            return TradingDecision(
                action="SELL",
                confidence=round(
                    min(1.0, 0.50 + bearish * 0.20),
                    4,
                ),
                score=score,
                reason="trend and momentum deterioration",
            )

        return TradingDecision(
            action="WAIT",
            confidence=score,
            score=score,
            reason="conditions insufficient",
        )
