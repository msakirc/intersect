# packages/intersect/tests/test_experience_source.py
"""P2a — Experience -> envelope items, inject/experience, discriminator set."""
from __future__ import annotations


def _fake_exp(text="prior good output", quality=0.9, task_id=7):
    from kara_kutu import Experience
    return Experience(kind="step_success", key="k", text=text,
                      tool_recipe=[{"tool": "write_file", "args": {"path": "x"}}],
                      quality=quality, task_id=task_id)


def test_maps_experience_to_inject_item():
    from intersect.experience_source import experience_envelope_items
    items = experience_envelope_items([_fake_exp()], step_id="7.4a")
    assert len(items) == 1
    it = items[0]
    assert it["exposure_class"] == "inject"
    assert it["applies_to"] == "execution"
    assert it["render"] == "experience"
    assert it["source"] == "experience"
    assert it["payload"]["text"] == "prior good output"
    assert it["payload"]["step_id"] == "7.4a"
    assert it["payload"]["tool_recipe"][0]["tool"] == "write_file"
    assert it["confidence"] == 0.9
    # sentinel id (never a real yalayut artifact id)
    assert it["artifact_id"] < 0


def test_empty_in_empty_out():
    from intersect.experience_source import experience_envelope_items
    assert experience_envelope_items([], step_id="7.4a") == []
