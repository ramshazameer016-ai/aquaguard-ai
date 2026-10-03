"""Text-based evidence analysis for citizen reports."""

import re
from typing import Dict, List


INDICATOR_PATTERNS = {
    "fish_mortality": [
        r"\bdead fish\b",
        r"\bdead fishes\b",
        r"\bdying fish\b",
        r"\bfish mortality\b",
        r"\bfish deaths?\b",
        r"\bfish floating\b",
        r"\bfish are dead\b",
    ],
    "foam_surface_material": [
        r"\bfoam\b",
        r"\bfoamy\b",
        r"\bscum\b",
        r"\bsurface material\b",
        r"\bbubbles?\b",
    ],
    "water_discoloration": [
    r"\bgreen water\b",
    r"\bgreenish water\b",
    r"\bgreenish discoloration\b",
    r"\bgreen discoloration\b",
    r"\bdiscoloration of the water\b",
    r"\bdiscolouration of the water\b",
    r"\bdiscolored water\b",
    r"\bdiscoloured water\b",
    r"\bunusual water color\b",
    r"\bunusual water colour\b",
    r"\bstrange water color\b",
    r"\bstrange water colour\b",
    r"\bwater changed color\b",
    r"\bwater changed colour\b",
    r"\bbrown water\b",
    r"\bred water\b",
    r"\bblack water\b",
    r"\bcloudy water\b",
],
    "unusual_odor": [
        r"\bunusual odor\b",
        r"\bunusual odour\b",
        r"\bstrange odor\b",
        r"\bstrange odour\b",
        r"\bbad smell\b",
        r"\bstrong smell\b",
        r"\bunusual smell\b",
        r"\bfoul smell\b",
        r"\bfoul odor\b",
        r"\bfoul odour\b",
    ],
    "wildlife_activity": [
        r"\bdead bird\b",
        r"\bdead birds\b",
        r"\bdead wildlife\b",
        r"\bwildlife mortality\b",
        r"\bwildlife deaths?\b",
        r"\banimals? affected\b",
        r"\bbirds? affected\b",
    ],
}


NEGATION_PATTERNS = [
    r"\bno\b",
    r"\bnot\b",
    r"\bdid not\b",
    r"\bdidn't\b",
    r"\bdo not\b",
    r"\bdon't\b",
    r"\bwithout\b",
    r"\bnever\b",
]


def normalize_text(text: str) -> str:
    """Normalize text for indicator matching."""

    text = text.lower().strip()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


def is_negated(
    text: str,
    match_start: int,
) -> bool:
    """
    Check whether an indicator appears to be negated.

    The MVP uses a small word window immediately before
    the matched phrase.
    """

    prefix = text[:match_start]

    words = prefix.split()

    if not words:
        return False

    window = " ".join(
        words[-5:]
    )

    for pattern in NEGATION_PATTERNS:
        if re.search(
            pattern,
            window,
        ):
            return True

    return False


def analyze_text(
    text: str,
) -> Dict:
    """
    Analyze citizen report text.

    Returns cautious indicator signals rather than
    a pollution determination.
    """

    normalized = normalize_text(text)

    indicators: List[Dict] = []

    for indicator_type, patterns in INDICATOR_PATTERNS.items():

        positive_matches = []
        negated_matches = []

        for pattern in patterns:
            for match in re.finditer(
                pattern,
                normalized,
            ):
                if is_negated(
                    normalized,
                    match.start(),
                ):
                    negated_matches.append(
                        match.group(0)
                    )
                else:
                    positive_matches.append(
                        match.group(0)
                    )

        if positive_matches:
            indicators.append(
                {
                    "indicator": indicator_type,
                    "signal": round(
                        min(
                            1.0,
                            0.5
                            + (
                                0.15
                                * len(
                                    positive_matches
                                )
                            ),
                        ),
                        2,
                    ),
                    "matches": positive_matches,
                    "negated_matches": negated_matches,
                }
            )

    if indicators:
        overall_signal = min(
            1.0,
            0.25
            + (
                0.20
                * len(indicators)
            ),
        )
    else:
        overall_signal = 0.0

    return {
        "text_analyzed": True,
        "overall_signal": round(
            overall_signal,
            2,
        ),
        "indicator_count": len(
            indicators
        ),
        "indicators": indicators,
        "assessment": (
            "Possible aquatic anomaly indicators "
            "present in report text."
            if indicators
            else
            "No predefined aquatic anomaly "
            "indicators detected in report text."
        ),
        "calibration_status": "uncalibrated",
    }