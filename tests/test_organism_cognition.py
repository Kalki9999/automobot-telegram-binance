from organism.cognition.thinker import Thinker
from organism.fear.evaluator import FearState
from organism.world.model import WorldState


def test_thinker_proposes_buy():
    world = WorldState(
        confidence=0.80,
        market={
            "signal": "buy",
            "symbol": "BTC/USDT",
        },
    )

    fear = FearState(
        level=0.20,
        uncertainty=0.10,
        drawdown=0.05,
        recent_failure_rate=0.10,
    )

    action = Thinker().think(world, fear)

    assert action is not None
    assert action.skill == "trading"
    assert action.operation == "buy"
    assert action.parameters["symbol"] == "BTC/USDT"


def test_high_fear_prevents_action():
    world = WorldState(
        confidence=0.90,
        market={
            "signal": "buy",
            "symbol": "BTC/USDT",
        },
    )

    fear = FearState(
        level=0.80,
        uncertainty=0.80,
        drawdown=0.70,
        recent_failure_rate=0.80,
    )

    action = Thinker().think(world, fear)

    assert action is None


def test_low_confidence_prevents_action():
    world = WorldState(
        confidence=0.30,
        market={
            "signal": "buy",
            "symbol": "BTC/USDT",
        },
    )

    fear = FearState(
        level=0.10,
        uncertainty=0.10,
        drawdown=0.00,
        recent_failure_rate=0.00,
    )

    action = Thinker().think(world, fear)

    assert action is None
