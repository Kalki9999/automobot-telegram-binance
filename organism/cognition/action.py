from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(frozen=True)
class ActionContract:
    """
    The only form in which the organism may request an external action.

    Cognition proposes an action.
    It does not execute the action.
    """

    action_id: str
    skill: str
    operation: str
    reason: str
    confidence: float
    parameters: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.action_id:
            raise ValueError("action_id is required")

        if not self.skill:
            raise ValueError("skill is required")

        if not self.operation:
            raise ValueError("operation is required")

        if not self.reason:
            raise ValueError("reason is required")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
