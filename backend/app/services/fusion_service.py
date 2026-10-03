"""Explainable evidence fusion for AquaGuard AI.

Stage 7:

- Evidence Confidence
- AI Belief
- Supporting / conflicting / missing evidence
- Evidence quality
- Evidence agreement
- Source independence
- Evidence completeness

Important:

Evidence Confidence is an ordinal prioritisation index.

AI Belief is an assessment-reliability indicator based on
measurable properties of the evidence actually available.

Neither value is a probability of pollution, toxicity, or causation.

The fusion engine must never invent evidence merely to increase
the score. Missing evidence contributes zero points.

The maximum component weights below are architecture-level
expert priors. They are not calibrated probabilities.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional


# -------------------------------------------------------------------
# Architecture-defined maximum contributions
# -------------------------------------------------------------------
#
# These are NOT output values.
#
# They are the maximum number of points a component can contribute
# when the corresponding real evidence signal is 1.0 and satisfies
# the applicable quality conditions.
#
# The seven maxima sum to 100.
#
# Source:
# AquaGuard AI architecture, Section H.2.
# -------------------------------------------------------------------

MAX_WEIGHTS = {
    "photo_text": 25.0,
    "independent_reports": 20.0,
    "spatiotemporal_cluster": 10.0,
    "rainfall": 10.0,
    "dissolved_oxygen": 15.0,
    "water_temperature": 10.0,
    "historical_similarity": 10.0,
}


# -------------------------------------------------------------------
# Utility functions
# -------------------------------------------------------------------

def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:
    """Keep a value inside a specified range."""
    return max(minimum, min(maximum, value))


def clamp01(value: float) -> float:
    """Keep a signal inside the [0, 1] range."""
    return max(0.0, min(1.0, float(value)))


def confidence_band(score: float) -> str:
    """Architecture bands for Evidence Confidence."""
    if score < 35:
        return "low"

    if score < 65:
        return "moderate"

    return "high"


def belief_band(score: float) -> str:
    """Interpretability bands for AI Belief."""
    if score < 35:
        return "low"

    if score < 65:
        return "moderate"

    return "high"


# -------------------------------------------------------------------
# Evidence quality
# -------------------------------------------------------------------

def quality_factor(data_quality: Optional[str]) -> float:
    """Convert an explicitly supplied quality label to a factor.

    This is a deterministic data-quality adjustment, not a
    probability of correctness.

    Unknown quality is deliberately conservative.
    """

    if not data_quality:
        return 0.70

    normalized = str(data_quality).strip().lower()

    if normalized in {"high", "verified", "good"}:
        return 1.00

    if normalized in {"medium", "moderate", "partial", "provisional"}:
        return 0.70

    if normalized in {"low", "poor"}:
        return 0.40

    if normalized == "stale":
        return 0.40

    if normalized == "simulated":
        # Simulated evidence is explicitly labelled.
        # It is usable for the demo but must not silently look
        # like measured real-world evidence.
        return 0.60

    return 0.70


# -------------------------------------------------------------------
# Evidence Confidence
# -------------------------------------------------------------------

def calculate_evidence_confidence(
    contributions: List[Dict[str, Any]],
    conflict_adjustment: float = 0.0,
) -> float:
    """Calculate Evidence Confidence from actual contributions.

    Only supporting contribution values enter the positive total.

    Conflict deductions are explicit and separately logged.

    No score is added merely because an evidence category exists.
    """

    supporting_total = sum(
        float(item.get("contribution", 0.0))
        for item in contributions
        if item.get("direction") == "supporting"
    )

    total = supporting_total + float(conflict_adjustment)

    return round(clamp(total), 2)


# -------------------------------------------------------------------
# Evidence agreement
# -------------------------------------------------------------------

def calculate_evidence_agreement(
    supporting_count: int,
    conflicting_count: int,
) -> float:
    """Calculate directional agreement from actual evidence items."""

    total = supporting_count + conflicting_count

    if total == 0:
        return 0.0

    return round(
        clamp(
            supporting_count / total * 100.0
        ),
        2,
    )


# -------------------------------------------------------------------
# Evidence completeness
# -------------------------------------------------------------------

def calculate_evidence_completeness(
    available_count: int,
    expected_count: int,
) -> float:
    """Calculate the fraction of expected evidence components available."""

    if expected_count <= 0:
        return 0.0

    return round(
        clamp(
            available_count / expected_count * 100.0
        ),
        2,
    )


# -------------------------------------------------------------------
# AI Belief
# -------------------------------------------------------------------

def calculate_ai_belief(
    *,
    quality_score: float,
    agreement_score: float,
    independence_score: float,
    completeness_score: float,
) -> float:
    """Calculate AI Belief from measurable evidence properties.

    IMPORTANT:

    This function does not use a hard-coded desired result.

    It takes four independently calculated properties of the
    evidence and uses their simple arithmetic mean.

    Therefore, if evidence quality, agreement, independence, or
    completeness changes, AI Belief changes directly.

    AI Belief is NOT a probability.
    """

    belief = (
        quality_score
        + agreement_score
        + independence_score
        + completeness_score
    ) / 4.0

    return round(clamp(belief), 2)


# -------------------------------------------------------------------
# Internal helpers
# -------------------------------------------------------------------

def _make_missing(
    evidence_type: str,
    description: str,
    maximum: float,
) -> Dict[str, Any]:
    """Create a genuinely missing evidence record."""

    return {
        "evidence_type": evidence_type,
        "direction": "missing",
        "signal": 0.0,
        "weight": maximum,
        "contribution": 0.0,
        "data_quality": "missing",
        "description": description,
    }


def _make_neutral(
    evidence_type: str,
    description: str,
    maximum: float,
    signal: float = 0.0,
) -> Dict[str, Any]:
    """Create a neutral evidence record with zero contribution."""

    return {
        "evidence_type": evidence_type,
        "direction": "neutral",
        "signal": round(clamp01(signal), 4),
        "weight": maximum,
        "contribution": 0.0,
        "data_quality": "available",
        "description": description,
    }


def _append_supporting(
    item: Dict[str, Any],
    contributions: List[Dict[str, Any]],
    supporting: List[Dict[str, Any]],
) -> None:
    """Append an actual supporting evidence item."""

    contributions.append(item)
    supporting.append(item)


# -------------------------------------------------------------------
# Main fusion function
# -------------------------------------------------------------------

def fuse_evidence(
    *,
    text_result: Dict[str, Any],
    photo_result: Optional[Dict[str, Any]] = None,
    community_result: Optional[Dict[str, Any]] = None,
    environmental_result: Optional[Dict[str, Any]] = None,
    historical_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Fuse real available evidence into an auditable assessment.

    The function deliberately does NOT fabricate environmental,
    historical, or community signals.

    Inputs should contain measurements/results produced by the
    preceding AquaGuard AI modules.
    """

    contributions: List[Dict[str, Any]] = []

    supporting_evidence: List[Dict[str, Any]] = []

    conflicting_evidence: List[Dict[str, Any]] = []

    missing_evidence: List[Dict[str, Any]] = []

    conflict_adjustment = 0.0

    # ================================================================
    # 1. PHOTO + TEXT
    # ================================================================
    #
    # Architecture:
    #
    # 25 x (
    #     0.7 x image_signal x quality_factor
    #     +
    #     0.3 x text_signal
    # )
    #
    # This is ONE 25-point component, not two independent 25-point
    # components.
    # ================================================================

    text_signal = clamp01(
        float(
            text_result.get(
                "overall_signal",
                0.0,
            )
        )
    )

    image_available = bool(
        photo_result
        and photo_result.get("vision_analyzed")
    )

    if image_available:
        indicators = photo_result.get(
            "indicators",
            {},
        )

        visual_signals: List[float] = []

        for indicator in indicators.values():
            if not isinstance(indicator, dict):
                continue

            if "signal" not in indicator:
                continue

            visual_signals.append(
                clamp01(
                    float(
                        indicator.get(
                            "signal",
                            0.0,
                        )
                    )
                )
            )

        image_signal = (
            max(visual_signals)
            if visual_signals
            else 0.0
        )

        image_quality = photo_result.get(
            "data_quality",
            "medium",
        )

        # If the vision module supplies an explicit water-scene
        # signal, use it as a cap only when it indicates the image
        # is not a water scene.
        water_scene_signal = photo_result.get(
            "water_scene_signal"
        )

        if isinstance(water_scene_signal, dict):
            scene_signal = clamp01(
                float(
                    water_scene_signal.get(
                        "signal",
                        0.0,
                    )
                )
            )

            scene_prompt = str(
                water_scene_signal.get(
                    "prompt",
                    "",
                )
            ).lower()

            if "not a water scene" in scene_prompt:
                image_signal = min(
                    image_signal,
                    1.0 - scene_signal,
                )

        image_quality_value = quality_factor(
            image_quality
        )

        photo_text_signal = clamp01(
            (
                0.7
                * image_signal
                * image_quality_value
            )
            +
            (
                0.3
                * text_signal
            )
        )

        photo_text_contribution = (
            MAX_WEIGHTS["photo_text"]
            * photo_text_signal
        )

        if photo_text_signal > 0:
            item = {
                "evidence_type": "photo_text",
                "direction": "supporting",
                "signal": round(
                    photo_text_signal,
                    4,
                ),
                "image_signal": round(
                    image_signal,
                    4,
                ),
                "text_signal": round(
                    text_signal,
                    4,
                ),
                "image_quality_factor": round(
                    image_quality_value,
                    4,
                ),
                "weight": MAX_WEIGHTS["photo_text"],
                "contribution": round(
                    photo_text_contribution,
                    2,
                ),
                "data_quality": image_quality,
                "description": (
                    "Photo and report-text signals were "
                    "combined using the architecture-defined "
                    "25-point photo+text component."
                ),
            }

            _append_supporting(
                item,
                contributions,
                supporting_evidence,
            )

        else:
            item = _make_neutral(
                "photo_text",
                (
                    "Photo and text were available, but "
                    "their combined anomaly signal was zero."
                ),
                MAX_WEIGHTS["photo_text"],
            )

            contributions.append(item)

    else:
        # Vision/photo evidence is unavailable.
        #
        # Architecture fallback:
        # score from the available text/context evidence and
        # explicitly record the photo evidence as missing.
        #
        # We do NOT invent an image signal.
        #
        # Only the documented text portion of the 25-point
        # photo+text component contributes when no image is
        # available:
        #
        # 25 x (0.3 x text_signal)

        photo_text_signal = clamp01(
            0.3 * text_signal
        )

        photo_text_contribution = (
            MAX_WEIGHTS["photo_text"]
            * photo_text_signal
        )

        if text_signal > 0:
            item = {
                "evidence_type": "photo_text",
                "direction": "supporting",
                "signal": round(
                    photo_text_signal,
                    4,
                ),
                "image_signal": None,
                "text_signal": round(
                    text_signal,
                    4,
                ),
                "image_quality_factor": None,
                "weight": MAX_WEIGHTS["photo_text"],
                "contribution": round(
                    photo_text_contribution,
                    2,
                ),
                "data_quality": "text_available_photo_missing",
                "description": (
                    "Photo evidence was unavailable, so the "
                    "available report-text signal contributed "
                    "through the text portion of the architecture-"
                    "defined photo+text component. No image signal "
                    "was invented."
                ),
            }

            _append_supporting(
                item,
                contributions,
                supporting_evidence,
            )

            # The photo remains explicitly unavailable, but it is
            # represented inside the single photo_text component.
            # Do not create a separate fusion component for the
            # missing photo, because the architecture defines
            # photo+text as one 25-point component.

        else:
            item = _make_missing(
                "photo_text",
                (
                    "Neither photo evidence nor a supporting "
                    "report-text signal was available for the "
                    "photo+text fusion component."
                ),
                MAX_WEIGHTS["photo_text"],
            )
            contributions.append(item)
            missing_evidence.append(item)
    # ================================================================
    # 2. INDEPENDENT REPORTS
    # ================================================================
    #
    # Architecture:
    #
    # 20 x (1 - exp(-k x n_eff))
    #
    # n_eff excludes the target report and represents actual
    # independent reporter groups after deduplication.
    #
    # k = 0.6 is the architecture's stated diminishing-return
    # parameter.
    # ================================================================

    if community_result is not None:
        independent_count_raw = community_result.get(
            "independent_report_count"
        )

        if independent_count_raw is not None:
            independent_count = max(
                0,
                int(independent_count_raw),
            )

            # independent_report_count from the current correlation
            # service represents independent reports associated with
            # the target. The target report itself is not an additional
            # corroborating report.
            n_eff = float(independent_count)

            k = 0.6

            independent_signal = clamp01(
                1.0 - math.exp(
                    -k * n_eff
                )
            )

            contribution = (
                MAX_WEIGHTS["independent_reports"]
                * independent_signal
            )

            if independent_count > 0:
                item = {
                    "evidence_type": "independent_reports",
                    "direction": "supporting",
                    "signal": round(
                        independent_signal,
                        4,
                    ),
                    "effective_independent_count": round(
                        n_eff,
                        4,
                    ),
                    "independent_report_count": independent_count,
                    "weight": MAX_WEIGHTS[
                        "independent_reports"
                    ],
                    "contribution": round(
                        contribution,
                        2,
                    ),
                    "data_quality": "medium",
                    "description": (
                        "Independent nearby reports contributed "
                        "using a diminishing-return function."
                    ),
                }

                _append_supporting(
                    item,
                    contributions,
                    supporting_evidence,
                )

            else:
                item = _make_neutral(
                    "independent_reports",
                    (
                        "Community correlation was available, "
                        "but no independent corroborating "
                        "reports were found."
                    ),
                    MAX_WEIGHTS["independent_reports"],
                )

                contributions.append(item)

        else:
            item = _make_missing(
                "independent_reports",
                (
                    "Community correlation did not provide "
                    "an independent report count."
                ),
                MAX_WEIGHTS["independent_reports"],
            )

            contributions.append(item)
            missing_evidence.append(item)

    else:
        item = _make_missing(
            "independent_reports",
            "Community correlation was not available.",
            MAX_WEIGHTS["independent_reports"],
        )

        contributions.append(item)
        missing_evidence.append(item)

    # ================================================================
    # 3. SPATIOTEMPORAL CLUSTER
    # ================================================================
    #
    # Architecture:
    #
    # 10 x spatial_score x temporal_score x type_agreement
    #
    # The correlation service currently provides enough information
    # to calculate spatial and temporal proximity for the target's
    # related reports.
    #
    # We do not invent type agreement. If same_category_count and
    # related_report_count are available, it is derived directly.
    # ================================================================

    if community_result is not None:
        related_count = max(
            0,
            int(
                community_result.get(
                    "related_report_count",
                    0,
                )
            ),
        )

        same_category_count = max(
            0,
            int(
                community_result.get(
                    "same_category_count",
                    0,
                )
            ),
        )

        cluster_detected = bool(
            community_result.get(
                "cluster_detected",
                False,
            )
        )

        related_reports = community_result.get(
            "related_reports",
            [],
        )

        if cluster_detected and related_count > 0:
            # Spatial score:
            # actual distances are used when returned by the
            # correlation service.
            spatial_scores: List[float] = []

            temporal_scores: List[float] = []

            for related in related_reports:
                if not isinstance(related, dict):
                    continue

                distance_km = related.get(
                    "distance_km"
                )

                if distance_km is not None:
                    distance = max(
                        0.0,
                        float(distance_km),
                    )

                    # 1.0 at 0 km, 0.0 at 2 km.
                    spatial_scores.append(
                        clamp01(
                            1.0
                            - (
                                distance / 2.0
                            )
                        )
                    )

                time_difference_hours = related.get(
                    "time_difference_hours"
                )

                if time_difference_hours is not None:
                    hours = max(
                        0.0,
                        float(
                            time_difference_hours
                        ),
                    )

                    # 1.0 within 24 h, linear decline
                    # to 0 at 72 h.
                    if hours <= 24.0:
                        temporal_scores.append(1.0)
                    elif hours >= 72.0:
                        temporal_scores.append(0.0)
                    else:
                        temporal_scores.append(
                            clamp01(
                                1.0
                                - (
                                    (hours - 24.0)
                                    / 48.0
                                )
                            )
                        )

            spatial_score = (
                sum(spatial_scores)
                / len(spatial_scores)
                if spatial_scores
                else 0.0
            )

            temporal_score = (
                sum(temporal_scores)
                / len(temporal_scores)
                if temporal_scores
                else 0.0
            )

            if related_count > 0:
                type_agreement = clamp01(
                    same_category_count
                    / related_count
                )
            else:
                type_agreement = 0.0

            cluster_signal = (
                spatial_score
                * temporal_score
                * type_agreement
            )

            cluster_contribution = (
                MAX_WEIGHTS["spatiotemporal_cluster"]
                * cluster_signal
            )

            if cluster_signal > 0:
                item = {
                    "evidence_type": "spatiotemporal_cluster",
                    "direction": "supporting",
                    "signal": round(
                        cluster_signal,
                        4,
                    ),
                    "spatial_score": round(
                        spatial_score,
                        4,
                    ),
                    "temporal_score": round(
                        temporal_score,
                        4,
                    ),
                    "type_agreement": round(
                        type_agreement,
                        4,
                    ),
                    "weight": MAX_WEIGHTS[
                        "spatiotemporal_cluster"
                    ],
                    "contribution": round(
                        cluster_contribution,
                        2,
                    ),
                    "data_quality": "medium",
                    "description": (
                        "Spatial proximity, temporal proximity, "
                        "and reported-category agreement were "
                        "derived from the community correlation "
                        "results."
                    ),
                }

                _append_supporting(
                    item,
                    contributions,
                    supporting_evidence,
                )

            else:
                item = _make_neutral(
                    "spatiotemporal_cluster",
                    (
                        "A related cluster exists, but the "
                        "available spatial, temporal, or type "
                        "information does not provide a positive "
                        "cluster contribution."
                    ),
                    MAX_WEIGHTS["spatiotemporal_cluster"],
                )

                contributions.append(item)

        else:
            item = _make_neutral(
                "spatiotemporal_cluster",
                (
                    "No spatiotemporal community cluster was "
                    "detected."
                ),
                MAX_WEIGHTS["spatiotemporal_cluster"],
            )

            contributions.append(item)

    else:
        item = _make_missing(
            "spatiotemporal_cluster",
            "Community correlation was not available.",
            MAX_WEIGHTS["spatiotemporal_cluster"],
        )

        contributions.append(item)
        missing_evidence.append(item)

    # ================================================================
    # 4. ENVIRONMENTAL COMPONENTS
    # ================================================================
    #
    # Environmental evidence is deliberately split into the three
    # architecture-defined components:
    #
    # rainfall          max 10
    # dissolved oxygen  max 15
    # temperature       max 10
    #
    # We do NOT manufacture severity from a generic environmental
    # "signal".
    #
    # The caller must provide a real, already-derived [0,1] severity
    # for a component when sufficient environmental data exists.
    # ================================================================

    environmental_components = {
        "rainfall": {
            "maximum": MAX_WEIGHTS["rainfall"],
            "field": "rainfall_severity",
            "description": (
                "Rainfall severity derived from actual rainfall "
                "observations and an available local baseline."
            ),
        },
        "dissolved_oxygen": {
            "maximum": MAX_WEIGHTS["dissolved_oxygen"],
            "field": "dissolved_oxygen_severity",
            "description": (
                "Dissolved-oxygen severity derived from an actual "
                "DO observation and configured domain thresholds."
            ),
        },
        "water_temperature": {
            "maximum": MAX_WEIGHTS["water_temperature"],
            "field": "water_temperature_severity",
            "description": (
                "Water-temperature severity derived from an actual "
                "water-temperature observation and an available "
                "seasonal/local reference."
            ),
        },
    }

    for evidence_type, config in environmental_components.items():

        maximum = float(config["maximum"])
        field = str(config["field"])

        if environmental_result is None:
            item = _make_missing(
                evidence_type,
                (
                    f"{config['description']} "
                    "No environmental result was supplied."
                ),
                maximum,
            )

            contributions.append(item)
            missing_evidence.append(item)
            continue

        # Accept only the explicitly named severity.
        # We intentionally DO NOT fall back to a generic "signal".
        raw_signal = environmental_result.get(
            field
        )

        if raw_signal is None:
            item = _make_missing(
                evidence_type,
                (
                    f"{config['description']} "
                    "The required severity value was not "
                    "available, so no contribution was assigned."
                ),
                maximum,
            )

            contributions.append(item)
            missing_evidence.append(item)
            continue

        signal = clamp01(
            float(raw_signal)
        )

        data_quality = environmental_result.get(
            f"{evidence_type}_data_quality",
            environmental_result.get(
                "data_quality",
                "provisional",
            ),
        )

        q_factor = quality_factor(
            data_quality
        )

        contribution = (
            maximum
            * signal
            * q_factor
        )

        is_simulated = bool(
            environmental_result.get(
                f"{evidence_type}_is_simulated",
                environmental_result.get(
                    "is_simulated",
                    False,
                ),
            )
        )

        if signal > 0:
            item = {
                "evidence_type": evidence_type,
                "direction": "supporting",
                "signal": round(
                    signal,
                    4,
                ),
                "quality_factor": round(
                    q_factor,
                    4,
                ),
                "weight": maximum,
                "contribution": round(
                    contribution,
                    2,
                ),
                "data_quality": data_quality,
                "is_simulated": is_simulated,
                "description": config[
                    "description"
                ],
            }

            _append_supporting(
                item,
                contributions,
                supporting_evidence,
            )

        else:
            item = {
                "evidence_type": evidence_type,
                "direction": "neutral",
                "signal": 0.0,
                "quality_factor": round(
                    q_factor,
                    4,
                ),
                "weight": maximum,
                "contribution": 0.0,
                "data_quality": data_quality,
                "is_simulated": is_simulated,
                "description": (
                    config["description"]
                    + " The measured/derived severity "
                    "was zero."
                ),
            }

            contributions.append(item)

    # ================================================================
    # 5. HISTORICAL SIMILARITY
    # ================================================================
    #
    # Architecture:
    #
    # 10 x cosine similarity between current feature vector and
    # previous reviewed events of the same type.
    #
    # No history = 0.
    # ================================================================

    if historical_result is None:
        item = _make_missing(
            "historical_similarity",
            (
                "No reviewed historical-event similarity result "
                "was available."
            ),
            MAX_WEIGHTS["historical_similarity"],
        )

        contributions.append(item)
        missing_evidence.append(item)

    else:
        raw_signal = historical_result.get(
            "signal"
        )

        if raw_signal is None:
            item = _make_missing(
                "historical_similarity",
                (
                    "Historical data was supplied, but no "
                    "similarity signal was available."
                ),
                MAX_WEIGHTS["historical_similarity"],
            )

            contributions.append(item)
            missing_evidence.append(item)

        else:
            historical_signal = clamp01(
                float(raw_signal)
            )

            historical_contribution = (
                MAX_WEIGHTS["historical_similarity"]
                * historical_signal
            )

            if historical_signal > 0:
                item = {
                    "evidence_type": "historical_similarity",
                    "direction": "supporting",
                    "signal": round(
                        historical_signal,
                        4,
                    ),
                    "weight": MAX_WEIGHTS[
                        "historical_similarity"
                    ],
                    "contribution": round(
                        historical_contribution,
                        2,
                    ),
                    "data_quality": historical_result.get(
                        "data_quality",
                        "medium",
                    ),
                    "description": (
                        "Historical similarity was supplied "
                        "from reviewed events."
                    ),
                }

                _append_supporting(
                    item,
                    contributions,
                    supporting_evidence,
                )

            else:
                item = _make_neutral(
                    "historical_similarity",
                    (
                        "Historical similarity was available "
                        "but produced zero similarity."
                    ),
                    MAX_WEIGHTS["historical_similarity"],
                )

                contributions.append(item)

    # ================================================================
    # 6. EXPLICIT CONFLICTS
    # ================================================================
    #
    # We do not manufacture conflicts.
    #
    # A future evidence adapter can supply explicit conflict
    # adjustments. For now, conflict_adjustment remains zero unless
    # an evidence item explicitly provides a negative adjustment.
    #
    # This prevents "no evidence" from being incorrectly interpreted
    # as contradictory evidence.
    # ================================================================

    for item in contributions:
        if item.get("direction") != "conflicting":
            continue

        adjustment = float(
            item.get(
                "conflict_adjustment",
                0.0,
            )
        )

        if adjustment > 0:
            adjustment = -adjustment

        conflict_adjustment += adjustment

        conflicting_evidence.append(item)

    # ================================================================
    # 7. EVIDENCE CONFIDENCE
    # ================================================================

    evidence_confidence = calculate_evidence_confidence(
        contributions=contributions,
        conflict_adjustment=conflict_adjustment,
    )

    confidence = confidence_band(
        evidence_confidence
    )

    # ================================================================
    # 8. EVIDENCE QUALITY
    # ================================================================
    #
    # Quality is calculated only from evidence that actually exists.
    #
    # Missing evidence does NOT become a low-quality item.
    # ================================================================

    available_items = [
        item
        for item in contributions
        if item.get("direction") != "missing"
    ]

    if available_items:
        quality_values = [
            quality_factor(
                item.get("data_quality")
            )
            for item in available_items
        ]

        quality_score = round(
            sum(quality_values)
            / len(quality_values)
            * 100.0,
            2,
        )
    else:
        quality_score = 0.0

    # ================================================================
    # 9. EVIDENCE AGREEMENT
    # ================================================================

    supporting_count = len(
        supporting_evidence
    )

    conflicting_count = len(
        conflicting_evidence
    )

    agreement_score = calculate_evidence_agreement(
        supporting_count=supporting_count,
        conflicting_count=conflicting_count,
    )

    # ================================================================
    # 10. SOURCE INDEPENDENCE
    # ================================================================
    #
    # IMPORTANT:
    #
    # Evidence categories are NOT automatically independent sources.
    #
    # A photo and text from the same citizen are one source.
    #
    # We therefore use explicit independent-source information when
    # provided by an upstream module.
    #
    # If it is not supplied, we conservatively derive independence
    # only from community independent reports plus distinct external
    # evidence sources explicitly declared by the input.
    # ================================================================

    explicit_independent_sources = set()

    if community_result is not None:
        independent_report_count = community_result.get(
            "independent_report_count"
        )

        if independent_report_count is not None:
            if int(independent_report_count) > 0:
                explicit_independent_sources.add(
                    "community_independent_reports"
                )

    if environmental_result is not None:
        environmental_source = environmental_result.get(
            "source"
        )

        if environmental_source:
            explicit_independent_sources.add(
                f"environment:{environmental_source}"
            )

    if historical_result is not None:
        historical_source = historical_result.get(
            "source"
        )

        if historical_source:
            explicit_independent_sources.add(
                f"historical:{historical_source}"
            )

    explicit_source_count = len(
        explicit_independent_sources
    )

    # The current MVP can verify whether at least one genuinely
    # independent evidence source exists. It does not pretend that
    # evidence categories equal independent sources.
    #
    # For the normalized score, 4 independent source groups is the
    # maximum meaningful reference used by this MVP.
    independence_score = round(
        clamp(
            explicit_source_count
            / 4.0
            * 100.0
        ),
        2,
    )

    # ================================================================
    # 11. EVIDENCE COMPLETENESS
    # ================================================================
    #
    # Seven architecture-defined components are expected:
    #
    # 1 photo+text
    # 2 independent reports
    # 3 spatiotemporal cluster
    # 4 rainfall
    # 5 dissolved oxygen
    # 6 water temperature
    # 7 historical similarity
    #
    # Only actually available components count.
    # ================================================================

    expected_evidence_categories = 7

    available_evidence_categories = len(
        [
            item
            for item in contributions
            if item.get("direction") != "missing"
        ]
    )

    completeness_score = calculate_evidence_completeness(
        available_count=available_evidence_categories,
        expected_count=expected_evidence_categories,
    )

    # ================================================================
    # 12. AI BELIEF
    # ================================================================
    #
    # No desired score is inserted.
    #
    # It is the direct arithmetic mean of four measurable properties
    # of the evidence currently available.
    # ================================================================

    ai_belief = calculate_ai_belief(
        quality_score=quality_score,
        agreement_score=agreement_score,
        independence_score=independence_score,
        completeness_score=completeness_score,
    )

    belief = belief_band(
        ai_belief
    )

    # ================================================================
    # 13. HUMAN-READABLE REASONING
    # ================================================================

    reasoning: List[str] = []

    if supporting_count:
        reasoning.append(
            f"{supporting_count} evidence component(s) "
            "currently provide supporting signals."
        )
    else:
        reasoning.append(
            "No available evidence component currently "
            "provides a supporting signal."
        )

    if explicit_source_count >= 2:
        reasoning.append(
            f"{explicit_source_count} explicitly identified "
            "independent source group(s) contributed."
        )
    elif explicit_source_count == 1:
        reasoning.append(
            "Only one explicitly identified independent "
            "source group is currently available."
        )
    else:
        reasoning.append(
            "No explicitly identified independent source "
            "groups were available."
        )

    if conflicting_count:
        reasoning.append(
            f"{conflicting_count} explicit conflicting "
            "evidence item(s) were detected."
        )
    else:
        reasoning.append(
            "No explicit conflicting evidence was supplied."
        )

    if missing_evidence:
        reasoning.append(
            f"{len(missing_evidence)} of the "
            f"{expected_evidence_categories} expected "
            "evidence components are currently missing."
        )
    else:
        reasoning.append(
            "All expected evidence components are available."
        )

    # Simulation transparency
    simulated_components = [
        item
        for item in contributions
        if item.get("is_simulated") is True
    ]

    if simulated_components:
        reasoning.append(
            f"{len(simulated_components)} evidence component(s) "
            "use explicitly simulated data."
        )

    # Quality explanation
    if quality_score < 60:
        reasoning.append(
            "The available evidence quality is limited."
        )
    elif quality_score < 80:
        reasoning.append(
            "The available evidence has mixed or provisional quality."
        )
    else:
        reasoning.append(
            "The available evidence is generally high quality "
            "for this assessment."
        )

    # Agreement explanation
    if supporting_count + conflicting_count == 0:
        reasoning.append(
            "Directional agreement cannot be established because "
            "there are no supporting or conflicting evidence items."
        )
    elif agreement_score >= 80:
        reasoning.append(
            "Available directional evidence is largely consistent."
        )
    elif agreement_score >= 50:
        reasoning.append(
            "Available evidence contains mixed directional signals."
        )
    else:
        reasoning.append(
            "Available evidence shows substantial directional disagreement."
        )

    # ================================================================
    # 14. RETURN AUDITABLE RESULT
    # ================================================================

    return {
        "evidence_confidence": evidence_confidence,
        "confidence_band": confidence,

        "ai_belief": ai_belief,
        "belief_band": belief,

        "belief_factors": {
            "evidence_quality": quality_score,
            "evidence_agreement": agreement_score,
            "source_independence": independence_score,
            "evidence_completeness": completeness_score,
        },

        "contributions": contributions,

        "supporting_evidence": supporting_evidence,

        "conflicting_evidence": conflicting_evidence,

        "missing_evidence": missing_evidence,

        "reasoning": reasoning,

        "conflict_adjustment": round(
            conflict_adjustment,
            2,
        ),

        "fusion_maximum": 100.0,

        "fusion_version": (
            "architecture-h2.0-"
            "uncalibrated"
        ),

        "calibration_status": "uncalibrated",

        "human_verification_required": True,

        "is_pollution_confirmation": False,

        "assessment": (
            "Evidence Confidence is an ordinal index of how "
            "strongly the available evidence supports a potential "
            "aquatic-health anomaly. AI Belief describes how "
            "strongly the system trusts that assessment based on "
            "evidence quality, agreement, independence, and "
            "completeness. Neither value confirms pollution, "
            "toxicity, or causation."
        ),
    }