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

def get_standard_driver_entry_fee(event: dict | None = None) -> float:
    if not event:
        return 0.0

    pricing = event.get("pricing", {})
    return float(pricing.get("standard_driver_entry_fee", 0.0) or 0.0)


def calculate_driver_amount_due(
    standard_fee: float,
    discount_amount: float,
) -> float:
    due = float(standard_fee or 0.0) - float(discount_amount or 0.0)
    return max(due, 0.0)


def calculate_payment_status(
    amount_due: float,
    amount_paid: float,
) -> str:
    amount_due = float(amount_due or 0.0)
    amount_paid = float(amount_paid or 0.0)

    if amount_due <= 0:
        return "comped"

    if amount_paid <= 0:
        return "pending"

    if amount_paid < amount_due:
        return "part_paid"

    return "paid"


def calculate_team_payment_summary(entry: dict[str, Any]) -> dict[str, float | str]:
    driver_1_standard_fee = float(entry.get("driver_1_standard_fee", 0.0) or 0.0)
    driver_2_standard_fee = float(entry.get("driver_2_standard_fee", 0.0) or 0.0)

    driver_1_discount_amount = float(entry.get("driver_1_discount_amount", 0.0) or 0.0)
    driver_2_discount_amount = float(entry.get("driver_2_discount_amount", 0.0) or 0.0)

    driver_1_amount_due = calculate_driver_amount_due(
        driver_1_standard_fee,
        driver_1_discount_amount,
    )
    driver_2_amount_due = calculate_driver_amount_due(
        driver_2_standard_fee,
        driver_2_discount_amount,
    )

    driver_1_amount_paid = float(entry.get("driver_1_amount_paid", 0.0) or 0.0)
    driver_2_amount_paid = float(entry.get("driver_2_amount_paid", 0.0) or 0.0)

    team_standard_fee = driver_1_standard_fee + driver_2_standard_fee
    team_discount_amount = driver_1_discount_amount + driver_2_discount_amount
    team_amount_due = driver_1_amount_due + driver_2_amount_due
    team_amount_paid = driver_1_amount_paid + driver_2_amount_paid

    if team_amount_due <= 0:
        team_payment_status = "comped"
    elif team_amount_paid <= 0:
        team_payment_status = "pending"
    elif team_amount_paid < team_amount_due:
        team_payment_status = "part_paid"
    else:
        team_payment_status = "paid"

    return {
        "driver_1_amount_due": driver_1_amount_due,
        "driver_2_amount_due": driver_2_amount_due,
        "driver_1_payment_status": calculate_payment_status(
            driver_1_amount_due,
            driver_1_amount_paid,
        ),
        "driver_2_payment_status": calculate_payment_status(
            driver_2_amount_due,
            driver_2_amount_paid,
        ),
        "team_standard_fee": team_standard_fee,
        "team_discount_amount": team_discount_amount,
        "team_amount_due": team_amount_due,
        "team_amount_paid": team_amount_paid,
        "team_payment_status": team_payment_status,
    }


