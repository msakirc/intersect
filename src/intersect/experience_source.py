# packages/intersect/src/intersect/experience_source.py
"""Experience adapter for the flash multi-source gate (P2a).

Auto-captured, pre-vetted per-step experience does NOT go through
scoring/exposure.classify/binding/render_variant (it would tier-3 quarantine
and collide on _slot_key). Instead it is converted to envelope items with a
hand-set inject exposure + an ``experience`` render + a ``source`` discriminator,
and APPENDED to the envelope after budget.apply_caps so the capability
(yalayut skill) envelope stays byte-identical.
"""
from __future__ import annotations


def experience_envelope_items(experiences: list, *, step_id: str) -> list[dict]:
    """Map recalled Experience objects to inject-class envelope items."""
    items: list[dict] = []
    for i, exp in enumerate(experiences or []):
        items.append({
            "artifact_id": -(i + 1),                 # sentinel — not a yalayut id
            "name": f"prior [{step_id}] output",
            "exposure_class": "inject",
            "applies_to": "execution",
            "render": "experience",
            "payload": {
                "kind": getattr(exp, "kind", "step_success"),
                "text": getattr(exp, "text", "") or "",
                "tool_recipe": list(getattr(exp, "tool_recipe", []) or []),
                "step_id": step_id,
            },
            "confidence": float(getattr(exp, "quality", 0.0) or 0.0),
            "source": "experience",
        })
    return items
