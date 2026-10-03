"""Transparent risk-outlook service for AquaGuard AI.

This service provides a contextual, rule-based short-term risk outlook.

It does not:
- predict pollution with certainty,
- diagnose health conditions,
- establish environmental causation,
- or provide a calibrated probability.

All calculations are deterministic and based on explicitly supplied
event evidence, stored Evidence Confidence, and authority-approved alerts.
"""

from typing import Any, Dict, List


def calculate_risk_outlook(
    *,
    event_status: str,
    current_evidence_confidence: float,
    previous_evidence_confidence: float | None,
    supporting_evidence_count: int,
    conflicting_evidence_count: int,
    active_alert_count: int,
) -> Dict[str, Any]:
    """Calculate a transparent short-term contextual risk outlook.

    Parameters
    ----------
    event_status:
        Current human-verification/lifecycle status of the event.

    current_evidence_confidence:
        Most recently stored Evidence Confidence score, expected in
        the range 0-100.

    previous_evidence_confidence:
        Previously stored Evidence Confidence score, if available.

    supporting_evidence_count:
        Number of stored evidence items currently marked as supporting.

    conflicting_evidence_count:
        Number of stored evidence items currently marked as conflicting.

    active_alert_count:
        Number of currently active authority-approved alerts.

    Returns
    -------
    Dict[str, Any]
        Values designed to match RiskOutlookResponse.
    """

    # ------------------------------------------------------------------
    # Normalize explicitly supplied numeric inputs.
    # ------------------------------------------------------------------

    current_score = max(
        0.0,
        min(float(current_evidence_confidence), 100.0),
    )

    if previous_evidence_confidence is not None:
        previous_score = max(
            0.0,
            min(float(previous_evidence_confidence), 100.0),
        )
    else:
        previous_score = None

    supporting_count = max(
        0,
        int(supporting_evidence_count),
    )

    conflicting_count = max(
        0,
        int(conflicting_evidence_count),
    )

    active_alerts = max(
        0,
        int(active_alert_count),
    )

    risk_score = 0.0

    factors: List[str] = []
    limitations: List[str] = []

    calculation_parts: List[str] = []

    # ------------------------------------------------------------------
    # 1. Human verification status
    #
    # These are explicit MVP contextual rules.
    # They are not learned probabilities.
    # ------------------------------------------------------------------

    if event_status == "confirmed_anomaly":
        status_points = 35.0

        risk_score += status_points

        factors.append(
            "The event has been confirmed through the human "
            "verification workflow."
        )

        calculation_parts.append(
            f"human_status={status_points:.2f}"
        )

    elif event_status == "escalated":
        status_points = 45.0

        risk_score += status_points

        factors.append(
            "The event has been escalated through the human "
            "verification workflow."
        )

        calculation_parts.append(
            f"human_status={status_points:.2f}"
        )

    elif event_status in {
        "under_review",
        "testing_requested",
    }:
        status_points = 20.0

        risk_score += status_points

        factors.append(
            "The event is undergoing human review or additional testing."
        )

        calculation_parts.append(
            f"human_status={status_points:.2f}"
        )

    else:
        status_points = 0.0

        factors.append(
            "The event has not reached a confirmed or escalated status."
        )

        calculation_parts.append(
            f"human_status={status_points:.2f}"
        )

    # ------------------------------------------------------------------
    # 2. Stored supporting evidence
    #
    # Maximum contribution: 30 points.
    # ------------------------------------------------------------------

    evidence_points = min(
        supporting_count * 10.0,
        30.0,
    )

    if supporting_count > 0:
        risk_score += evidence_points

        factors.append(
            f"{supporting_count} stored evidence item(s) "
            "currently provide supporting context."
        )

    calculation_parts.append(
        f"supporting_evidence={evidence_points:.2f}"
    )

    # ------------------------------------------------------------------
    # 3. Stored conflicting evidence
    #
    # Maximum reduction: 20 points.
    # ------------------------------------------------------------------

    conflict_reduction = min(
        conflicting_count * 8.0,
        20.0,
    )

    if conflicting_count > 0:
        risk_score -= conflict_reduction

        factors.append(
            f"{conflicting_count} stored evidence item(s) "
            "provide conflicting context."
        )

    calculation_parts.append(
        f"conflicting_evidence=-{conflict_reduction:.2f}"
    )

    # ------------------------------------------------------------------
    # 4. Current Evidence Confidence
    #
    # The stored Evidence Confidence contributes 20% of its 0-100
    # value to the contextual risk score.
    #
    # Example:
    #   Evidence Confidence = 50
    #   contribution = 50 * 0.20 = 10
    #
    # This is a deterministic rule, not a probability calibration.
    # ------------------------------------------------------------------

    evidence_confidence_points = current_score * 0.20

    risk_score += evidence_confidence_points

    factors.append(
        "The current stored Evidence Confidence contributes "
        "to the contextual outlook."
    )

    calculation_parts.append(
        f"evidence_confidence={evidence_confidence_points:.2f}"
    )

    # ------------------------------------------------------------------
    # 5. Evidence momentum
    #
    # Momentum is calculated from actual stored Evidence Confidence
    # snapshots.
    #
    # If no previous score exists, momentum is defined as 0 because
    # there is no observed change to calculate.
    # ------------------------------------------------------------------

    if previous_score is None:
        evidence_momentum = 0.0

        factors.append(
            "Evidence momentum is neutral because no previous "
            "Evidence Confidence snapshot is available."
        )

    else:
        evidence_momentum = current_score - previous_score

        if evidence_momentum > 0:
            factors.append(
                f"Evidence Confidence increased by "
                f"{evidence_momentum:.2f} point(s) since the "
                "previous stored snapshot."
            )

        elif evidence_momentum < 0:
            factors.append(
                f"Evidence Confidence decreased by "
                f"{abs(evidence_momentum):.2f} point(s) since the "
                "previous stored snapshot."
            )

        else:
            factors.append(
                "Evidence Confidence is unchanged from the "
                "previous stored snapshot."
            )

    # Momentum is reported as a diagnostic trend measure. It is not
    # separately added to risk_score, preventing double-counting of
    # the current Evidence Confidence.
    calculation_parts.append(
        f"evidence_momentum={evidence_momentum:.2f}"
    )

    # ------------------------------------------------------------------
    # 6. Authority-approved alerts
    #
    # Maximum contribution: 10 points.
    # ------------------------------------------------------------------

    alert_points = min(
        active_alerts * 5.0,
        10.0,
    )

    if active_alerts > 0:
        risk_score += alert_points

        factors.append(
            f"{active_alerts} active authority-approved "
            "alert(s) are associated with the event."
        )

    calculation_parts.append(
        f"active_alerts={alert_points:.2f}"
    )

    # ------------------------------------------------------------------
    # 7. Clamp final contextual risk score.
    # ------------------------------------------------------------------

    risk_score = max(
        0.0,
        min(risk_score, 100.0),
    )

    # ------------------------------------------------------------------
    # 8. Risk bands
    #
    # These are interpretability bands for the MVP, not calibrated
    # probabilities.
    # ------------------------------------------------------------------

    if risk_score >= 70.0:
        risk_band = "high"

    elif risk_score >= 40.0:
        risk_band = "moderate"

    elif risk_score >= 20.0:
        risk_band = "low"

    else:
        risk_band = "minimal"

    # ------------------------------------------------------------------
    # 9. Outlook direction
    #
    # Direction is derived from the actual Evidence Confidence
    # momentum.
    # ------------------------------------------------------------------

    if evidence_momentum > 0:
        outlook_direction = "increasing"

    elif evidence_momentum < 0:
        outlook_direction = "decreasing"

    else:
        outlook_direction = "stable"

    # ------------------------------------------------------------------
    # 10. Limitations and safety boundaries
    # ------------------------------------------------------------------

    limitations.extend(
        [
            "This is a contextual risk outlook, not a calibrated "
            "probability of future pollution or disease.",
            "The outlook does not establish environmental causation.",
            "Evidence Confidence bands and risk bands are "
            "interpretability categories, not calibrated probabilities.",
            "Additional field or laboratory evidence may change "
            "the assessment.",
        ]
    )

    # ------------------------------------------------------------------
    # 11. Human verification remains required.
    # ------------------------------------------------------------------

    return {
        "current_evidence_confidence": round(
            current_score,
            2,
        ),
        "previous_evidence_confidence": (
            round(previous_score, 2)
            if previous_score is not None
            else None
        ),
        "evidence_momentum": round(
            evidence_momentum,
            2,
        ),
        "risk_outlook_score": round(
            risk_score,
            2,
        ),
        "risk_band": risk_band,
        "outlook_direction": outlook_direction,
        "outlook_window": "short_term",
        "calculation": (
            " + ".join(calculation_parts)
            + " ; final_score=clamp(total, 0, 100)"
        ),
        "factors": factors,
        "limitations": limitations,
        "human_verification_required": True,
        "pollution_confirmation": False,
    }