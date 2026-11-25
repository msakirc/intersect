# packages/intersect/tests/test_flash_experience_append.py
"""P2a — flash appends recalled experience items; capability items untouched."""
from __future__ import annotations
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_flash_appends_experience_after_caps():
    # `import intersect.flash as _flash` binds _flash to the re-exported flash
    # FUNCTION (intersect/__init__.py:13 shadows the submodule), so `_flash.flash`
    # would AttributeError. Import the function directly (patches are by-string).
    from intersect.flash import flash

    from kara_kutu import Experience, i2p_step_key
    exp = Experience(kind="step_success", key=i2p_step_key("", "7.4a", "coder"),
                     text="MARKER prior output", tool_recipe=[], quality=0.9, task_id=3)

    async def _fake_recall(key, *, limit=3):
        return [exp]

    task = {"id": 1, "title": "[7.4a] db_schema_author", "agent_type": "coder",
            "mission_id": 0, "context": "{}"}

    # yalayut is imported INSIDE flash() → patch by string, not _flash.yalayut.
    with patch("yalayut.query", AsyncMock(return_value=[])), patch("kara_kutu.recall", _fake_recall):
        out = await flash(task)

    env = out["skills"]
    exp_items = [e for e in env if e.get("source") == "experience"]
    assert len(exp_items) == 1
    assert exp_items[0]["payload"]["text"] == "MARKER prior output"


@pytest.mark.asyncio
async def test_flash_no_experience_leaves_capability_envelope_byte_identical():
    """REGRESSION GUARD — no exemplars → envelope identical to the pre-P2a path."""
    from intersect.flash import flash

    async def _empty_recall(key, *, limit=3):
        return []

    task = {"id": 1, "title": "[7.4a] db_schema_author", "agent_type": "coder",
            "mission_id": 0, "context": "{}"}
    with patch("yalayut.query", AsyncMock(return_value=[])), patch("kara_kutu.recall", _empty_recall):
        out = await flash(task)
    # capability path empty + no experience → envelope is exactly [] (unchanged)
    assert out["skills"] == []
    assert all(e.get("source") != "experience" for e in out["skills"])
