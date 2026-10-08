from organism.cognition.thinker import Thinker
from organism.governor.permission import PermissionGate
from organism.memory.store import MemoryStore
from organism.organism import AutomobotOrganism
from organism.world.model import WorldState
from skills.trading.freqtrade import FreqtradeAdapter


def build_organism(tmp_path, *, trading_enabled=False):
    world = WorldState(
        capital=100.0,
        available_capital=100.0,
        confidence=0.80,
        uncertainty=0.10,
        drawdown=0.0,
        market={
            "signal": "buy",
            "symbol": "BTC/USDT",
        },
        system={
            "recent_failure_rate": 0.0,
        },
    )

    memory = MemoryStore(
        str(tmp_path / "memory.json")
    )

    return AutomobotOrganism(
        world=world,
        memory=memory,
        thinker=Thinker(),
        permission_gate=PermissionGate(
            trading_enabled=trading_enabled,
        ),
        trading_skill=FreqtradeAdapter(
            dry_run=True,
        ),
    ), memory


def test_organism_blocks_live_trade(tmp_path):
    organism, memory = build_organism(
        tmp_path,
        trading_enabled=False,
    )

    result = organism.cycle()

    assert result.action_created is True
    assert result.execution is None

    events = memory.recent()
    assert events[-1]["type"] == "decision"
    assert events[-1]["data"]["result"] == "BLOCKED"


def test_organism_executes_dry_run(tmp_path):
    organism, memory = build_organism(
        tmp_path,
        trading_enabled=True,
    )

    result = organism.cycle()

    assert result.action_created is True
    assert result.execution is not None
    assert result.execution.status == "DRY_RUN"

    events = memory.recent()
    assert events[-1]["type"] == "execution"


def test_organism_stays_defensive_under_high_fear(tmp_path):
    organism, memory = build_organism(
        tmp_path,
        trading_enabled=True,
    )

    organism.world.drawdown = 0.20
    organism.world.uncertainty = 0.90
    organism.world.system["recent_failure_rate"] = 0.80

    result = organism.cycle()

    assert result.state == "SURVIVAL"
    assert result.action_created is False
    assert result.execution is None

    events = memory.recent()
    assert events[-1]["data"]["result"] == "NO_ACTION"
