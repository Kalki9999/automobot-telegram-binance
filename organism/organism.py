from dataclasses import dataclass
from typing import Optional

from organism.cognition.thinker import Thinker
from organism.fear.evaluator import FearState, evaluate_fear
from organism.governor.permission import PermissionGate
from organism.memory.store import MemoryStore
from organism.world.model import WorldState
from skills.trading.adapter import ExecutionResult, TradingAdapter


@dataclass(frozen=True)
class OrganismCycle:
    state: str
    fear: FearState
    action_created: bool
    execution: Optional[ExecutionResult]


class AutomobotOrganism:
    """
    Top-level Automobot organism.

    Observe
      -> evaluate fear
      -> think
      -> create action
      -> permission gate
      -> execute through a skill
      -> remember result

    Cognition never executes an action directly.
    """

    def __init__(
        self,
        *,
        world: WorldState,
        memory: MemoryStore,
        thinker: Thinker,
        permission_gate: PermissionGate,
        trading_skill: TradingAdapter,
    ):
        self.world = world
        self.memory = memory
        self.thinker = thinker
        self.permission_gate = permission_gate
        self.trading_skill = trading_skill

    def cycle(self) -> OrganismCycle:
        # 1. Evaluate internal threat state.
        fear = evaluate_fear(
            uncertainty=self.world.uncertainty,
            drawdown=self.world.drawdown,
            recent_failure_rate=self.world.system.get(
                "recent_failure_rate",
                0.0,
            ),
        )

        self.world.fear = fear.level

        # 2. High fear changes the organism's state.
        self.world.organism_state = fear.mode

        # 3. Cognition proposes an action.
        action = self.thinker.think(
            self.world,
            fear,
        )

        if action is None:
            self.memory.remember(
                "decision",
                {
                    "result": "NO_ACTION",
                    "state": self.world.organism_state,
                    "fear": fear.level,
                },
            )

            return OrganismCycle(
                state=self.world.organism_state,
                fear=fear,
                action_created=False,
                execution=None,
            )

        # 4. Constitution / permission gate.
        permission = self.permission_gate.evaluate(
            action,
            fear,
        )

        if not permission.allowed:
            self.memory.remember(
                "decision",
                {
                    "result": "BLOCKED",
                    "action": action.operation,
                    "reason": permission.reason,
                    "fear": fear.level,
                },
            )

            return OrganismCycle(
                state=self.world.organism_state,
                fear=fear,
                action_created=True,
                execution=None,
            )

        # 5. Execute ONLY through the selected skill.
        execution = self.trading_skill.execute(
            action.operation,
            action.parameters,
        )

        # 6. Remember consequence.
        self.memory.remember(
            "execution",
            {
                "operation": action.operation,
                "status": execution.status,
                "success": execution.success,
                "message": execution.message,
            },
        )

        return OrganismCycle(
            state=self.world.organism_state,
            fear=fear,
            action_created=True,
            execution=execution,
        )
