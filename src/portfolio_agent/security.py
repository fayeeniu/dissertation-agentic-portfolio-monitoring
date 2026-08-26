from __future__ import annotations

import json
import re
from typing import Any

from .enums import DataClassification

_INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"system\s+prompt", re.IGNORECASE),
    re.compile(r"developer\s+message", re.IGNORECASE),
    re.compile(r"reveal\s+(the\s+)?(secret|credential|password)", re.IGNORECASE),
    re.compile(r"do\s+not\s+follow\s+(the\s+)?instructions", re.IGNORECASE),
)


def contains_prompt_injection(value: Any) -> bool:
    serialized = json.dumps(value, sort_keys=True, default=str)
    return any(pattern.search(serialized) for pattern in _INJECTION_PATTERNS)


def assert_external_model_safe(
    *, classification: DataClassification, content: dict[str, Any], is_untrusted: bool
) -> None:
    if classification not in {DataClassification.PUBLIC, DataClassification.SYNTHETIC}:
        raise PermissionError(
            "Restricted or internal evidence cannot be sent to an external model."
        )
    if is_untrusted or contains_prompt_injection(content):
        raise PermissionError("Untrusted instruction-like evidence cannot be sent to a model.")
