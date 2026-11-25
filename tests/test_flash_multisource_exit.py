# packages/intersect/tests/test_flash_multisource_exit.py
"""P2a EXIT — capture -> flash -> ONE envelope carries the experience; skills unchanged."""
from __future__ import annotations
import pytest
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_capture_then_flash_one_envelope(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("DB_PATH", db_path)
    import dabidabi as _db_mod
    monkeypatch.setattr(_db_mod, "DB_PATH", db_path)
    if _db_mod._db_connection is not None:
        await _db_mod._db_connection.close()
        _db_mod._db_connection = None
    from dabidabi import init_db, get_db
    await init_db()
    db = await get_db()
    await db.execute("INSERT INTO missions (id,title,status,workflow) VALUES (1,'t','active','')")
    await db.commit()
    from kara_kutu.workflow_exemplars import _ensure_table
    await _ensure_table()
    # kara_kutu.capture -> capture_exemplar -> _tool_recipe_for_task SELECTs
    # audit_log + task_traces (NOT created by init_db) — ensure them or capture raises.
    from kara_kutu.audit import _ensure_table as _ensure_audit
    from kara_kutu.tracing import _ensure_table as _ensure_trace
    await _ensure_audit(db)
    await _ensure_trace(db)

    # 1) capture a [7.4a] success
    from kara_kutu import capture, i2p_step_key
    await capture(i2p_step_key("", "7.4a", "coder"), task_id=3,
                  result="EXIT-MARKER output", quality=0.9, mission_id=1)

    # 2) flash with an empty capability path → envelope carries just the experience.
    #    `import intersect.flash as _flash` binds the FUNCTION (intersect/__init__.py
    #    re-export), so import the function directly. yalayut is imported INSIDE
    #    flash() → patch by string (also avoids the embedding cold-load).
    from intersect.flash import flash
    from unittest.mock import patch
    task = {"id": 1, "title": "[7.4a] db_schema_author", "agent_type": "coder",
            "mission_id": 1, "context": "{}"}
    with patch("yalayut.query", AsyncMock(return_value=[])):
        out = await flash(task)
    exp = [e for e in out["skills"] if e.get("source") == "experience"]
    assert len(exp) == 1 and exp[0]["payload"]["text"] == "EXIT-MARKER output"
