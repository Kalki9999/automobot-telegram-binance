from organism.cognition.action import ActionContract
from organism.fear.evaluator import FearState
from organism.governor.permission import PermissionGate


def test_trading_disabled():
    action = ActionContract(
        action_id="test-1",
        skill="trading",
        operation="buy",
        reason="test signal",
        confidence=0.8,
        parameters={"symbol": "BTC/USDT"},
    )

    fear = FearState(
        level=0.1,
        uncertainty=0.1,
        drawdown=0.0,
        recent_failure_rate=0.0,
    )

    result = PermissionGate(
        trading_enabled=False
    ).evaluate(action, fear)

    assert result.allowed is False


def test_high_fear_blocks_trading():
    action = ActionContract(
        action_id="test-2",
        skill="trading",
        operation="buy",
        reason="test signal",
        confidence=0.8,
    )

    fear = FearState(
        level=0.85,
        uncertainty=0.8,
        drawdown=0.8,
        recent_failure_rate=0.8,
    )

    result = PermissionGate(
        trading_enabled=True
    ).evaluate(action, fear)

    assert result.allowed is False


def test_withdrawal_is_blocked():
    action = ActionContract(
        action_id="test-3",
        skill="trading",
        operation="withdraw",
        reason="test",
        confidence=1.0,
    )

    fear = FearState(
        level=0.0,
        uncertainty=0.0,
        drawdown=0.0,
        recent_failure_rate=0.0,
    )

    result = PermissionGate(
        trading_enabled=True,
        allow_withdrawals=False,
    ).evaluate(action, fear)

    assert result.allowed is False