def apply_team_payment_summary(entry: dict[str, Any]) -> dict[str, Any]:
    entry.update(calculate_team_payment_summary(entry))
    return entry

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
    reserve_status: str,
    grid_status: str,
    notes: str,
    event: dict | None = None,
    driver_1_email: str = "",
    driver_1_phone: str = "",
    driver_1_contact_status: str = "not_contacted",
    driver_1_discount_amount: float = 0.0,
    driver_1_discount_reason: str = "none",
    driver_1_amount_paid: float = 0.0,
    driver_1_payment_method: str = "",
    driver_1_payment_note: str = "",
    driver_2_email: str = "",
    driver_2_phone: str = "",
    driver_2_contact_status: str = "not_contacted",
    driver_2_discount_amount: float = 0.0,
    driver_2_discount_reason: str = "none",
    driver_2_amount_paid: float = 0.0,
    driver_2_payment_method: str = "",
    driver_2_payment_note: str = "",
    primary_contact_driver: str = "driver_1",
    ready_status: str = "not_ready",
) -> str:
    entry_id = build_entry_id(team_name, entry_type)
    standard_fee = get_standard_driver_entry_fee(event)

    entry = {
        "entry_id": entry_id,
        "event_id": event_id,
        "entry_format": "team_2_driver",
        "team_name": team_name,
        "car_choice": car_choice,
        "backup_car_choice": backup_car_choice,
        "entry_type": entry_type,
        "reserve_status": reserve_status,
        "grid_status": grid_status,
        "primary_contact_driver": primary_contact_driver,
        "ready_status": ready_status,

        "driver_1_name": driver_1_name,
        "driver_1_attendance_status": driver_1_attendance_status,
        "driver_1_email": driver_1_email,
        "driver_1_phone": driver_1_phone,
        "driver_1_contact_status": driver_1_contact_status,
        "driver_1_standard_fee": standard_fee,
        "driver_1_discount_amount": float(driver_1_discount_amount or 0.0),
        "driver_1_discount_reason": driver_1_discount_reason,
        "driver_1_amount_paid": float(driver_1_amount_paid or 0.0),
        "driver_1_payment_method": driver_1_payment_method,
        "driver_1_payment_note": driver_1_payment_note,

        "driver_2_name": driver_2_name,
        "driver_2_attendance_status": driver_2_attendance_status,
        "driver_2_email": driver_2_email,
        "driver_2_phone": driver_2_phone,
        "driver_2_contact_status": driver_2_contact_status,
        "driver_2_standard_fee": standard_fee,
        "driver_2_discount_amount": float(driver_2_discount_amount or 0.0),
        "driver_2_discount_reason": driver_2_discount_reason,
        "driver_2_amount_paid": float(driver_2_amount_paid or 0.0),
        "driver_2_payment_method": driver_2_payment_method,
        "driver_2_payment_note": driver_2_payment_note,

        "notes": notes,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    entry = apply_team_payment_summary(entry)

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
    event: dict | None = None,
) -> str:
    registration_route = registration.get("registration_route", "team_2_driver")

    if registration_route not in ["team_2_driver", ""]:
        raise ValueError(
            "Only complete two-driver team registrations can create Event Entries directly."
        )
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
    path = f"{event_entries_folder(event_id)}/{entry_id}.json"

    existing_entries = list_event_entries(event_id)
    existing_entry_ids = {
        entry.get("entry_id", "")
        for entry in existing_entries
    }

    existing_source_registration_ids = {
        entry.get("source_registration_id", "")
        for entry in existing_entries
    }

    source_registration_id = registration.get("submission_id", "")

    if entry_id in existing_entry_ids:
        raise ValueError(
            f"An Event Entry already exists for this team: {team_name}."
        )

    if source_registration_id and source_registration_id in existing_source_registration_ids:
        raise ValueError(
            "An Event Entry has already been created from this registration."
        )

    standard_fee = get_standard_driver_entry_fee(event)

    entry = {
        "entry_id": entry_id,
        "event_id": event_id,
        "entry_format": "team_2_driver",
        "source_registration_id": source_registration_id,
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
                "primary_contact_driver": "driver_1",
        "ready_status": "not_ready",

        "driver_1_email": registration.get("driver_1_email", ""),
        "driver_1_phone": registration.get("driver_1_phone", ""),
        "driver_1_contact_status": "not_contacted",
        "driver_1_standard_fee": standard_fee,
        "driver_1_discount_amount": 0.0,
        "driver_1_discount_reason": "none",
        "driver_1_amount_paid": 0.0,
        "driver_1_payment_method": "",
        "driver_1_payment_note": "",

        "driver_2_email": registration.get("driver_2_email", ""),
        "driver_2_phone": registration.get("driver_2_phone", ""),
        "driver_2_contact_status": "not_contacted",
        "driver_2_standard_fee": standard_fee,
        "driver_2_discount_amount": 0.0,
        "driver_2_discount_reason": "none",
        "driver_2_amount_paid": 0.0,
        "driver_2_payment_method": "",
        "driver_2_payment_note": "",
    }

    entry = apply_team_payment_summary(entry)

    return save_event_entry(event_id, entry) 