"""CLIP-based image evidence analysis for citizen reports.

Stage 6.2:
- Zero-shot CLIP image analysis
- Cautious aquatic anomaly indicators
- Water-scene check
- Deterministic fallback when vision is unavailable

Important:
CLIP outputs are relative, uncalibrated signals.
They are NOT pollution probabilities or confirmations.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, Optional

from PIL import Image

MODEL_NAME = "openai/clip-vit-base-patch32"

PROMPTS = {
    "fish_mortality": "a photo of dead fish floating on water",
    "water_discoloration": "green algae bloom on water",
    "foam_surface_material": "foam on a river",
    "clear_water": "clear clean water",
    "not_water_scene": "not a water scene",
}

_model = None
_processor = None
_result_cache: Dict[str, Dict[str, Any]] = {}


def _image_sha256(image_path: str) -> str:
    """Calculate SHA-256 for deterministic image caching."""
    sha256 = hashlib.sha256()

    with open(image_path, "rb") as image_file:
        for chunk in iter(lambda: image_file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def _load_model():
    """Load CLIP once and keep it in memory."""
    global _model, _processor

    if _model is None or _processor is None:
        from transformers import CLIPModel, CLIPProcessor

        _processor = CLIPProcessor.from_pretrained(MODEL_NAME)
        _model = CLIPModel.from_pretrained(MODEL_NAME)

        _model.eval()

    return _model, _processor


def _validate_image(image_path: str) -> Dict[str, Any]:
    """Perform lightweight image validation."""
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    with Image.open(path) as image:
        width, height = image.size
        image_format = image.format

    return {
        "width": width,
        "height": height,
        "format": image_format,
        "resolution_ok": width >= 224 and height >= 224,
    }


def _signal_band(value: float) -> str:
    """Convert an uncalibrated signal into a UI-friendly band."""
    if value < 0.40:
        return "weak"
    if value < 0.70:
        return "moderate"
    return "strong"


def analyze_image(image_path: str) -> Dict[str, Any]:
    """Analyze an image using zero-shot CLIP.

    Returns cautious visual evidence signals.
    It does not determine pollution, toxicity, or cause.
    """

    image_info = _validate_image(image_path)
    image_hash = _image_sha256(image_path)

    if image_hash in _result_cache:
        cached = dict(_result_cache[image_hash])
        cached["cache_hit"] = True
        return cached

    try:
        import torch

        model, processor = _load_model()

        with Image.open(image_path) as image:
            image = image.convert("RGB")

        prompt_names = list(PROMPTS.keys())
        prompt_texts = list(PROMPTS.values())

        inputs = processor(
            text=prompt_texts,
            images=image,
            return_tensors="pt",
            padding=True,
        )

        with torch.no_grad():
            outputs = model(**inputs)

        probabilities = outputs.logits_per_image.softmax(dim=1)[0]

        signals = {}

        for index, prompt_name in enumerate(prompt_names):
            value = float(probabilities[index].item())

            signals[prompt_name] = {
                "signal": round(value, 4),
                "band": _signal_band(value),
                "prompt": PROMPTS[prompt_name],
            }

        result = {
            "vision_analyzed": True,
            "model": MODEL_NAME,
            "image_sha256": image_hash,
            "image_quality": image_info,
            "water_scene_signal": signals["not_water_scene"],
            "indicators": {
                "fish_mortality": signals["fish_mortality"],
                "water_discoloration": signals["water_discoloration"],
                "foam_surface_material": signals["foam_surface_material"],
            },
            "clear_water_signal": signals["clear_water"],
            "assessment": (
                "Possible visual aquatic anomaly indicators detected. "
                "These are uncalibrated visual evidence signals and "
                "do not confirm pollution or toxicity."
            ),
            "calibration_status": "uncalibrated",
            "cache_hit": False,
        }

    except Exception as exc:
        result = {
            "vision_analyzed": False,
            "model": MODEL_NAME,
            "image_sha256": image_hash,
            "image_quality": image_info,
            "water_scene_signal": None,
            "indicators": {},
            "clear_water_signal": None,
            "assessment": (
                "Vision analysis unavailable. "
                "Photo evidence is missing from the AI assessment."
            ),
            "calibration_status": "uncalibrated",
            "cache_hit": False,
            "fallback": True,
            "error": str(exc),
        }

    _result_cache[image_hash] = result

    return result