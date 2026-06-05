from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
import uuid

from src.data_loader import save_json, load_json


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "submission"


def build_submission_id(team_name: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{slugify(team_name)}_{uuid.uuid4().hex[:8]}"


def create_pending_spa_entry(payload: dict) -> Path:
    submission_id = build_submission_id(payload.get("team_name", "team"))
    payload = {
        "submission_id": submission_id,
        "submitted_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
        **payload,
    }
    return save_json(
        f"data/registrations/pending/spa_3h_endurance/{submission_id}.json",
        payload,
    )


def load_confirmed_spa_entries() -> list[dict]:
    return load_json("data/events/spa_3h_endurance/confirmed_entries.json", default=[])
