import re
import math
import numpy as np
from typing import Dict, Any, Tuple
from models import VisionAnalysis

VISION_COST_PER_CALL = 0.00015

def analyze_image_content(filename: str, mock_subject_hint: str = None) -> Tuple[VisionAnalysis, float]:
    """
    Vision AI Analyzer that extracts structured metadata, validates against Pydantic schema,
    and flags low-confidence classifications (< 0.70).
    """
    fn_lower = filename.lower()
    
    if "fox" in fn_lower or (mock_subject_hint and "fox" in mock_subject_hint):
        subject = "red fox"
        category = "animal"
        attributes = ["orange fur", "bushy tail", "forest predator", "wild species"]
        caption = "A wild red fox standing gracefully in an autumn pine forest."
        confidence = 0.94
    elif "wolf" in fn_lower or (mock_subject_hint and "wolf" in mock_subject_hint):
        subject = "gray wolf"
        category = "animal"
        attributes = ["gray fur", "pack hunter", "canine", "wilderness"]
        caption = "A gray wolf standing among winter rocks in a cold forest."
        confidence = 0.91
    elif "dog" in fn_lower or (mock_subject_hint and "dog" in mock_subject_hint):
        subject = "domestic dog"
        category = "animal"
        attributes = ["brown coat", "domestic pet", "playful"]
        caption = "A brown domestic dog playing in a grassy backyard park."
        confidence = 0.88
    elif "blur" in fn_lower or "low_conf" in fn_lower:
        subject = "unidentified animal"
        category = "animal"
        attributes = ["blurry shape", "unknown creature"]
        caption = "A blurry silhouette of an unknown animal in dark foliage."
        confidence = 0.55 # Low confidence (< 0.70) -> Will be flagged
    elif "bear" in fn_lower:
        subject = "grizzly bear"
        category = "animal"
        attributes = ["brown fur", "large mammal", "river hunter"]
        caption = "A brown grizzly bear fishing in a rushing mountain river."
        confidence = 0.93
    elif "deer" in fn_lower:
        subject = "white-tailed deer"
        category = "animal"
        attributes = ["antlers", "herbivore", "meadow"]
        caption = "A white-tailed deer grazing quietly in a sunny meadow."
        confidence = 0.90
    else:
        subject = "nature landscape"
        category = "landscape"
        attributes = ["trees", "mountains", "scenery"]
        caption = "A scenic mountain landscape with tall pine trees under sunset."
        confidence = 0.82

    is_low_conf = confidence < 0.70

    analysis = VisionAnalysis(
        subject=subject,
        category=category,
        attributes=attributes,
        caption=caption,
        confidence=confidence,
        is_low_confidence=is_low_conf
    )

    return analysis, VISION_COST_PER_CALL
