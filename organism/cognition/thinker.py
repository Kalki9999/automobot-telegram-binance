from organism.cognition.action import ActionContract
from organism.fear.evaluator import FearState
from organism.world.model import WorldState


class Thinker:
    """
    Converts world state into a proposed action.

    The thinker has NO execution authority.
    It can only produce an ActionContract.
    """

    def think(
        self,
        world: WorldState,
        fear: FearState,
    ) -> ActionContract | None:

        # High fear means observe rather than act.
        if fear.level >= 0.60:
            return None

        # Insufficient confidence means remain observational.
        if world.confidence < 0.50:
            return None

        # No market opportunity currently known.
        if not world.market.get("signal"):
            return None

        signal = world.market["signal"]

        if signal == "buy":
            return ActionContract(
                action_id="trade-buy",
                skill="trading",
                operation="buy",
                reason="Market model produced a buy signal.",
                confidence=world.confidence,
                parameters={
                    "symbol": world.market.get("symbol", "BTC/USDT"),
                },
            )

        if signal == "sell":
            return ActionContract(
                action_id="trade-sell",
                skill="trading",
                operation="sell",
                reason="Market model produced a sell signal.",
                confidence=world.confidence,
                parameters={
                    "symbol": world.market.get("symbol", "BTC/USDT"),
                },
            )

        return None
