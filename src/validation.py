from __future__ import annotations

import re

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(email.strip()))


def required_fields_present(payload: dict, fields: list[str]) -> tuple[bool, list[str]]:
    missing = [field for field in fields if not str(payload.get(field, "")).strip()]
    return len(missing) == 0, missing
