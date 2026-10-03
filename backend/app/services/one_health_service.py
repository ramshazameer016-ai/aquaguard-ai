"""One Health contextual assessment service for AquaGuard AI.

This service provides contextual interpretation only.

It does not diagnose disease, confirm pollution, establish causation,
or replace field/laboratory assessment.
"""

from typing import Any, Dict, List


def assess_one_health_context(
    *,
    event_status: str,
    event_title: str,
    evidence_items: List[Any],
    environmental_observations: List[Any],
) -> Dict[str, Any]:
    """Build a transparent One Health contextual assessment."""

    environmental_context: List[str] = []
    ecological_context: List[str] = []
    human_health_context: List[str] = []

    supporting_context: List[str] = []
    limitations: List[str] = []

    category_text = event_title.lower()

    # ---------------------------------------------------------
    # Environmental context
    # ---------------------------------------------------------

    if environmental_observations:
        for observation in environmental_observations:
            parameter = str(
                getattr(observation, "parameter", "")
            )

            value = getattr(observation, "value", None)
            unit = str(
                getattr(observation, "unit", "")
            )

            source = str(
                getattr(observation, "source", "unknown")
            )

            simulated = bool(
                getattr(observation, "is_simulated", False)
            )

            simulation_text = (
                " This observation is simulated."
                if simulated
                else ""
            )

            environmental_context.append(
                f"{parameter} observation available: "
                f"{value} {unit} from {source}."
                f"{simulation_text}"
            )
    else:
        environmental_context.append(
            "No environmental observations are currently "
            "available for this event."
        )

        limitations.append(
            "Environmental measurements are unavailable."
        )

    # ---------------------------------------------------------
    # Ecological context
    # ---------------------------------------------------------

    if (
        "fish" in category_text
        or "wildlife" in category_text
        or "water" in category_text
        or "discoloration" in category_text
    ):
        ecological_context.append(
            "The reported observation is potentially relevant "
            "to aquatic environmental conditions."
        )

        supporting_context.append(
            "The event concerns an aquatic observation that "
            "may warrant ecological or field investigation."
        )
    else:
        ecological_context.append(
            "The available event description does not provide "
            "a specific ecological interpretation."
        )

    # ---------------------------------------------------------
    # Human-health context
    # ---------------------------------------------------------

    human_health_context.append(
        "The available observation does not establish "
        "human exposure, toxicity, or disease."
    )

    human_health_context.append(
        "Human-health implications require appropriate "
        "environmental, exposure, or laboratory evidence "
        "before a health conclusion is made."
    )

    # ---------------------------------------------------------
    # Evidence context
    # ---------------------------------------------------------

    supporting_count = 0
    conflicting_count = 0

    for item in evidence_items:
        direction = str(
            getattr(item, "direction", "")
        ).lower()

        if direction == "supporting":
            supporting_count += 1

        elif direction == "conflicting":
            conflicting_count += 1

    if supporting_count > 0:
        supporting_context.append(
            f"{supporting_count} stored evidence item(s) "
            "currently support the potential anomaly."
        )

    if conflicting_count > 0:
        limitations.append(
            f"{conflicting_count} stored evidence item(s) "
            "provide conflicting context."
        )

    if not evidence_items:
        limitations.append(
            "No stored evidence items are currently available "
            "for this event."
        )

    # ---------------------------------------------------------
    # Attention level
    # ---------------------------------------------------------

    if event_status in {
        "confirmed_anomaly",
        "escalated",
    }:
        attention_level = "investigation_recommended"

    elif event_status in {
        "under_review",
        "testing_requested",
    }:
        attention_level = "caution"

    elif event_status in {
        "potential",
        "monitor",
        "caution",
        "investigation_recommended",
    }:
        attention_level = "advisory"

    else:
        attention_level = "informational"

    # ---------------------------------------------------------
    # Explicit limitations
    # ---------------------------------------------------------

    limitations.append(
        "This assessment provides contextual One Health "
        "information and does not confirm pollution."
    )

    limitations.append(
        "This assessment does not provide a medical diagnosis."
    )

    limitations.append(
        "Environmental measurements are contextual evidence "
        "and do not independently establish causation."
    )

    return {
        "environmental_context": environmental_context,
        "ecological_context": ecological_context,
        "human_health_context": human_health_context,
        "attention_level": attention_level,
        "supporting_context": supporting_context,
        "limitations": limitations,
        "human_verification_required": True,
        "pollution_confirmation": False,
        "medical_diagnosis": False,
    }