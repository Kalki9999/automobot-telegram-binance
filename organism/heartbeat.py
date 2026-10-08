from organism.memory.store import MemoryStore
from organism.world.model import WorldState


class Heartbeat:
    """
    One organism cycle.

    Observe -> update state -> remember -> return state.

    Decision-making and external actions are deliberately
    not performed here yet.
    """

    def __init__(
        self,
        world: WorldState,
        memory: MemoryStore,
    ) -> None:
        self.world = world
        self.memory = memory

    def tick(self) -> WorldState:
        self.world.timestamp = __import__(
            "datetime"
        ).datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat()

        self.memory.remember(
            "heartbeat",
            {
                "organism_state": self.world.organism_state,
                "fear": self.world.fear,
                "uncertainty": self.world.uncertainty,
                "confidence": self.world.confidence,
                "drawdown": self.world.drawdown,
            },
        )

        return self.world
