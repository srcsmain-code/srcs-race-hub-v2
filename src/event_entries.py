from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from src.github_writer import (
    commit_json_to_github,
    list_github_directory,
    read_json_from_github,
)


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = value.strip("_")
    return value or "entry"


def event_entries_folder(event_id: str) -> str:
    return f"data/event_entries/{event_id}"


def build_entry_id(name: str, entry_type: str = "regular") -> str:
    base = slugify(name)
    if entry_type == "reserve":
        return f"reserve_{base}"
    return base


def list_event_entries(event_id: str) -> list[dict[str, Any]]:
    folder = event_entries_folder(event_id)

    try:
        files = list_github_directory(folder)
    except Exception:
        return []

    entries: list[dict[str, Any]] = []

    for file_info in files:
        if file_info.get("type") != "file":
            continue

        name = file_info.get("name", "")
        if not name.endswith(".json"):
            continue

        path = file_info.get("path", "")
        if not path:
            continue

        payload = read_json_from_github(path)
        payload["_github_path"] = path
        entries.append(payload)

    entries.sort(
        key=lambda item: (
            item.get("entry_type", ""),
            item.get("team_name", ""),
            item.get("driver_name", ""),
            item.get("driver_1_name", ""),
        )
    )

    return entries


def save_event_entry(event_id: str, entry: dict[str, Any]) -> str:
    entry_id = entry.get("entry_id") or build_entry_id(
        entry.get("team_name") or entry.get("driver_name") or "entry",
        entry.get("entry_type", "regular"),
    )

    entry["entry_id"] = entry_id
    entry["event_id"] = event_id
    entry["updated_at_utc"] = datetime.now(timezone.utc).isoformat()

    path = f"{event_entries_folder(event_id)}/{entry_id}.json"

    commit_json_to_github(
        path=path,
        payload=entry,
        message=f"Save event entry: {entry.get('team_name') or entry.get('driver_name') or entry_id}",
    )

    return path


def create_single_driver_event_entry(
    event_id: str,
    driver_name: str,
    team_name: str,
    entry_type: str,
    attendance_status: str,
    payment_status: str,
    reserve_status: str,
    grid_status: str,
    notes: str,
) -> str:
    entry_id = build_entry_id(driver_name, entry_type)

    entry = {
        "entry_id": entry_id,
        "event_id": event_id,
        "entry_format": "single_driver",
        "driver_name": driver_name,
        "team_name": team_name,
        "entry_type": entry_type,
        "attendance_status": attendance_status,
        "payment_status": payment_status,
        "reserve_status": reserve_status,
        "grid_status": grid_status,
        "notes": notes,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    return save_event_entry(event_id, entry)


def create_team_2_driver_event_entry(
    event_id: str,
    team_name: str,
    car_choice: str,
    backup_car_choice: str,
    driver_1_name: str,
    driver_1_attendance_status: str,
    driver_2_name: str,
    driver_2_attendance_status: str,
    entry_type: str,
    payment_status: str,
    reserve_status: str,
    grid_status: str,
    notes: str,
) -> str:
    entry_id = build_entry_id(team_name, entry_type)

    entry = {
        "entry_id": entry_id,
        "event_id": event_id,
        "entry_format": "team_2_driver",
        "team_name": team_name,
        "car_choice": car_choice,
        "backup_car_choice": backup_car_choice,
        "driver_1_name": driver_1_name,
        "driver_1_attendance_status": driver_1_attendance_status,
        "driver_2_name": driver_2_name,
        "driver_2_attendance_status": driver_2_attendance_status,
        "entry_type": entry_type,
        "payment_status": payment_status,
        "reserve_status": reserve_status,
        "grid_status": grid_status,
        "notes": notes,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    return save_event_entry(event_id, entry)


def update_event_entry(
    event_id: str,
    existing_entry: dict[str, Any],
    updates: dict[str, Any],
) -> str:
    entry = dict(existing_entry)
    entry.pop("_github_path", None)
    entry.update(updates)

    return save_event_entry(event_id, entry)

def create_team_2_driver_entry_from_registration(
    event_id: str,
    registration: dict[str, Any],
) -> str:
    team_name = registration.get("team_name", "")
    car_choice = registration.get("car_choice", "")
    backup_car_choice = registration.get("backup_car_choice", "")
    driver_1_name = registration.get("driver_1_name", "")
    driver_2_name = registration.get("driver_2_name", "")
    notes = registration.get("notes", "")

    if not team_name:
        raise ValueError("Registration is missing team_name.")

    if not driver_1_name or not driver_2_name:
        raise ValueError("Registration is missing one or both driver names.")

    entry_id = build_entry_id(team_name, "regular")

    entry = {
        "entry_id": entry_id,
        "event_id": event_id,
        "entry_format": "team_2_driver",
        "source_registration_id": registration.get("submission_id", ""),
        "source_registration_path": registration.get("_github_path", ""),
        "team_name": team_name,
        "car_choice": car_choice,
        "backup_car_choice": backup_car_choice,
        "driver_1_name": driver_1_name,
        "driver_1_attendance_status": "expected",
        "driver_2_name": driver_2_name,
        "driver_2_attendance_status": "expected",
        "entry_type": "regular",
        "payment_status": "pending",
        "reserve_status": "not_applicable",
        "grid_status": "not_assigned",
        "notes": notes,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    return save_event_entry(event_id, entry)    