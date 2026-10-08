from organism.heartbeat import Heartbeat
from organism.memory.store import MemoryStore
from organism.world.model import WorldState


def test_world_state():
    world = WorldState()

    world.update(
        capital=100.0,
        available_capital=95.0,
        fear=0.25,
        confidence=0.70,
        organism_state="OBSERVING",
    )

    assert world.capital == 100.0
    assert world.available_capital == 95.0
    assert world.fear == 0.25
    assert world.confidence == 0.70


def test_memory_persists(tmp_path):
    path = tmp_path / "memory.json"

    memory = MemoryStore(str(path))

    memory.remember(
        "test",
        {"message": "organism alive"},
    )

    restored = MemoryStore(str(path))

    assert len(restored.recent()) == 1
    assert restored.recent()[0]["type"] == "test"


def test_heartbeat_records_event(tmp_path):
    path = tmp_path / "memory.json"

    world = WorldState(
        organism_state="OBSERVING",
        fear=0.2,
        uncertainty=0.3,
        confidence=0.7,
    )

    memory = MemoryStore(str(path))
    heartbeat = Heartbeat(world, memory)

    heartbeat.tick()

    events = memory.recent()

    assert len(events) == 1
    assert events[0]["type"] == "heartbeat"
    assert events[0]["data"]["fear"] == 0.2
