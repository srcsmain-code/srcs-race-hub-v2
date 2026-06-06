from __future__ import annotations

import json
from pathlib import Path
from typing import Any


EVENTS_DIR = Path("data/events")


def load_event(event_id: str) -> dict[str, Any]:
    path = EVENTS_DIR / f"{event_id}.json"

    if not path.exists():
        raise FileNotFoundError(f"Event config not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def list_events() -> list[dict[str, Any]]:
    if not EVENTS_DIR.exists():
        return []

    events: list[dict[str, Any]] = []

    for path in sorted(EVENTS_DIR.glob("*.json")):
        with path.open("r", encoding="utf-8") as file:
            events.append(json.load(file))

    return events


def list_public_events() -> list[dict[str, Any]]:
    return [
        event for event in list_events()
        if event.get("public_visible", True)
    ]


def get_event_label(event: dict[str, Any]) -> str:
    return f"{event.get('event_short_name', event.get('event_name', 'Unnamed event'))} — {event.get('category', '')}"