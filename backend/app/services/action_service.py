"""Rule-based recommended actions for AquaGuard AI events.

Recommendations are advisory only. They do not automatically
execute field, laboratory, public-health, or environmental actions.
"""

from typing import Any, Dict, List


def generate_recommended_actions(
    *,
    event_status: str,
    risk_band: str,
    evidence_confidence: float,
    supporting_evidence_count: int,
    conflicting_evidence_count: int,
    active_alert_count: int,
) -> List[Dict[str, Any]]:
    """
    Generate deterministic recommended actions from the current
    event and evidence context.

    These are recommendations for human/authority review.
    """

    actions: List[Dict[str, Any]] = []

    normalized_status = (event_status or "").lower()
    normalized_band = (risk_band or "").lower()

    # ---------------------------------------------------------
    # 1. Field inspection
    # ---------------------------------------------------------

    if (
        normalized_status in {
            "confirmed_anomaly",
            "under_review",
            "testing_requested",
            "under_investigation",
            "verified",
        }
        or normalized_band in {"moderate", "high", "critical"}
    ):
        actions.append(
            {
                "action_type": "site_inspection",
                "description": (
                    "Conduct a field inspection of the affected "
                    "area to verify the reported aquatic condition "
                    "and identify additional observable evidence."
                ),
                "priority": (
                    "high"
                    if normalized_band in {"high", "critical"}
                    or normalized_status in {"confirmed_anomaly", "verified"}
                    else "medium"
                ),
            }
        )

    # ---------------------------------------------------------
    # 2. Water sample collection
    # ---------------------------------------------------------

    if (
        normalized_status in {"confirmed_anomaly", "verified"}
        or normalized_band in {"high", "critical"}
    ):
        actions.append(
            {
                "action_type": "water_sample_collection",
                "description": (
                    "Collect an appropriate water sample for "
                    "field or laboratory testing to investigate "
                    "the observed anomaly. Sampling should follow "
                    "the responsible authority's procedures."
                ),
                "priority": (
                    "urgent"
                    if normalized_band == "critical"
                    else "high"
                ),
            }
        )

    # ---------------------------------------------------------
    # 3. Continued environmental monitoring
    # ---------------------------------------------------------

    if (
        normalized_band in {"moderate", "high", "critical"}
        or supporting_evidence_count > 0
    ):
        actions.append(
            {
                "action_type": "environmental_monitoring",
                "description": (
                    "Continue monitoring relevant environmental "
                    "conditions and subsequent observations around "
                    "the event location."
                ),
                "priority": "medium",
            }
        )

    # ---------------------------------------------------------
    # 4. Additional evidence review
    # ---------------------------------------------------------

    if (
        evidence_confidence < 50
        or conflicting_evidence_count > 0
    ):
        actions.append(
            {
                "action_type": "evidence_review",
                "description": (
                    "Review available citizen reports, spatial-temporal "
                    "correlation, environmental context, and AI evidence "
                    "signals to identify missing or conflicting evidence."
                ),
                "priority": "medium",
            }
        )

    # ---------------------------------------------------------
    # 5. Authority review when an official alert exists
    # ---------------------------------------------------------

    if active_alert_count > 0:
        actions.append(
            {
                "action_type": "authority_review",
                "description": (
                    "Review the current event status, risk outlook, "
                    "evidence history, and active alert before deciding "
                    "whether any further official response is appropriate."
                ),
                "priority": "medium",
            }
        )

    # ---------------------------------------------------------
    # Fallback
    # ---------------------------------------------------------

    if not actions:
        actions.append(
            {
                "action_type": "continued_monitoring",
                "description": (
                    "Continue monitoring the event for additional "
                    "evidence before considering further action."
                ),
                "priority": "low",
            }
        )

    return actions