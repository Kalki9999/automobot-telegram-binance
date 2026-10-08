from dataclasses import dataclass


@dataclass(frozen=True)
class ConfidenceState:
    raw_confidence: float
    calibrated_confidence: float
    sample_count: int
    accuracy: float
    calibration_error: float


def calibrate_confidence(
    *,
    raw_confidence: float,
    correct_predictions: int,
    total_predictions: int,
) -> ConfidenceState:

    raw = max(0.0, min(1.0, raw_confidence))
    total = max(0, total_predictions)
    correct = max(0, min(correct_predictions, total))

    if total == 0:
        accuracy = 0.0
        # No evidence means confidence must not be trusted.
        calibrated = raw * 0.5
    else:
        accuracy = correct / total

        # Evidence gradually pulls claimed confidence
        # toward observed accuracy.
        weight = min(1.0, total / 100.0)

        calibrated = (
            raw * (1.0 - weight)
            + accuracy * weight
        )

    calibration_error = abs(raw - accuracy)

    return ConfidenceState(
        raw_confidence=raw,
        calibrated_confidence=round(calibrated, 4),
        sample_count=total,
        accuracy=round(accuracy, 4),
        calibration_error=round(calibration_error, 4),
    )
